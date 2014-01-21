#!/bin/bash

REPO_URL="${REPO_URL:-http://download.fedoraproject.org/pub/fedora/linux/releases/20/Fedora/x86_64/os/}"

VIRT_DOMAIN="btts"
DEFAULT_DISK_SIZE=5 # [GB]
KS_FILE="kickstart.ks"

usage()
{
    RANDOM_MAC="$(gen_mac)"

    cat <<END
Usage: $(basename "$0") <btdevs> <diskopts> [<MAC> [<network>]]

Installs a libvirt-managed virtual machine running BTTS services.

The domain will be named '${VIRT_DOMAIN}'. It is an error if a domain of that
name already exists.

Prerequisites

1. (Optional) Create a libvirt managed storage to be used by the VM.  You can
   simply skip this step and pass 'pool=default' as <diskopts> to automatically
   create a virtual volume in the default pool.

2. (Optional) Choose a MAC address to be used by the VM and configure the
   virtual network of your choice (see next step) to assign a fixed IP address
   for this MAC address by adding a //network/ip/dhcp/host XML node:

   <host mac="..." name="btts" ip="..." />

   A random local MAC addres: ${RANDOM_MAC}

   You can simply skip this step and omit the <MAC> argument. A random MAC/IP
   address will be assigned to the virtual machine. You can reach it with mDNS
   name "btts.local." if your host supports this.

3. (Optional) Create a virtual network to attach the VM to. You can simply skip
   this step and use the 'default' virtual network by omiting the <network>
   argument.

4. (Optional) Setup libvirt hook to add/remove port forwarding rules.

   See http://wiki.libvirt.org/page/Networking#Forwarding_Incoming_Connections


OPTIONS
    btdevs
        Comma separated list of <vendor-id>:<dev-id> pairs specifying
        Bluetooth controllers to make available in the virtual machine by
        attaching the respective host USB device.

    diskopts
        Storage configuration as accepted by virt-install's --disk option.
        Default 'size=${DEFAULT_DISK_SIZE}' is automatically appended if not
        included. See virt-install(1).

    MAC
        MAC address to configure the virtual machine's network interface. It is
        supposed the virtual network <network> is configured to assign a static
        IP address for this MAC address.

    network
        Name of a virtual network to attach the virtual machine to. Defaults to
        'default'.

ENVIRONMENT
    http_proxy [protocol://]<host>[:port]
        HTTP proxy settings is also forwarded to the VM.

        Hint: use a caching HTTP proxy (e.g. 'polipo') to speedup repeated
        execution.
        Hint: define also REPO_URL to prevent missing cache just because of
        redirects.

        Currently: ${http_proxy:-<unset>}

    REPO_URL
        Preferred Fedora installation tree location. Useful with http_proxy.

        Currently: ${REPO_URL}

EXAMPLES
    ~# $(basename "$0") dead:beef

        Make the Bluetooth controller identified by USB vendor:product pair
        'dead:beef' available to the virtual machine.
        Create a volume in the default libvirt storage pool as a storage.
        Use default size ${DEFAULT_DISK_SIZE}GB.
        Attach the virtual machine to the 'default' virtual network, using
        a random MAC address.

    ~# $(basename "$0") dead:beef pool=my_pool,size=10 \\
            ${RANDOM_MAC} my_vnet

        Make the Bluetooth controller identified by USB vendor:product pair
        'dead:beef' available to the virtual machine.
        Use an existing libvirt storage pool 'my_pool' to create new storage of
        the specified size '10' GB on.
        Attach the virtual machine to the 'my_vnet' virtual network, using
        '${RANDOM_MAC}' as its MAC address.

END
}

ok()
{
    [[ $? -eq 0 ]]
}

die()
{
    echo >&2 "Fatal: ${*}"
    exit 1
}

register_cleanup()
{
    CLEANUP="${CLEANUP} $*"
}

cleanup()
{
    echo "Cleanup..." >&2
    for step in ${CLEANUP}
    do
        ${step}
    done
}

encrypt_password()
{
    python -c "import crypt; print(crypt.crypt(\"$(cat)\", \
        crypt.mksalt(crypt.METHOD_SHA512)))"
}

virsh()
{
  command virsh -c qemu:///system "${@}"
}

gen_mac()
{
    echo "02$(od -t x1 -A n -v -N 5 /dev/urandom |tr \  :)"
}

devids_to_btops()
{
    for dev in ${1//,/ }
    do
        echo "--host-device 0x${dev%:*}:0x${dev#*:}"
    done
}

#
# Start

for arg in "${@}"
do
    if [[ ${arg} =~ ^(-h|--help)$ ]]
    then
        usage
        exit 1
    fi
done


[[ ${UID} -eq 0 ]] \
  || die "Must be run with UID 0 to workaround this bug:" \
          "https://www.mail-archive.com/debian-bugs-dist@lists.debian.org/msg1187154.html"

#
# Check dependencies

need_cmd()
{
    if ! which ${1?} &>/dev/null
    then
        die "Needed '${1}' tool not available on this system."
    fi
}

need_cmd mktemp
need_cmd timedatectl
need_cmd virsh
need_cmd virt-install

if ! encrypt_password <<<foo &>/dev/null
then
    die "Needed 'crypt' python module not available on this system." \
        "Required version >= 3.3."
fi

#
# Parse arguments

trap cleanup EXIT

BTDEVS="${1}"
[[ -n ${BTDEVS} ]] \
    || die "Missing argument."$'\n'"$(usage)"
[[ ${BTDEVS} =~ ^[0-9a-f]{4}:[0-9a-f]{4}(,[0-9a-f]{4}:[0-9a-f]{4})*$ ]]\
    || die "Invalid argument: '${BTDEVS}'."$'\n'"$(usage)"

DISKOPTS="${2}"
[[ -n ${DISKOPTS} ]] \
    || die "Missing argument."$'\n'"$(usage)"
if ! [[ ${DISKOPTS} =~ ,size=[0-9] ]]
then
    DISKOPTS="${DISKOPTS},size=${DEFAULT_DISK_SIZE}"
fi

MAC_ADDRESS="${3:-$(gen_mac)}"
[[ ${MAC_ADDRESS} =~ ^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$ ]] \
    || die "'${MAC_ADDRESS}': Not a valid MAC address"

NETWORK="${4:-default}"
NET_XML="$(virsh net-dumpxml "${NETWORK}")" \
  || die "'${NETWORK}': Unknown network (check with 'virsh net-list --all')"
HOST_IP="$(xmllint --xpath 'string(//network/ip/@address)' - <<<"${NET_XML}")" \
  || die "Failed to extract host IP from '${NETWORK}' network configuration."

#
# Detect existing domain

! virsh desc ${VIRT_DOMAIN} &>/dev/null \
    || die "Domain '${VIRT_DOMAIN}' already exists."

#
# Make tmp dir

TMP_DIR="$(mktemp -d --tmpdir btts-kickstart.XXXXXX)" \
    || die "Failed to create temporary directory"
cleanup_tmp_dir() { rm -rf "${TMP_DIR}"; }
register_cleanup cleanup_tmp_dir

#
# Generate kickstart file

echo "An admin account with login name 'btts' will be created in the VM..."
while [[ -z ${PASSWORD} ]]
do
    read -p "Enter new password: " -s PASSWORD; echo
    [[ -n ${PASSWORD} ]] \
        || { echo "Password cannot be empty."; continue; }
    read -p "Retype new password: " -s PASSWORD2; echo
    [[ ${PASSWORD} == ${PASSWORD2} ]] \
        || { echo "Passwords do not match."; continue; }
    PASSWORD="$(encrypt_password <<<"${PASSWORD}")"
    unset PASSWORD2
done

TIMEZONE="$(LANG=c timedatectl |awk '$1 == "Timezone:" { print $2 }')"

cat > ${TMP_DIR}/${KS_FILE} <<END
auth --enableshadow --passalgo=sha512
keyboard --vckeymap=us --xlayouts='us'
lang en_US.UTF-8
network  --bootproto=dhcp --ipv6=auto --activate --hostname=btts.localdomain
rootpw --lock
timezone ${TIMEZONE} --isUtc
user --groups=wheel --name=btts --password=${PASSWORD} --iscrypted --gecos="BlueTooth Test Suite"
bootloader --location=mbr --timeout=2
autopart --type=lvm
clearpart --none --initlabel
selinux --disabled

%packages
@core
#@minimal-environment # not understood by the installer
#@hardware-support
#@standard
@c-development
@rpm-development-tools

nss-mdns
git
vim-enhanced
%end

END

#
# Build up kernel commandline

BOOT_OPTIONS=""
BOOT_OPTIONS="${BOOT_OPTIONS} ks=file:///${KS_FILE}"
BOOT_OPTIONS="${BOOT_OPTIONS} console=ttyS0 headless cmdline"
BOOT_OPTIONS="${BOOT_OPTIONS} noselinux selinux=0"
#BOOT_OPTIONS="${BOOT_OPTIONS} sshd"

if [[ -n "${http_proxy}" ]]
then
    vm_http_proxy="${http_proxy}"
    vm_http_proxy="${vm_http_proxy/localhost/${HOST_IP}}"
    vm_http_proxy="${vm_http_proxy/127.0.0.1/${HOST_IP}}"
    BOOT_OPTIONS="${BOOT_OPTIONS} proxy=${vm_http_proxy}"
fi

#
# Start installation

if ! NPROC=$(nproc 2>/dev/null)
then
    echo "Warning: the 'nproc' utility is not available." \
        "Cannot determine number of CPUs available. Failing back to 1." >&2
    NPROC=1
fi

# Use half of the CPUs available
VCPUS=$(( (NPROC + 1) / 2 ))

virt-install \
    --connect qemu:///system \
    --name "${VIRT_DOMAIN}" \
    --description "BlueTooth Test Suite guest (Fedora)" \
    --ram 2048 \
    --vcpus ${VCPUS} \
    --disk "${DISKOPTS}" \
    --graphics none \
    --location "${REPO_URL}" \
    --initrd-inject ${TMP_DIR}/${KS_FILE} \
    --extra-args "${BOOT_OPTIONS}" \
    --network network=${NETWORK},mac=${MAC_ADDRESS} \
    --console pty \
    $(devids_to_btops ${BTDEVS}) \
    --autostart
