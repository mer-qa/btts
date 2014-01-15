#!/bin/sh -e
#
# BTTS - BlueTooth Test Suite
#
# Copyright (C) 2014 Jolla Ltd.
# Contact: Martin Kampas <martin.kampas@jollamobile.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

cd "$(dirname "$0")"

spectool --get-files --directory bluez bluez/bluez.spec

sudo yum-builddep bluez/bluez.spec

mkdir -p bluez.rpmbuild/{BUILD{,ROOT},{,S}RPMS}

rpmbuild --define "_topdir $(readlink -f bluez.rpmbuild)" \
	--define "_sourcedir $(readlink -f bluez)" \
	--define "_specdir $(readlink -f bluez)" \
	-bb bluez/bluez.spec
