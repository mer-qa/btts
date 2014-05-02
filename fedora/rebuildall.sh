#!/bin/bash -e

cd $(dirname "$0")

./clean.sh
./pulseaudio.rpmbuild.sh
./echoprint-codegen.rpmbuild.sh
./btts.rpmbuild.sh
./createrepo.sh
