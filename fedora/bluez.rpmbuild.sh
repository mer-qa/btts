#!/bin/sh -e

cd "$(dirname "$0")"

spectool --get-files --directory bluez bluez/bluez.spec

sudo yum-builddep bluez/bluez.spec

mkdir -p bluez.rpmbuild/{BUILD{,ROOT},{,S}RPMS}

rpmbuild --define "_topdir $(readlink -f bluez.rpmbuild)" \
	--define "_sourcedir $(readlink -f bluez)" \
	--define "_specdir $(readlink -f bluez)" \
	-bb bluez/bluez.spec
