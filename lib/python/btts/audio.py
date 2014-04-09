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

_pa_profile_by_bt_profile = {
    'hfp' : 'headset_audio_gateway',
    'a2dp': 'a2dp_source',
}

def _duration(file_path):
    duration = subprocess.check_output(['soxi', '-D', file_path])
    duration = math.floor(float(duration))
    return duration

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

class Minimodem:
    _BAUDMODE = '2'
    _REASONABLE_TIMEOUT = 10

    @staticmethod
    def write(message, file_path):
        cmd = ['minimodem', '--tx', '--file', file_path, Minimodem._BAUDMODE]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                universal_newlines=True)
        proc.communicate(input=message, timeout=Minimodem._REASONABLE_TIMEOUT)

    @staticmethod
    def read(file_path):
        cmd = ['minimodem', '--rx', '--file', file_path, Minimodem._BAUDMODE]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                universal_newlines=True)
        outs, errs = proc.communicate(timeout=Minimodem._REASONABLE_TIMEOUT)
        return outs

class Recorder:
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
        ready = any(profile_manager.get_profiles_state(profiles=['a2dp', 'hfp']))
        if not ready:
            raise self.NotReadyError()

    @staticmethod
    def _device_address_for_pa():
        device_manager = btts.DeviceManager()
        return device_manager.device_address.upper().replace(':', '_')

    @staticmethod
    def receiving_audio():
        args = ('''pactl list short sources |awk '$2 == "bluez_source.%s" { print $7 }' '''
                % (Recorder._device_address_for_pa()))
        out = subprocess.check_output(args, shell=True, universal_newlines=True)
        return out.strip() == 'RUNNING'

    def start(self, ofile, profile, duration = 0, start_padding=0, mono=False):
        assert profile in _pa_profile_by_bt_profile.keys()
        assert duration >= 0

        self._ensure_ready()

        if self._sox != None:
            log.info('Recording in progress. Restarting!')
            self._parec.terminate()
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

        pa_profile = _pa_profile_by_bt_profile[profile]

        # Card profile must be switched before parec is started, otherwise it
        # would get reconnected to default source upon playback-started profile
        # change.
        set_card_profile_cmd = ('pactl set-card-profile bluez_card.%s %s'
                                % (self._device_address_for_pa(), pa_profile)).split()
        try:
            subprocess.check_call(set_card_profile_cmd)
        except subprocess.CalledProcessError as e:
            raise self.Error('Failed to set card profile: pactl failed')

        # Notes:
        # 1. Not using `sox -t pulseaudio <pa_dev>` as SoX uses pa_simple which
        # connects streams with PA_STREAM_INTERPOLATE_TIMING.
        # 2. Regarding the use of the 'AU' format see
        # http://www.mega-nerd.com/libsndfile/FAQ.html#Q017
        parec_cmd = ('parec --device bluez_source.%s --file-format=au'
                     % (self._device_address_for_pa())).split()
        sox_cmd = ('sox -q -t au - %s silence 1 0.5 0.1%%'
                   % (ofile)).split()
        if duration > 0:
            sox_cmd += ('trim 0 %d' % (duration)).split()
        if mono:
            sox_cmd += ('remix -').split()

        self._parec = subprocess.Popen(parec_cmd, stdout=subprocess.PIPE)
        self._sox = subprocess.Popen(sox_cmd, stdin=self._parec.stdout)
        self._parec.stdout.close()

        self._start_time = time.monotonic()
        self._duration = duration
        self._start_padding = start_padding

        self._ofile = ofile

    def wait(self):
        self._ensure_ready()

        if self._sox == None:
            raise self.NotStartedError()

        elapsed = time.monotonic() - self._start_time
        remaining = max(0, self._duration - elapsed)
        remaining += self._start_padding

        try:
            self._sox.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            self._parec.terminate()

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

        duration = _duration(self._ofile)

        if duration < self._duration:
            raise self.RecordTooShortError(duration, self._duration)

class Player:
    _REASONABLE_PLAY_BACK_WAIT_TIME = 5 # seconds

    class Error(Exception):
        _dbus_error_name = 'org.merproject.btts.Player.Error'

    class NotReadyError(Error):
        def __init__(self):
            Player.Error.__init__(self, 'Not ready')

    class NotStartedError(Error):
        def __init__(self):
            Player.Error.__init__(self, 'Operation not started')

    def __init__(self):
        self._sox = None
        self._paplay = None

    def _ensure_ready(self):
        profile_manager = btts.ProfileManager()
        ready = profile_manager.get_profiles_state()['hfp']
        if not ready:
            raise self.NotReadyError()

    def start(self, ifile, duration=0):
        '''
        Start playing back.

        If 'duration' (seconds) is given, it will limit maximum length to be played back.

        Returns expected play back time.
        '''
        assert duration >= 0
        self._ensure_ready()

        if self._sox != None:
            log.info('Playback in progress. Restarting!')
            self._sox.terminate()
            try:
                self._sox.wait(timeout=_REASONABLE_TERMINATE_TIME)
                self._paplay.wait(timeout=_REASONABLE_TERMINATE_TIME)
            except subprocess.TimeoutExpired:
                log.warning('Playback pipeline refused to terminate. Will be killed.')
                self._sox.kill()
                self._paplay.kill()
            finally:
                self._sox = None
                self._paplay = None

        total_duration = _duration(ifile)
        if total_duration < duration:
            log.warning('%s: File duration %gs is shorter than requested %gs'
                        % (ifile, total_duration, duration))
        if duration == 0:
            duration = math.ceil(total_duration)

        sox_cmd = ('sox -q %s -t au - trim 0 %d' % (ifile, duration)).split()
        pacat_cmd = ('pacat --device btts_inject --file-format=au').split()

        self._sox = subprocess.Popen(sox_cmd, stdout=subprocess.PIPE)
        self._pacat = subprocess.Popen(pacat_cmd, stdin=self._sox.stdout)
        self._sox.stdout.close()

        self._start_time = time.monotonic()
        self._duration = duration

        self._ifile = ifile

        return duration

    def wait(self):
        self._ensure_ready()

        if self._sox == None:
            raise self.NotStartedError()

        total_wait_time = self._duration + self._REASONABLE_PLAY_BACK_WAIT_TIME
        elapsed_wait_time = time.monotonic() - self._start_time
        remaining = max(0, total_wait_time - elapsed_wait_time)

        try:
            self._pacat.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            self._sox.terminate()

        try:
            self._sox.wait(timeout=_REASONABLE_TERMINATE_TIME)
            self._pacat.wait(timeout=_REASONABLE_TERMINATE_TIME)
        except subprocess.TimeoutExpired:
            self._sox.kill()
            self._pacat.kill()
            raise btts.cliutils.Failure('Playback pipeline refused to terminate')
        finally:
            self._sox = None
            self._pacat = None
