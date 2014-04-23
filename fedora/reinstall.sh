#!/bin/bash -e

cd $(dirname "$0")

sudo yum makecache --disablerepo='*' --enablerepo='btts-local'

if installed="$(repoquery --installed 'btts*' |grep .)"
then
	sudo rpm -e --nodeps ${installed}
fi

if available="$(repoquery --disablerepo='*' --enablerepo='btts-local' 'btts*' |grep .)"
then
	sudo yum --nogpgcheck install ${available}
fi
