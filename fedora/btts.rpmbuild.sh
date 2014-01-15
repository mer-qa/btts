#!/bin/sh -e

cd "$(dirname "$0")"

tar -cz -f ~/rpmbuild/SOURCES/btts-0.1.0.tar.gz -C .. . \
	--exclude ./fedora \
	--exclude ./.git \
	--exclude '.[^/]*' \
	--transform 's,^\.,btts-0.1.0,'

sudo yum-builddep btts/btts.spec

mkdir -p btts.rpmbuild/{BUILD{,ROOT},{,S}RPMS}

rpmbuild -bb btts/btts.spec
