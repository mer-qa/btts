#!/bin/bash -e

cd $(dirname "$0")

./clean.sh
./bluez.rpmbuild.sh
./ofono.rpmbuild.sh
./btts.rpmbuild.sh
./createrepo.sh
