# -*- coding: utf-8 -*-
import numpy as np
import scipy.io.wavfile
from collections import defaultdict

import os, math, struct, sys, warnings, copy, re

import wave, audioop, resampy



def read_wavheader(path):
    with wave.open(path) as wf:
        samplerate = wf.getframerate()
        nchannels = wf.getnchannels()
        qbyte = wf.getsampwidth()
        nsamples = wf.getnframes()

    return nsamples, nchannels, samplerate, qbyte



def read_wavheaders(paths):
    nsamples = 0
    nchannels = 0

    for f in paths:
        nf, ch, fs, nb = read_wavheader(f)

        if nsamples == 0:
            nsamples = nf
        elif nf != nsamples:
            raise RuntimeError('The input audio files must have exactly the same length.')

        nchannels += ch

    return nsamples, nchannels, fs, nb



def _interpret_wav(x, fs, ch, nb, sample_rate):
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
    if sample_rate is not None and sample_rate != fs:
        y = resampy.resample(y, fs, sample_rate)
    return y



def read_wav(path, sample_rate=None, channel=None):
    with wave.open(path) as wf:
        fs = wf.getframerate()
        ch = wf.getnchannels()
        nb = wf.getsampwidth()

        # Read the target segment of audio.
        x = wf.readframes(wf.getnframes())

        try:
            y = _interpret_wav(x, fs, ch, nb, sample_rate)
        except RuntimeError as e:
            print('filename = {}'.format(path), file=sys.stderr)
            raise e

        if sample_rate is not None:
            fs = sample_rate

        if channel is None:
            return y, fs
        elif channel == 'random':
            return y[np.random.randint(0, ch)], fs
        else:
            return y[channel], fs



def snip_wav(path, length, start=0, sample_rate=None, channel=None):
    with wave.open(path) as wf:
        fs = wf.getframerate()
        ch = wf.getnchannels()
        nb = wf.getsampwidth()

        if sample_rate is None:
            len_to_read = length
            start_idx = start
        else:
            len_to_read = math.ceil(length * fs / sample_rate)
            start_idx = start * fs // sample_rate

        # Read the target segment of audio.
        wf.setpos(start_idx)
        x = wf.readframes(len_to_read)

        y = _interpret_wav(x, fs, ch, nb, sample_rate)

        if sample_rate is not None:
            fs = sample_rate

        if channel is None:
            return y[:, :length], fs
        elif channel == 'random':
            return y[np.random.randint(0, ch)], fs
        else:
            return y[channel, :length], fs


def snip_wavs(paths, length, start=0, sample_rate=None):
    x = snip_wav(paths[0], length, start, sample_rate)
    for f in paths[1:]:
        y = snip_wav(f, length, start, sample_rate)
        x = np.vstack((x,y))

    return x



def quantize_wav(x):
    int16_max = np.iinfo(np.int16).max
    int16_min = np.iinfo(np.int16).min

    if x.dtype.kind == 'f':
        x *= int16_max

    sample_to_clip = np.sum(x > int16_max)
    if sample_to_clip > 0:
        warnings.warn('Clipping {} samples'.format(sample_to_clip))
    x = np.clip(x, int16_min, int16_max)
    x = x.astype(np.int16)

    return x



def append_wav(x, path):
    '''Adapted from scipy.io.wavfile.read()'''
    x = copy.deepcopy(x)

    x = quantize_wav(x)
    if x.ndim > 1:
        x = x.T

    fid = open(path, 'r+b')

    try:
        file_size, is_big_endian = scipy.io.wavfile._read_riff_chunk(fid)
        fmt_chunk_received = False
        data_chunk_received = False

        if is_big_endian:
            raise NotImplementedError('RIFX is not supported.')

        while fid.tell() < file_size and not data_chunk_received:
            # read the next chunk
            chunk_id = fid.read(4)

            # 'fmt' chunk
            if chunk_id == b'fmt ':
                fmt_chunk_received = True
                fmt_chunk = scipy.io.wavfile._read_fmt_chunk(fid, is_big_endian)
                format_tag, channels, fs = fmt_chunk[1:4]
                bit_depth = fmt_chunk[6]

                if format_tag != 0x0001:
                    raise NotImplementedError('Unsupported format: only PCM is supported.')
                if bit_depth not in (8, 16, 32, 64, 96, 128):
                    raise NotImplementedError("Unsupported bit depth: the wav file has {}-bit data.".format(bit_depth))

            # 'data' chunk
            elif chunk_id == b'data':
                if not fmt_chunk_received:
                    raise RuntimeError("Corrupted wav file: fmt chunk not found before data chunk.")
                data_chunk_received = True

                orig_data_size = struct.unpack('<I', fid.read(4))[0]
                new_data_size = orig_data_size + np.prod(x.shape) * bit_depth // 8;

                fid.seek(-4, 1)
                fid.write(struct.pack('<I', new_data_size))

                fid.seek(orig_data_size, 1)

                if x.dtype.byteorder == '>' or (x.dtype.byteorder == '=' and sys.byteorder == 'big'):
                    x = x.byteswap()
                scipy.io.wavfile._array_tofile(fid, x)

                # Determine file size and place it in correct position at start of the file.
                size = fid.tell()
                fid.seek(4, 0)
                fid.write(struct.pack('<I', size-8))

            elif chunk_id == b'fact':
                scipy.io.wavfile._skip_unknown_chunk(fid, is_big_endian)
            elif chunk_id == b'LIST':
                scipy.io.wavfile._skip_unknown_chunk(fid, is_big_endian)
            elif chunk_id in (b'JUNK', b'Fake'):
                scipy.io.wavfile._skip_unknown_chunk(fid, is_big_endian)
            else:
                raise RuntimeError('Unknown chunk.')

    finally:
        fid.close()



def write_wav(x, path, sample_rate=16000, avoid_clipping=False, save_as_one_file=True):
    x = copy.deepcopy(x)

    if avoid_clipping:
        m = np.max(np.abs(x))
        if m > np.iinfo(np.int16).max / np.abs(np.iinfo(np.int16).min):
            x /= ( m * np.abs(np.iinfo(np.int16).min) / np.iinfo(np.int16).max )

    x = quantize_wav(x)
    if x.ndim > 1:
        x = x.T

    os.makedirs(os.path.dirname(path), exist_ok=True)

    if save_as_one_file or x.ndim == 1:
        scipy.io.wavfile.write(path, sample_rate, x)
    else:        
        nmics = x.shape[1]
        for i in range(nmics):
            basename = path[:-4] if path[-4:] == '.wav' else path
            fname = f'{basename}__{i}.wav'
            scipy.io.wavfile.write(fname, sample_rate, x[:, i])



def load_rir_collection(rirlist, filename_style='haerdoga'):
    if filename_style == 'haerdoga':
        p = re.compile('RIR_(r\d+)_s\d+_p\d+_.*\.wav')
    else:
        raise ValueError('filename_style must be haerdoga.')

    rirfiles = defaultdict(list)

    with open(rirlist) as f:
        for s in f:
            file = s.rstrip()
            m = p.match(os.path.basename(file))
            if m is None:
                raise RuntimeError('RIR file name does not match the supposed pattern.')
            else:
                rirfiles[m.group(1)].append(file)

    # Check if each room has 2 or more RIRs.
    for room, files in rirfiles.items():
        if len(files) < 2:
            raise RuntimeError('Room {} does not have multiple RIRs.'.format(room))
        
    return list(rirfiles.values())

