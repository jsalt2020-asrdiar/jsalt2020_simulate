#!/usr/bin/env python3
# encoding: utf-8

# RIR convolution and noise superposition example

import wave, audioop, sys
import numpy as np
import scipy.signal



def _interpret_wav(x, ch, nb):
    # Convert the data to a 16-bit sequence.
    if nb == 1:
        x = audioop.bias(x, nb, -128)
    
    if len(x) % nb != 0:
        print('length = {}'.format(len(x)), file=sys.stderr)
        print('width = {}'.format(nb), file=sys.stderr)
        raise RuntimeError('Not a whole number of frames')       
    
    x = audioop.lin2lin(x, nb, 2)

    # Convert the data to a numpy array.
    scale = 1./float(1 << 15)
    fmt = '<i{:d}'.format(2)
    y = scale * np.frombuffer(x, fmt).astype(np.float32)

    y = y.reshape((-1, ch)).T
    return y



def read_wav(path):
    with wave.open(path) as wf:
        fs = wf.getframerate()
        ch = wf.getnchannels()
        nb = wf.getsampwidth()

        # Read the target segment of audio.
        x = wf.readframes(wf.getnframes())

    try:
        y = _interpret_wav(x, ch, nb)
    except RuntimeError as e:
        print('filename = {}'.format(path), file=sys.stderr)
        raise e

    return y[0], fs   # returning the first channel signal



source_file = '2830-3980-0036_0_a0.wav'
rir_file = '2830-3980-0036_0_r0__0.wav'
noise_file = '2830-3980-0036_0_s2__0.wav'
noisy_file = '2830-3980-0036_0__0.wav'  # reference

# Any wav file loader may be used here. 
s, _ = read_wav(source_file)
h, _ = read_wav(rir_file)
n, _ = read_wav(noise_file)
y, _ = read_wav(noisy_file)

x = scipy.signal.lfilter(h, 1, s) + n

snr = 10 * np.log10( np.sum(y**2) / np.sum((x - y)**2) )

print('')
print(f'SNR between the resynthesized signal and the original synthesized signal is {snr:.1f} dB.')
print('')





