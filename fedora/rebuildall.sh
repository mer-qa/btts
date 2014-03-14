#!/bin/bash -e

cd $(dirname "$0")

./clean.sh
./bluez.rpmbuild.sh
./pulseaudio.rpmbuild.sh
./ofono.rpmbuild.sh
./echoprint-codegen.rpmbuild.sh
./btts.rpmbuild.sh
./createrepo.sh
