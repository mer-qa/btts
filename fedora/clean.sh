#!/bin/bash -e

cd "$(dirname "$0")"

repo_created=$([[ -d rpmbuild/RPMS/repodata ]]; echo $?)

rm -rf rpmbuild/*

if [[ ${repo_created} -eq 0 ]]
then
	echo "Updating repository data..." >&2
	mkdir rpmbuild/RPMS
	./createrepo.sh
fi
