#!/bin/bash -e

cd $(dirname "$0")

sudo yum makecache --disablerepo='*' --enablerepo='btts-local'

if installed="$(repoquery --installed '*' |grep '\.btts[0-9]\+\.')"
then
	sudo rpm -e --nodeps ${installed}
fi

filter=(
	"bluez*"
	"pulseaudio"
	"pulseaudio-module-bluetooth"
	"pulseaudio-utils"
	"ofono*"
	"echoprint-codegen*"
	"btts*"
)

if available="$(repoquery --disablerepo='*' --enablerepo='btts-local' "${filter[@]}" |grep .)"
then
	sudo yum --nogpgcheck install ${available}
fi
