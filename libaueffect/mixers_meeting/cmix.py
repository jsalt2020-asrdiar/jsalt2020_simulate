# -*- coding: utf-8 -*-
import libaueffect

import os
from collections import OrderedDict
import numpy as np
import copy

import re


class CleanMixMeeting(object):
    def __init__(self, gain_range=[-5, 5]):
        self._gain_range = gain_range

        print('Instantiating CleanMixMeeting')
        print('Gain range in dB: ({}, {})'.format(self._gain_range[0], self._gain_range[1]))
        print('', flush=True)



    def substitute_generators(self, generator_pool):
        pass


    def __call__(self, inputs, offsets, speaker_labels, to_return=()):
        ylen = np.amax([len(dt) + offset for dt, offset in zip(inputs, offsets)])

        y = np.zeros(ylen)
        for dt, offset in zip(inputs, offsets):
            gain = np.random.uniform(self._gain_range[0], self._gain_range[1])
            scale = 10**(gain / 20)
            y[offset : offset + len(dt)] += scale * dt

        # description of the mixing process
        params = [('mixer', self.__class__.__name__),
                  ('implementation', __name__)]

        return y, OrderedDict(params), {}
