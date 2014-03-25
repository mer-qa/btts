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
import time

import btts

log = logging.getLogger(__name__)

_REASONABLE_TERMINATE_TIME = 5 # seconds

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

        return code

class Recorder:
    _REASONABLE_RECORD_WAIT_TIME = 30 # seconds; keep in sync with doc

    class Error(Exception):
        _dbus_error_name = 'org.merproject.btts.Recorder.Error'

    class NotReadyError(Error):
        def __init__(self):
            Recorder.Error.__init__(self, 'Not ready')

    class NotStartedError(Error):
        def __init__(self):
            Recorder.Error.__init__(self, 'Operation not started')

    class RecordTooShortError(Error):
        def __init__(self, actual_duration, expected_duration):
            Recorder.Error.__init__(self, ('The duration of the recorded '
                                           'audio (%dsecs) is shorter than '
                                           'expected (%dsecs)')
                                          % (actual_duration, expected_duration))

    def __init__(self):
        self._parec = None
        self._sox = None

    def _ensure_ready(self):
        profile_manager = btts.ProfileManager()
        ready = profile_manager.get_profiles_state()['a2dp']
        if not ready:
            raise self.NotReadyError()

    def start(self, ofile, duration):
        self._ensure_ready()

        if self._sox != None:
            log.info('Recording in progress. Restarting!')
            self._sox.terminate()
            try:
                self._sox.wait(timeout=_REASONABLE_TERMINATE_TIME)
                self._parec.wait(timeout=_REASONABLE_TERMINATE_TIME)
            except subprocess.TimeoutExpired:
                log.warning('Recording pipeline refused to terminate. Will be killed.')
                self._sox.kill()
                self._parec.kill()
            finally:
                self._sox = None
                self._parec = None

        device_manager = btts.DeviceManager()
        device_address = device_manager.device_address.upper().replace(':', '_')

        # Notes:
        # 1. Not using `sox -t pulseaudio <pa_dev>` as SoX uses pa_simple which
        # connects streams with PA_STREAM_INTERPOLATE_TIMING.
        # 2. Regarding the use of the 'AU' format see
        # http://www.mega-nerd.com/libsndfile/FAQ.html#Q017
        parec_cmd = ('parec --device bluez_source.%s --file-format=au'
                     % (device_address)).split()
        sox_cmd = ('sox -q -t au - %s silence 1 0.5 0.1%% trim 0 %d'
                   % (ofile, duration)).split()

        self._parec = subprocess.Popen(parec_cmd, stdout=subprocess.PIPE)
        self._sox = subprocess.Popen(sox_cmd, stdin=self._parec.stdout)
        self._parec.stdout.close()

        self._start_time = time.monotonic()
        self._duration = duration

        self._ofile = ofile

    def wait(self):
        self._ensure_ready()

        if self._sox == None:
            raise self.NotStartedError()

        total_wait_time = self._duration + self._REASONABLE_RECORD_WAIT_TIME
        elapsed_wait_time = time.monotonic() - self._start_time
        remaining = total_wait_time - elapsed_wait_time

        if remaining < 0:
            log.warning(('Called too late - have been recording for longer '
                         '(%dsecs) than the required duration (%dsecs).')
                        % (elapsed_wait_time, self._duration))
            remaining = 0

        try:
            self._sox.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            self._sox.terminate()

        try:
            self._sox.wait(timeout=_REASONABLE_TERMINATE_TIME)
            self._parec.wait(timeout=_REASONABLE_TERMINATE_TIME)
        except subprocess.TimeoutExpired:
            self._sox.kill()
            self._parec.kill()
            raise btts.cliutils.Failure('Recording pipeline refused to terminate')
        finally:
            self._sox = None
            self._parec = None

        duration = subprocess.check_output(['soxi', '-D', self._ofile])
        duration = math.floor(float(duration))

        if duration < self._duration:
            raise self.RecordTooShortError(duration, self._duration)
