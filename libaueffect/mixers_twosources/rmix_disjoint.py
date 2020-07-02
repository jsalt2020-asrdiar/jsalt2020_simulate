# -*- coding: utf-8 -*-
import libaueffect

import os
from collections import OrderedDict
import numpy as np
import copy

import re


class ReverbMixDisjointNoise(object):
    def __init__(self, room_simulator, noise_generator=None, min_snr=0.0, max_snr=20.0, max_mixlen=10.0, max_silence=2.0, max_amplitude=1.0, min_amplitude=0.3, min_sillen=2, max_uttlen=100000, no_delay=True):
        self._room_simulator = room_simulator
        self._noise_generator = noise_generator

        self._min_snr = libaueffect.checked_cast(min_snr, 'float')
        self._max_snr = libaueffect.checked_cast(max_snr, 'float')
        self._max_mixlen = libaueffect.checked_cast(max_mixlen, 'float')
        self._max_silence = libaueffect.checked_cast(max_silence, 'float')
        self._max_amplitude = libaueffect.checked_cast(max_amplitude, 'float')
        self._min_amplitude = libaueffect.checked_cast(min_amplitude, 'float')
        self._no_delay = libaueffect.checked_cast(no_delay, 'bool')
        self._min_sillen = libaueffect.checked_cast(min_sillen, 'float')
        self._max_uttlen = libaueffect.checked_cast(max_uttlen, 'float')

        print('Instantiating AnechoicMixDisjoint')
        print('SNR range in dB: ({}, {})'.format(self._min_snr, self._max_snr))
        print('Maximum mixture length: {} s'.format(self._max_mixlen))
        print('Maximum silence duration: {} s'.format(self._max_silence))
        print('Maximum length of each speaker utterance: {} s'.format(self._max_uttlen))
        print('Amplitude range: ({}, {})'.format(self._min_amplitude, self._max_amplitude))
        print('Delay cancellation: {}'.format(self._no_delay))        
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


    def __call__(self, inputs, samplerate, output_filename, input_filenames, to_save=('image', 'noise'), save_as_one_file=False):
        print(output_filename)
        for i, f in enumerate(input_filenames):
            if i == 0:
                print('\t= {}'.format(f))
            else:
                print('\t+ {}'.format(f))

        # Truncate each utterance. 
        max_uttlen = int(np.floor(self._max_uttlen * samplerate))
        for i in range(len(inputs)):
            if len(inputs[i]) > max_uttlen:
                b = np.random.randint(0, len(inputs[i]) - max_uttlen)
                inputs[i] = inputs[i][b : b + max_uttlen]

        # 0 source
        if len(inputs) == 0:
            sillen = 0
            nsamples = int(np.random.uniform(self._min_sillen, self._max_mixlen) * samplerate)
            x = np.zeros((2, nsamples))

        # 1 source
        elif len(inputs) == 1:
            sillen = 0                   
            x = np.stack([inputs[0], np.zeros(inputs[0].shape)])

        # 2+ sources
        else:
            # Radomly determine the silence length. 
            sillen = np.random.uniform(0, self._max_silence)
            maxspeechsamples = int((self._max_mixlen - sillen) * samplerate)

            len0 = len(inputs[0])
            len1 = len(inputs[1])
            
            # Truncate the signals. 
            if len0 + len1 > maxspeechsamples:
                x = []
                x.append(inputs[0][:int(maxspeechsamples * (len0 / (len0 + len1)))])
                x.append(inputs[1][:int(maxspeechsamples * (len1 / (len0 + len1)))])
            else:
                x = copy.deepcopy(inputs[:2])

            target_len = len(x[0]) + len(x[1]) + int(sillen * samplerate)
            x = np.stack([np.pad(x[0], mode='constant', pad_width=(0, target_len - len(x[0]))), 
                          np.pad(x[1], mode='constant', pad_width=(target_len - len(x[1]), 0))])
       
        # Truncate long signals. 
        x = x[:, :min(x.shape[1], int(samplerate * self._max_mixlen))]
        target_len = x.shape[1]

        # Filter and mix the signals. 
        target_amp = np.random.uniform(self._min_amplitude, self._max_amplitude)
        h, h_info = self._room_simulator(nspeakers=2, info_as_display_style=True)
        z, y, h = libaueffect.reverb_mix(x, h, sample_rate=samplerate, cancel_delay=self._no_delay, second_arg_is_filename=False)

        # Generage noise. 
        if self._noise_generator is not None:
            n = self._noise_generator(nsamples=target_len)
            if len(inputs) > 0:
                n, snr = libaueffect.signals.scale_noise_to_random_snr(n, z, self._min_snr, self._max_snr)
            else:
                snr = float('-inf')

            # Add the noise and normalize the resultant signal. 
            u = z + n


        else:
            u = np.copy(z)

        # Normalize the generated signal. 
        max_amplitude = np.amax(np.absolute(u))
        scale = (32767/32768) / max_amplitude * target_amp

        u *= scale
        y *= scale
        n *= scale
        for i in range(len(h)):
            h[i] *= scale

        # description of the mixing process
        params = [('mixer', self.__class__.__name__),
                  ('implementation', __name__), 
                  ('amplitude', target_amp),
                  ('silence length in seconds', sillen)]
        params += h_info
        if self._noise_generator is not None:
            params.append( ('snr', snr) )

        path, ext = os.path.splitext(output_filename)        

        # Save the reverberant source signals. 
        if 'image' in to_save:
            for i in range(len(y)):
                outfile = '{}_s{}{}'.format(path, i, ext)            
                libaueffect.write_wav(y[i], outfile, sample_rate=samplerate, avoid_clipping=False, save_as_one_file=save_as_one_file)
                params.append(('source{}'.format(i), outfile))

        # Save the noise. 
        if 'noise' in to_save and self._noise_generator is not None:
            outfile = '{}_s{}{}'.format(path, len(y), ext)            
            libaueffect.write_wav(n, outfile, sample_rate=samplerate, avoid_clipping=False, save_as_one_file=save_as_one_file)
            params.append(('noise', outfile))

        # Save the RIRs.
        if 'rir' in to_save: 
            for i in range(len(h)):
                outfile = '{}_r{}{}'.format(path, i, ext)            
                libaueffect.write_wav(h[i], outfile, sample_rate=samplerate, avoid_clipping=False, save_as_one_file=save_as_one_file)
                params.append(('rir{}'.format(i), outfile))

        # Save the anechoic source signals. 
        if 'source' in to_save:
            path, ext = os.path.splitext(output_filename)        
            for i in range(len(x)):
                outfile = '{}_a{}{}'.format(path, i, ext)            
                libaueffect.write_wav(x[i], outfile, sample_rate=samplerate, avoid_clipping=False, save_as_one_file=save_as_one_file)
                params.append(('anechoic{}'.format(i), outfile))

        return u, OrderedDict(params)
