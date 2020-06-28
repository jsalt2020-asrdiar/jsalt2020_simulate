# -*- coding: utf-8 -*-
import libaueffect

import pyrirgen

import numpy as np
import math



class RandomRirGenerator(object):
    def __init__(self, sound_velocity=340, fs=16000, 
                 roomdim_range_x=[5, 10], roomdim_range_y=[5, 10], roomdim_range_z=[2.5, 4.5], 
                 micpos='center', 
                 roomcenter_mic_dist_max_x=0.5, roomcenter_mic_dist_max_y=0.5, micpos_range_z=[0.6, 0.9], 
                 corner_mic_dist_max_x=0.03, corner_mic_dist_max_y=0.03, 
                 spkr_mic_dist_range_x=[0.5, 4], spkr_mic_dist_range_y=[0.5, 4], spkr_mic_dist_range_z=[0.1, 0.5], 
                 t60_range = [0.1, 0.4], 
                 min_angle_diff = 30, 
                 max_angle_diff = 360, 
                 micarray='circular7'):

        self._sound_velocity = libaueffect.checked_cast(sound_velocity, 'float')
        self._fs = libaueffect.checked_cast(fs, 'int')

        self._roomdim_range_x = libaueffect.checked_cast_array(roomdim_range_x, 'float', nelems=2)
        self._roomdim_range_y = libaueffect.checked_cast_array(roomdim_range_y, 'float', nelems=2)
        self._roomdim_range_z = libaueffect.checked_cast_array(roomdim_range_z, 'float', nelems=2)

        self._micpos = micpos
        self._roomcenter_mic_dist_max_x = libaueffect.checked_cast(roomcenter_mic_dist_max_x, 'float')
        self._roomcenter_mic_dist_max_y = libaueffect.checked_cast(roomcenter_mic_dist_max_y, 'float')
        self._micpos_range_z = libaueffect.checked_cast_array(micpos_range_z, 'float', nelems=2)

        self._corner_mic_dist_max_x = libaueffect.checked_cast(corner_mic_dist_max_x, 'float')
        self._corner_mic_dist_max_y = libaueffect.checked_cast(corner_mic_dist_max_y, 'float')

        self._spkr_mic_dist_range_x = libaueffect.checked_cast_array(spkr_mic_dist_range_x, 'float', nelems=2)
        self._spkr_mic_dist_range_y = libaueffect.checked_cast_array(spkr_mic_dist_range_y, 'float', nelems=2)
        self._spkr_mic_dist_range_z = libaueffect.checked_cast_array(spkr_mic_dist_range_z, 'float', nelems=2)

        self._t60_range = libaueffect.checked_cast_array(t60_range, 'float', nelems=2)

        self._min_angle_diff = libaueffect.checked_cast(min_angle_diff, 'float')
        self._max_angle_diff = libaueffect.checked_cast(max_angle_diff, 'float')

        if self._min_angle_diff >= self._max_angle_diff:
            raise ValueError('min_angle_diff (given: {}) must be smaller than max_angle_diff (given: {}).'.format(self._min_angle_diff, self._max_angle_diff))

        # microphone array geometry
        if micarray == 'circular7':
            self._micarray = np.concatenate([np.zeros((1,3)), np.array([0.0425 * np.array([np.cos(i * np.pi/3), np.sin(i * np.pi/3), 0]) for i in range(6)])])  # 7x3 array
        elif micarray == 'mono':
            self._micarray = np.zeros((1,3))  # 1x3 array
        else:
            self._micarray = micarray

        print('Instantiating {}'.format(self.__class__.__name__))
        print('Sound velocity: {}'.format(self._sound_velocity))
        print('Sampling frequency: {}'.format(self._fs))

        print('Room dimension range (x): {}'.format(self._roomdim_range_x))
        print('Room dimension range (y): {}'.format(self._roomdim_range_y))
        print('Room dimension range (z): {}'.format(self._roomdim_range_z))

        print('Mic positioning scheme: {}'.format(self._micpos))

        if self._micpos == 'center':
            print('Max distance between room center and mic (x): {}'.format(self._roomcenter_mic_dist_max_x))
            print('Max distance between room center and mic (y): {}'.format(self._roomcenter_mic_dist_max_y))
            print('Mic position range (z): {}'.format(self._micpos_range_z))
        elif self._micpos == 'corner':
            print('Max distance between room corner and mic (x): {}'.format(self._corner_mic_dist_max_x))
            print('Max distance between room corner and mic (y): {}'.format(self._corner_mic_dist_max_y))
            print('Mic position range (z): {}'.format(self._micpos_range_z))


        print('Speaker-mic distance range (x): {}'.format(self._spkr_mic_dist_range_x))
        print('Speaker-mic distance range (y): {}'.format(self._spkr_mic_dist_range_y))
        print('Speaker-mic distance range (z): {}'.format(self._spkr_mic_dist_range_z))

        print('T60 range (z): {}'.format(self._t60_range))

        print('Minimum angle difference between two sources: {}'.format(self._min_angle_diff))
        print('Maximum angle difference between two sources: {}'.format(self._max_angle_diff))

        print('Mic array geometry: {}'.format(micarray))

        print('', flush=True)



    def __call__(self, nspeakers=2, info_as_display_style=False):
        success = False
        
        while not success:
            # Randomly sample room dimensions. 
            L = np.array([np.random.uniform(*self._roomdim_range_x), 
                          np.random.uniform(*self._roomdim_range_y), 
                          np.random.uniform(*self._roomdim_range_z)])

            # Randomly sample T60. 
            rt = np.random.uniform(*self._t60_range)
            rirlen = int(rt * self._fs)

            # validity check
            V = np.prod(L)
            S = 2 * (L[0]*L[2] + L[1]*L[2] + L[0]*L[1])
            alpha = 24 * V * np.log(10) / (self._sound_velocity * S * rt)
            if alpha < 1:
                success = True

        # Randomly sample a mic array location. 
        if self._micpos == 'center':
            room_center = L / 2
            r = np.array([np.random.uniform(room_center[0] - self._roomcenter_mic_dist_max_x, room_center[0] + self._roomcenter_mic_dist_max_x),
                          np.random.uniform(room_center[1] - self._roomcenter_mic_dist_max_y, room_center[1] + self._roomcenter_mic_dist_max_y),
                          np.random.uniform(*self._micpos_range_z)])
            r = np.maximum(r, 0)
            r = np.minimum(r, L)
            R = self._micarray + r

        elif self._micpos == 'corner':
            corner_x = 'origin' if np.random.choice([0, 1]) == 1 else 'end'
            corner_y = 'origin' if np.random.choice([0, 1]) == 1 else 'end'
            r = np.array([np.random.uniform(0.0425, self._corner_mic_dist_max_x) if corner_x == 'origin'
                          else np.random.uniform(L[0] - self._corner_mic_dist_max_x, L[0] - 0.0425), 
                          np.random.uniform(0.0425, self._corner_mic_dist_max_y) if corner_y == 'origin'
                          else np.random.uniform(L[1] - self._corner_mic_dist_max_y, L[1] - 0.0425), 
                          np.random.uniform(*self._micpos_range_z)])
            r = np.maximum(r, 0)
            r = np.minimum(r, L)
            R = self._micarray + r
        else:
            raise ValueError('micpos must be either center or corner: {}'.format(self._micpos))


        # Randomly sample an ellipse on which sources will be located. 
        ellipse_xaxis = np.random.uniform(*self._spkr_mic_dist_range_x)
        ellipse_yaxis = np.random.uniform(*self._spkr_mic_dist_range_y)

        # Randomly sample a base height. 
        base_height = np.random.uniform(*self._spkr_mic_dist_range_z)

        mic2src_vecs = []
        h = []
        spkr_locations = []
        for i in range(nspeakers):
            max_trials = 1000
            
            for trial in range(max_trials):
                # Randomly draw a speaker location.
                theta = np.random.uniform(0, 2 * np.pi)
                x_offset = ellipse_xaxis * np.cos(theta)
                y_offset = ellipse_yaxis * np.sin(theta)
                z_offset = base_height + np.random.uniform(-0.1, 0.1)  # allow small fluctuation in height

                if self._micpos == 'corner':
                    x_offset = np.abs(x_offset) if corner_x == 'origin' else -np.abs(x_offset)
                    y_offset = np.abs(y_offset) if corner_y == 'origin' else -np.abs(y_offset)

                s = np.array([r[0] + x_offset, r[1] + y_offset, r[2] + z_offset])
                s = np.maximum(s, 0)
                s = np.minimum(s, L)

                mic2src = s[:2] - r[:2]
                mic2src = mic2src / np.linalg.norm(mic2src)

                # Check if the direction of the new source is valid with respect to the previously generated ones. 
                valid = True
                for m2s in mic2src_vecs:
                    angle_diff = math.degrees(np.arccos(np.clip(np.dot(mic2src, m2s), -1, 1)))
                    if angle_diff < self._min_angle_diff:
                        valid = False
                    if angle_diff > self._max_angle_diff:
                        valid = False
                if valid:
                    break

            if not valid:
                raise RuntimeError('Failed to generate valid RIRs.')
            # print('Tried {} times.'.format(trial))

            mic2src_vecs.append(mic2src)

            angle = math.degrees(np.arctan2(s[1]-r[1], s[0]-r[0])) + 180
            dist_2d = np.linalg.norm(s[:2] - r[:2])
            dist_3d = np.linalg.norm(s - r)
            height = s[2] - r[2]
            
            h0 = np.array(pyrirgen.generateRir(L, s, R, soundVelocity=self._sound_velocity, fs=self._fs, reverbTime=rt, nSamples=rirlen))

            #import matplotlib.pyplot as plt
            #plt.figure()
            #plt.plot(h0[0])
            #plt.show()
       
            h.append(h0)
            spkr_locations.append([angle, dist_2d, dist_3d, height])

        # Print the simulated enviroment. 
        print('Room dimensions: [{:6.3f} m, {:6.3f} m, {:6.3f} m]'.format(L[0], L[1], L[2]))
        print('T60: {:6.3f} s'.format(rt))
        print('Mic-array: [{:6.3f} m, {:6.3f} m, {:6.3f} m]'.format(r[0], r[1], r[2]))
        
        for i in range(nspeakers):
            print('Speaker {}: [angle, distance from mic (2d), distance from mic (3d), height relative to mic] = [{:6.3f} deg, {:6.3f} m, {:6.3f} m, {:6.3f} m]'.format(i, spkr_locations[i][0], spkr_locations[i][1], spkr_locations[i][2], spkr_locations[i][3]))
        print('', flush=True)

        # return
        if info_as_display_style:
            info = [('t60', rt), ('angles', [l[0] for l in spkr_locations])]
            return h, info
        else:
            return h, rt, spkr_locations
