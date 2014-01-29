#!/bin/sh -e

cd "$(dirname "$0")"

mkdir -p rpmbuild/{BUILD{,ROOT},{,S}RPMS}

spectool --get-files --directory bluez bluez/bluez.spec

sudo yum-builddep bluez/bluez.spec

rpmbuild --define "_topdir $(readlink -f rpmbuild)" \
	--define "_sourcedir $(readlink -f bluez)" \
	--define "_specdir $(readlink -f bluez)" \
	-bb bluez/bluez.spec

./createrepo.sh --as-needed
