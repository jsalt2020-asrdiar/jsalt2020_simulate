#!/usr/bin/env python
# -*- coding: utf-8 -*-
import argparse, os, sys, contextlib, wave, collections
import numpy as np

import webrtcvad
    

def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (8000, 16000, 32000)
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


class Frame(object):
    def __init__(self, bytes, timestamp, duration):
        self.bytes = bytes
        self.timestamp = timestamp
        self.duration = duration


def frame_generator(frame_duration_ms, audio, sample_rate):
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)
    offset = 0
    timestamp = 0.0
    duration = (float(n) / sample_rate) / 2.0
    while offset + n < len(audio):
        yield Frame(audio[offset:offset + n], timestamp, duration)
        timestamp += duration
        offset += n


def vad_collector(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, frames):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []
    for frame in frames:
        # sys.stdout.write('1' if vad.is_speech(frame.bytes, sample_rate) else '0')
        if not triggered:
            ring_buffer.append(frame)
            num_voiced = len([f for f in ring_buffer
                              if vad.is_speech(f.bytes, sample_rate)])
            if num_voiced > 0.9 * ring_buffer.maxlen:
                # sys.stdout.write('+(%s)' % (ring_buffer[0].timestamp,))
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            num_unvoiced = len([f for f in ring_buffer
                                if not vad.is_speech(f.bytes, sample_rate)])
            if num_unvoiced > 0.9 * ring_buffer.maxlen:
                # sys.stdout.write('-(%s)' % (frame.timestamp + frame.duration))
                triggered = False
                yield b''.join([f.bytes for f in voiced_frames])
                ring_buffer.clear()
                voiced_frames = []

    if voiced_frames:
        yield b''.join([f.bytes for f in voiced_frames])

 
        
def main(args):
    # Read the input file list. 
    print('Reading the input file list.')
    with open(args.inputlist) as f:
        files = [l.strip() for l in f.readlines() if l.strip() != '']
    print('{} files found.'.format(len(files)), flush=True)

    inputdir = os.path.commonpath(files)

    # Process each file. 
    for done, inputfile in enumerate(files):
        # Print the status. 
        if done % 100 == 0:
            print('{}/{}... {:.3f}%'.format(done, len(files), done/len(files)*100))   

        outputfile_base = os.path.join(args.outputdir, os.path.relpath(os.path.splitext(inputfile)[0], start=inputdir))
        os.makedirs(os.path.dirname(outputfile_base), exist_ok=True)

        # Perform VAD.
        audio, sample_rate = read_wave(inputfile)
        vad = webrtcvad.Vad(args.tightlevel)
        frames = frame_generator(30, audio, sample_rate)
        frames = list(frames)
        segments = vad_collector(sample_rate, 30, 300, vad, frames)

        # Chop the audio file.
        i = 0
        for x in segments:
            fmt = '<i{:d}'.format(2)
            y = np.frombuffer(x, fmt).astype(np.float32)

            if len(y) / 16000 > args.min_segment_len:
                outputfile = '{}_{}.wav'.format(outputfile_base, i)
                write_wave(outputfile, x, sample_rate)                
                i += 1



def make_argparse():
    # Set up an argument parser. 
    parser = argparse.ArgumentParser(description='Tightly segment utterances.')
    parser.add_argument('--inputlist', metavar='<file>', required='True',
                        help='Input file list.')
    parser.add_argument('--outputdir', metavar='<dir>', required='True',
                        help='Output directory.')
    parser.add_argument('--tightlevel', choices=[0, 1, 2, 3], metavar='<level>', default=2, 
                        help='0 is the least agressive; 3 the most aggressive.')
    parser.add_argument('--min_segment_len', type=float, metavar='<duration in sec>', default=3, 
                        help='Segments shorter than this threshold are discarded.')

    return parser



if __name__ == '__main__':
    parser = make_argparse()
    args = parser.parse_args()
    main(args)

