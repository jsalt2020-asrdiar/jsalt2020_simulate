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


    def __call__(self, inputs, offsets, speaker_labels, to_return=('image', 'noise')):
        # Determine the number of speakers. 
        spkrs = sorted(list(set(speaker_labels)))
        nspkrs = len(spkrs)

        # Generate RIRs. 
        rir, rir_info = self._room_simulator(nspeakers=nspkrs, info_as_display_style=True)

        spkr2idx = {spkr: i for i, spkr in enumerate(spkrs)}
        rir_info.append( ('speakers', spkrs) )

        # Remove the preceding delay. 
        rir = libaueffect.remove_delay_from_rirs(rir)
        nchans = rir[0].shape[0]
        rir_len = rir[0].shape[1]

        # Time-shift and concatenate the utterances of each speaker. 
        target_len = np.amax([dt.shape[0] + offset for dt, offset in zip(inputs, offsets)])
        s = np.zeros((nspkrs, target_len))  # anechoic signals

        utt_gain = {}
        i = 0
        for x, offset, spkr in zip(inputs, offsets, speaker_labels):
            # Randomly change the source amplitude. 
            gain = np.random.uniform(self._gain_range[0], self._gain_range[1])
            utt_gain[f'{i}_{spkr}'] = gain
            i += 1
            gain = 10**(gain / 20)
            s[spkr2idx[spkr], offset : offset + x.shape[0]] += x * gain

        # Reverberate and mix the signals. 
        u = np.zeros((nspkrs, nchans, target_len + rir_len - 1))  # source images
        for spkr in spkrs:
            spkr_idx = spkr2idx[spkr]
            h = rir[spkr_idx]
            for j in range(nchans):
                # u[spkr_idx, j] = scipy.signal.lfilter(h[j], 1, s[spkr_idx])
                u[spkr_idx, j] = scipy.signal.fftconvolve(s[spkr_idx], h[j], mode='full')

        y = np.sum(u, axis=0)

        # Generate noise. 
        if self._noise_generator is not None:
            n = self._noise_generator(nsamples=target_len+rir_len-1)                                                                                                                                                       
            n, snr = libaueffect.signals.scale_noise_to_random_snr(n, y, self._min_snr, self._max_snr)

            # Add the noise and normalize the resultant signal. 
            y += n
        else:
            n = np.zeros((nchans, target_len + rir_len - 1))

        # Normalize the generated signal. 
        max_amplitude = np.amax(np.absolute(y))
        scale = (32767/32768) / max_amplitude * 0.3
        y *= scale
        n *= scale
        u *= scale
        for h in rir:
            h *= scale

        # description of the mixing process
        params = [('mixer', self.__class__.__name__),
                  ('implementation', __name__)]
        params += rir_info
        params.append( ('utt_gain', utt_gain) )
        if self._noise_generator is not None:
            params.append( ('snr', snr) )

        # intermediate signals
        print(to_return)      
        interm = {}
        for wanted in to_return:
            if wanted == 'image':
                data = {}
                for spkr in spkrs:
                    name = f'{wanted}{spkr}'
                    data[name] = u[spkr2idx[spkr]]
                interm[wanted] = data
            elif wanted == 'segment_image':
                data = {}
                i = 0
                for x, offset, spkr in zip(inputs, offsets, speaker_labels):
                    name = f'{wanted}_{i}_{spkr}'
                    i+=1
                    data[name] = u[spkr2idx[spkr], :, offset : offset + x.shape[0] + rir_len - 1 ]
                interm[wanted] = data

            elif wanted == 'noise':
                data = {wanted: n}
                interm[wanted] = data

            elif wanted == 'rir':
                data = {}
                for spkr in spkrs:
                    name = f'{wanted}{spkr}'
                    data[name] = rir[spkr2idx[spkr]]
                interm[wanted] = data

            elif wanted == 'source':
                data = {}
                for spkr in spkrs:
                    name = f'{wanted}{spkr}'
                    data[name] = s[spkr2idx[spkr]]
                interm[wanted] = data
        print(interm)

        return y, OrderedDict(params), interm
