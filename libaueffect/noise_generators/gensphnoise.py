# -*- coding: utf-8 -*-

import libaueffect

import pyrirgen

import numpy as np
import math



class SphericalNoiseGenerator(object):
    def __init__(self, sound_velocity=340, fs=16000, micarray='circular7', spectral_shape='hoth', noise_points=64):

        self._sound_velocity = libaueffect.checked_cast(sound_velocity, 'float')
        self._fs = libaueffect.checked_cast(fs, 'int')

        # spectrum shape - hoth or white
        if spectral_shape in ('hoth', 'white'):
            self._spectral_shape = spectral_shape
        else:
            raise ValueError('The spectral_shape value must be either hoth or white.')

        # microphone array geometry
        if micarray == 'circular7':
            self._micarray = np.concatenate([np.zeros((1,3)), np.array([0.0425 * np.array([np.cos(i * np.pi/3), np.sin(i * np.pi/3), 0]) for i in range(6)])])
        elif micarray == 'mono':
            self._micarray = np.zeros((1,3))
        else:
            self._micarray = micarray

        self._noise_points = noise_points

        print('Instantiating {}'.format(self.__class__.__name__))
        print('Sound velocity: {}'.format(self._sound_velocity))
        print('Sampling frequency: {}'.format(self._fs))
        print('Spectral shape: {}'.format(self._spectral_shape))
        print('Mic array geometry: {}'.format(micarray))
        print('Number of noise points: {}'.format(noise_points))
        print('', flush=True)



    def __call__(self, nsamples, micarray=None):
        if micarray is None:
            return libaueffect.noise_generators.functions.generate_isotropic_noise(self._micarray, nsamples, self._fs, type='sph', spectrum=self._spectral_shape, num_points=self._noise_points)
        else:
            return libaueffect.noise_generators.functions.generate_isotropic_noise(micarray, nsamples, self._fs, type='sph', spectrum=self._spectral_shape, num_points=self._noise_points)


