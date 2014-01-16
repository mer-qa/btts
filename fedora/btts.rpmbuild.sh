#!/bin/sh -e

cd "$(dirname "$0")"

mkdir -p rpmbuild/{BUILD{,ROOT},{,S}RPMS}

tar -cz -f btts/btts-0.1.0.tar.gz -C .. . \
	--exclude ./fedora \
	--exclude ./.git \
	--exclude '.[^/]*' \
	--transform 's,^\.,btts-0.1.0,'

sudo yum-builddep btts/btts.spec

rpmbuild --define "_topdir $(readlink -f rpmbuild)" \
	--define "_sourcedir $(readlink -f btts)" \
	--define "_specdir $(readlink -f btts)" \
	-bb btts/btts.spec
