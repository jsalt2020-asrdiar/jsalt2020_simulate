# -*- coding: utf-8 -*-
import libaueffect

import numpy as np
import scipy
import scipy.io.wavfile
import math
import random
import copy
import sys



def load_random_rirs(rirfiles, nspeakers=2, sample_rate=16000):
    files = copy.deepcopy(rirfiles)
    random.shuffle(files)
    files = files[:nspeakers]
    h = [libaueffect.read_wav(f, sample_rate=sample_rate)[0] for f in files]
    if h[0].shape != h[1].shape:
        raise RuntimeError('The RIRs have different dimensions.')

    return h


def remove_delay_from_rirs(h):
    delay = sys.maxsize

    for i in range(len(h)):
        for j in range(len(h[i])):
            h_env = np.absolute(scipy.signal.hilbert(h[i][j]))
            if delay > np.argmax(h_env):
                delay = np.argmax(h_env)
    for i in range(len(h)):
        h[i] = h[i][:, delay:]

    return h


def reverb_mix(x, rirfiles, sample_rate=16000, cancel_delay=False, second_arg_is_filename=True):
    if second_arg_is_filename:
        h = load_random_rirs(rirfiles, nspeakers=2, sample_rate=sample_rate)
    else:
        h = rirfiles

    nchans = h[0].shape[0]
        
    # Compensate for the delay.
    if cancel_delay:
        h = remove_delay_from_rirs(h)

    # Filter the source signals. 
    nsrcs = x.shape[0]
    y = []
    for i in range(nsrcs):
        y.append(np.stack([scipy.signal.lfilter(h[i][j], 1, x[i]) for j in range(nchans)]))
    y = np.stack(y)

    # Mix the signals together. 
    z = np.sum(y, axis=0)

    # # Normalize the signal.
    # max_amplitude = max( [np.amax(np.absolute(z)), np.amax(np.absolute(y))] )
    # if max_amplitude > 0:
    #     scale = (32767/32768) / max_amplitude * amp
    #     y *= scale
    #     z *= scale

    return z, y, h



# Adjust the noise level to a given SNR.
def scale_noise_to_snr(n, x, snr, valid_segment=(None, None)):
    mag_x = np.mean(np.absolute(x[valid_segment[0] : valid_segment[1]]))
    maz_n = np.mean(np.absolute(n[valid_segment[0] : valid_segment[1]]))
    scale = mag_x / maz_n * ( math.pow(10, -snr / 20.0) )
    return scale * n


# Adjust the noise level to a randomy chosen SNR.
def scale_noise_to_random_snr(n, x, min_snr, max_snr, valid_segment=(None, None)):
    snr = np.random.uniform(min_snr, max_snr)
    return scale_noise_to_snr(n, x, snr, valid_segment), snr
