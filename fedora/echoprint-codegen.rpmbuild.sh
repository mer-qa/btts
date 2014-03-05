#!/bin/sh -e

cd "$(dirname "$0")"

mkdir -p rpmbuild/{BUILD{,ROOT},{,S}RPMS}

spectool --get-files --directory echoprint-codegen \
	echoprint-codegen/echoprint-codegen.spec

sudo yum-builddep echoprint-codegen/echoprint-codegen.spec

rpmbuild --define "_topdir $(readlink -f rpmbuild)" \
	--define "_sourcedir $(readlink -f echoprint-codegen)" \
	--define "_specdir $(readlink -f echoprint-codegen)" \
	-bb echoprint-codegen/echoprint-codegen.spec

./createrepo.sh --as-needed
