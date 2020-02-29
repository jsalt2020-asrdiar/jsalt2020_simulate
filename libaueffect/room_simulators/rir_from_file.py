# -*- coding: utf-8 -*-
import libaueffect

import numpy as np



class RirGeneratorFromFile(object):
    def __init__(self, rirfilelist):
        self._rirfiles = libaueffect.load_rir_collection(rirfilelist, filename_style='haerdoga')

        print('Instantiating {}'.format(self.__class__.__name__))
        print('RIRs listed in {} are used.'.format(rirfilelist))
        print('{} rooms found.'.format(len(self._rirfiles)))
        print('', flush=True)



    def __call__(self, nspeakers=2, info_as_display_style=False):
        rirfiles = self._rirfiles[np.random.randint(0, len(self._rirfiles))]  # room picked up randomly
        h = libaueffect.load_random_rirs(rirfiles, nspeakers=nspeakers)

        if info_as_display_style:
            info = [('rirfiles', rirfiles)]
            return h, info
        else:
            return h, rirfiles
