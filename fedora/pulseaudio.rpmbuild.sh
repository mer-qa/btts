#!/bin/sh -e

cd "$(dirname "$0")"

mkdir -p rpmbuild/{BUILD{,ROOT},{,S}RPMS}

spectool --get-files --directory pulseaudio pulseaudio/pulseaudio.spec

sudo yum-builddep pulseaudio/pulseaudio.spec

source0="$(spectool --list-files --source 0 pulseaudio/pulseaudio.spec \
		|sed -n 's/^Source0: \(pulseaudio-.*\.tar\.xz\)$/\1/p' |grep .)"
if ! [[ -f "pulseaudio/${source0}" ]]
then
	gitcommit="$(awk '$1 == "%global" && $2 == "gitcommit" { print $3 }' \
			pulseaudio/pulseaudio.spec |grep .)"
	mkdir -p rpmbuild/tmp-pulseaudio
	cd rpmbuild/tmp-pulseaudio
	[[ -d pulseaudio ]] || git clone git://anongit.freedesktop.org/pulseaudio/pulseaudio
	cd pulseaudio
	git fetch
	git reset --hard "${gitcommit}"
	#export GIT_DESCRIBE_FOR_BUILD="$(git describe --abbrev=6)"
	./autogen.sh
	make dist
	cp "${source0}" ../../../pulseaudio/
	cd ../../..
fi

rpmbuild --define "_topdir $(readlink -f rpmbuild)" \
	--define "_sourcedir $(readlink -f pulseaudio)" \
	--define "_specdir $(readlink -f pulseaudio)" \
	-bb pulseaudio/pulseaudio.spec

./createrepo.sh --as-needed
