# -*- coding: utf-8 -*-
import os, json
import numpy as np

import libaueffect



# Create an array of mixers from a config file. 
def create_AudioMixerArray(file):
    with open(file) as f:
        mixer_array_configs = json.load(f)

    print('BUILDING AN ARRAY OF AUDIO MIXERS FROM {}'.format(file))
    print('', flush=True)

    # Make the prior probabilities sum to one. 
    priors = np.array([float(x) for x in mixer_array_configs['probabilities']])
    priors = priors / np.sum(priors)

    # mixers
    mixers_desc = mixer_array_configs['mixers']
    mixers = []
    for mixer_info in mixers_desc:
        mixers.append( libaueffect.load_class(mixer_info['mixer'])(**mixer_info['opts']) )

    # generator pool
    if 'generators' in mixer_array_configs:
        generators_desc = mixer_array_configs['generators']
        generators = {}
        for generator_info in generators_desc:
            generators[generator_info['id']] = libaueffect.load_class(generator_info['generator'])(**generator_info['opts'])

    # Substitute the generators. 
    for mixer in mixers:
        mixer.substitute_generators(generators)


    return mixers, priors        
