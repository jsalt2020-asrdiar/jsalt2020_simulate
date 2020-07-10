# -*- coding: utf-8 -*-
import libaueffect
import numpy as np
import scipy.interpolate as interp



class SphericalNoiseGenerator(object):
    def __init__(self, sound_velocity=340, fs=16000, micarray='circular7', noise_points=64):

        self._sound_velocity = libaueffect.checked_cast(sound_velocity, 'float')
        self._fs = libaueffect.checked_cast(fs, 'int')

        # microphone array geometry
        if micarray == 'circular7':
            self._micarray = np.concatenate([np.zeros((1,3)), np.array([0.0425 * np.array([np.cos(i * np.pi/3), np.sin(i * np.pi/3), 0]) for i in range(6)])])
        elif micarray == 'mono':
            self._micarray = np.zeros((1,3))
        else:
            self._micarray = micarray
        self._nmics = self._micarray.shape[0]

        # Determine the number of points to sample. 
        if self._nmics == 1:
            self._npoints = 1
        else:
            self._npoints = noise_points

        # This is the sampled locations. 
        self._loc_xyz = libaueffect.noise_generators.functions.sample_sphere(self._npoints)

        # Get the spectral shape. 
        self._get_hoth_mag()

        print('Instantiating {}'.format(self.__class__.__name__))
        print('Sound velocity: {}'.format(self._sound_velocity))
        print('Sampling frequency: {}'.format(self._fs))
        print('Mic array geometry: {}'.format(micarray))
        print('Number of noise source points: {}'.format(self._npoints))
        print('', flush=True)

        self._tau = np.zeros((self._npoints, self._nmics))
        for i in range(self._npoints):
            for m in range(1, self._nmics):
                delta = np.sum(self._micarray[m, :] * self._loc_xyz[:, i])
                self._tau[i, m] = delta * self._fs / self._sound_velocity



    def __call__(self, nsamples):
        # Calculate the FFT size. 
        fft_size = int(2 ** np.ceil(np.log2(nsamples)))
        fft_size_by_2 = int(fft_size/2)

        # Get the interpolated spectral shape. 
        g = self._get_hoth_mag_interp(fft_size)

        # For each point, generate random noise in frequency domain and multiply by the steering vector
        w = 2 * np.pi * np.arange(0, fft_size_by_2 + 1, 1) / fft_size

        Z = np.random.normal(0, 1, (self._npoints, 2, fft_size_by_2 + 1))
        Zr, Zi = np.split(Z, 2, axis=1)    
        Z = Zr + 1j * Zi
        Z = Z * np.exp(-1j * w[np.newaxis, np.newaxis] * self._tau[..., np.newaxis])
        X = np.sum(Z, axis=0)
        X = X / np.sqrt(self._npoints)
        X *= g[np.newaxis]

        # transform to time domain
        X[:, 0] = np.sqrt(fft_size) * np.real(X[:, 0])
        X[:, fft_size_by_2] = np.sqrt(fft_size) * np.real(X[:, fft_size_by_2])
        X[:, 1:fft_size_by_2] = np.sqrt(fft_size_by_2) * X[:, 1:fft_size_by_2]

        n = np.fft.irfft(X, fft_size, axis=1)
        n = n[:, 0:nsamples]

        return n


    def _get_hoth_mag(self):
        # Hoth Noise Specifications
        # For details, see p. 80 of
        # http://studylib.net/doc/18787871/ieee-std-269-2001-draft-standard-methods-for-measuring
        hoth_freqs = [100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000]
        hoth_mag_db = [32.4, 30.9, 29.1, 27.6, 26, 24.4, 22.7, 21.1, 19.5, 17.8, 16.2, 14.6, 12.9, 11.3, 9.6, 7.8, 5.4, 2.6, -1.3, -6.6]
        hoth_index_1000_hz = 10
        hoth_index_4000_hz = 16
        hoth_tolerance = 3 # +/- 3dB

        hoth_mag = np.asarray(hoth_mag_db) - hoth_mag_db[hoth_index_1000_hz]
        hoth_mag = np.power(10, hoth_mag/20)
        hoth_w = 2 * np.pi * np.asarray(hoth_freqs) / self._fs

        if (self._fs == 16000):
            self._hoth_mag = interp.interp1d(hoth_w, 
                                             hoth_mag, 
                                             kind='cubic', 
                                             bounds_error=False,
                                             fill_value=(hoth_mag[0], hoth_mag[-1]))
        elif (self._fs == 8000):
            self._hoth_mag = interp.interp1d(hoth_w[0:hoth_index_4000_hz + 1], 
                                             hoth_mag[0:hoth_index_4000_hz + 1], 
                                             kind='cubic', 
                                             bounds_error=False,
                                             fill_value=(hoth_mag[0], hoth_mag[hoth_index_4000_hz + 1]))
        else:
            ValueError('Can only generate Hoth noise for 16000 sampling rates!')

        return self._hoth_mag



    def _get_hoth_mag_interp(self, fft_size):
        fft_size_by_2 = int(fft_size / 2)
        w = 2 * np.pi * np.arange(0, fft_size_by_2 + 1, 1) / fft_size

        hoth_mag_interp = self._hoth_mag(w)
        hoth_mag_interp[0] = 0 # skip DC (0 Hz)

        return hoth_mag_interp
