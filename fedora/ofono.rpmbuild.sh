#!/bin/sh -e

cd "$(dirname "$0")"

spectool --get-files --directory ofono ofono/ofono.spec

sudo yum-builddep ofono/ofono.spec

mkdir -p ofono.rpmbuild/{BUILD{,ROOT},{,S}RPMS}

rpmbuild --define "_topdir $(readlink -f ofono.rpmbuild)" \
	--define "_sourcedir $(readlink -f ofono)" \
	--define "_specdir $(readlink -f ofono)" \
	-bb ofono/ofono.spec
