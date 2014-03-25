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

from __future__ import absolute_import, print_function, unicode_literals

import json
import logging
import math
import subprocess
import sys

log = logging.getLogger(__name__)

# TODO: error handling
class Echonest:
    _MIN_CODE_LEN = 10
    _THRESHOLD = 0.5 # Percent match required

    @staticmethod
    def match_code_string(wanted, tested):
        wanted_keys = set(wanted.split(" ")[0::2])
        tested_keys = tested.split(" ")[0::2]
        assert(len(wanted_keys) >= Echonest._MIN_CODE_LEN)
        assert(len(tested_keys) >= Echonest._MIN_CODE_LEN)
        match = list(filter(lambda x: x in wanted_keys, tested_keys))
        match_len = len(match)
        total_len = len(tested_keys)
        log.info('Matched %d%% samples (%d out of %d). Threshold %d%%.'
                 % ((match_len / total_len) * 100, match_len, total_len,
                     Echonest._THRESHOLD * 100))
        return match_len >= total_len * Echonest._THRESHOLD

    @staticmethod
    def codegen(file_path):
        cmd = ['echoprint-codegen', file_path, '0', '30']
        env = {'BTTS_ECHOPRINT_NOCOMPRESS': '1'}
        proc = subprocess.Popen(cmd, stdin=subprocess.DEVNULL,
                                stdout=subprocess.PIPE, env=env)
        out = proc.communicate()[0]
        #log.debug('json: [[[%s]]]' % (out.decode('utf-8')), file=sys.stderr)
        data = json.loads(out.decode('utf-8'))
        code = data[0]['code']

        duration = subprocess.check_output(['soxi', '-D', file_path])
        duration = math.floor(float(duration))

        return (duration, code)
