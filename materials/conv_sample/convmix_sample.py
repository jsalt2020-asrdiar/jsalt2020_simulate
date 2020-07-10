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


source_files = ['000_source260.wav', '000_source2961.wav', '000_source4077.wav', '000_source4446.wav', '000_source6829.wav', '000_source7127.wav', '000_source8230.wav']
rir_files = ['000_rir260__0.wav', '000_rir2961__0.wav', '000_rir4077__0.wav', '000_rir4446__0.wav', '000_rir6829__0.wav', '000_rir7127__0.wav', '000_rir8230__0.wav']
noise_file = '000_noise__0.wav'
noisy_file = '000__0.wav'  # reference

# Any wav file loader may be used here. 
x = []
for source_file, rir_file in zip(source_files, rir_files):
    s, _ = read_wav(source_file)
    h, _ = read_wav(rir_file)
    x.append(scipy.signal.lfilter(h, 1, s))
x = np.sum(np.stack(x), axis=0)

n, _ = read_wav(noise_file)
x += n

y, _ = read_wav(noisy_file)

snr = 10 * np.log10( np.sum(y**2) / np.sum((x - y)**2) )

print('')
print(f'SNR between the resynthesized signal and the original synthesized signal is {snr:.1f} dB.')
print('')





