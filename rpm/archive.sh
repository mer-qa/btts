#!/bin/bash -e

version="$(awk '( $1 == "Version:" ) { print $2 }' *.spec |grep .)"

odir="$(pwd)"
cd "$(git rev-parse --show-toplevel)"

git archive --prefix="btts-${version}/" -o "${odir}/btts-${version}.tar.gz" HEAD
