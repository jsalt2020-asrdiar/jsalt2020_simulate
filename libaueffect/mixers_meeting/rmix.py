# -*- coding: utf-8 -*-
import libaueffect

import os, copy, scipy, re
from collections import OrderedDict
import numpy as np


class ReverbMixMeeting(object):
    def __init__(self, room_simulator, noise_generator=None, gain_range=[-5, 5], min_snr=0.0, max_snr=20.0):
        self._room_simulator = room_simulator
        self._noise_generator = noise_generator

        self._gain_range = gain_range
        self._min_snr = libaueffect.checked_cast(min_snr, 'float')
        self._max_snr = libaueffect.checked_cast(max_snr, 'float')

        print('Instantiating ReverbMixMeeting')
        print('Gain range in dB: ({}, {})'.format(self._gain_range[0], self._gain_range[1]))
        print('SNR range in dB: ({}, {})'.format(self._min_snr, self._max_snr))
        print('', flush=True)



    def substitute_generators(self, generator_pool):
        if isinstance(self._room_simulator, str):
            m = re.match(r'id=(\S+)', self._room_simulator)
            if m is not None:
                id = m.group(1)
                self._room_simulator = generator_pool[id]

        if isinstance(self._noise_generator, str):
            m = re.match(r'id=(\S+)', self._noise_generator)
            if m is not None:
                id = m.group(1)
                self._noise_generator = generator_pool[id]


    def __call__(self, inputs, offsets, speaker_labels):
        # Determine the number of speakers. 
        spkrs = sorted(list(set(speaker_labels)))
        nspkrs = len(spkrs)

        # Generate RIRs. 
        ret = self._room_simulator(nspeakers=nspkrs, info_as_display_style=True)
        if len(ret) == 2:
            rir, rir_info = ret
            micarray = None
        else:
            rir, rir_info, micarray = ret

        spkr2rir = {spkr: i for i, spkr in enumerate(spkrs)}
        rir_info.append( ('speakers', spkrs) )

        # Remove the preceding delay. 
        rir = libaueffect.remove_delay_from_rirs(rir)
        nchans = rir[0].shape[0]

        # Reverberate the source signals. 
        z = []
        for x, spkr in zip(inputs, speaker_labels):
            h = rir[ spkr2rir[spkr] ]            
            z.append( np.stack([scipy.signal.lfilter(h[j], 1, x) for j in range(nchans)]) )

        # Generate the mixture signals. 
        target_len = np.amax([dt.shape[1] + offset for dt, offset in zip(z, offsets)])

        y = np.zeros((nchans, target_len))
        for dt, offset in zip(z, offsets):
            gain = np.random.uniform(self._gain_range[0], self._gain_range[1])
            scale = 10**(gain / 20)
            y[:, offset : offset + dt.shape[1]] += scale * dt
       
        # Generage noise. 
        if self._noise_generator is not None:
            n = self._noise_generator(nsamples=target_len, micarray=micarray)
            n, snr = libaueffect.signals.scale_noise_to_random_snr(n, y, self._min_snr, self._max_snr)

            # Add the noise and normalize the resultant signal. 
            y = y + n

            # Normalize the generated signal. 
            max_amplitude = np.amax(np.absolute(y))
            scale = (32767/32768) / max_amplitude
            y *= scale

        # description of the mixing process
        params = [('mixer', self.__class__.__name__),
                  ('implementation', __name__)]
        params += rir_info
        if self._noise_generator is not None:
            params.append( ('snr', snr) )

        return y, OrderedDict(params)
