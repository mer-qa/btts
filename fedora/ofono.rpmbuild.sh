#!/bin/sh -e

cd "$(dirname "$0")"

mkdir -p rpmbuild/{BUILD{,ROOT},{,S}RPMS}

spectool --get-files --directory ofono ofono/ofono.spec

sudo yum-builddep ofono/ofono.spec

rpmbuild --define "_topdir $(readlink -f rpmbuild)" \
	--define "_sourcedir $(readlink -f ofono)" \
	--define "_specdir $(readlink -f ofono)" \
	-bb ofono/ofono.spec

./createrepo.sh --as-needed
