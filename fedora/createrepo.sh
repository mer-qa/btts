#!/bin/bash -e

repo_name="btts-local"
repo_dir="$(readlink -f $(dirname "$0"))/rpmbuild/RPMS"
repo_url="file://${repo_dir}"
repo_file="/etc/yum.repos.d/${repo_name}.repo"

createrepo "${repo_dir}"

repo_config="\
[${repo_name}]
name=${repo_name}
baseurl=${repo_url}
enabled=1\
"

if ! diff -q <(echo "${repo_config}") ${repo_file} &>/dev/null
then
	read -p "Add/update this repo to local yum configuration? [y/N] " YN
	if [[ ${YN} =~ ^[yY]$ ]]
	then
		sudo tee ${repo_file} <<<"${repo_config}"
	fi
fi