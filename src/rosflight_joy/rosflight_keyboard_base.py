#!/usr/bin/env python

# author: Seth Nielsen and James Jackson

from __future__ import print_function
import os
import sys
import time
import numpy as np
import pygame


class rosflight_keyboard_base():
    def __init__(self, device=0):
        os.environ["SDL_VIDEODRIVER"] = "x11"
        pygame.display.init()
        screen = pygame.display.set_mode((1, 1))
        pygame.key.set_repeat(1, 10)

        print("pygame with keyboard control")

        self.mapping = dict()

        self.print_limits = False
        self.limit_reached = False
        
        self.auto_arm = False
        self.is_armed = False
        self.init = False

        self.values = dict()
        self.values['x'] = 0
        self.values['y'] = 0
        self.values['F'] = 0
        self.values['z'] = 0
        self.values['aux1'] = 1
        self.values['aux2'] = -1
        self.values['aux3'] = -1
        self.values['aux4'] = -1
        
        dtypes = [('id', int), ('name', object), ('sign', int)]
        self.actions = np.array([
            (pygame.K_UP,    'y', -1),
            (pygame.K_DOWN,  'y',  1),
            (pygame.K_LEFT,  'x', -1),
            (pygame.K_RIGHT, 'x',  1),
            (pygame.K_w,     'F',  1),
            (pygame.K_s,     'F', -1),
            (pygame.K_a,     'z', -1),
            (pygame.K_d,     'z',  1),
            (pygame.K_o,  'aux1',  1)
        ], dtypes)

        self.delta = 0.05  # amount per interval that axis values slide towards zero

        self.next_update_time = time.time()
        self.switch_wait_until_time = time.time()
        self.switch_interval_time = 0.25

    def update(self):

        if not self.init and self.auto_arm:
            self.values['F'] = -1
            self.values['z'] =  1
            if self.is_armed:
                self.values['F'] = 0
                self.values['z'] =  0
                self.values['aux1'] = -1
                self.init = True
            return
        
        pygame.event.pump()

        # 50 Hz update
        if time.time() > self.next_update_time:
            self.next_update_time += 0.02
            keys = np.array(pygame.key.get_pressed())
            keys = np.nonzero(keys[:300])[0]  # keys 300+ aren't needed (alt, super, etc)
            if keys.size > 0:
                for key in keys:
                    if key in self.actions['id']:
                        name = self.actions[self.actions['id']==key]['name'][0]
                        sign = self.actions[self.actions['id']==key]['sign'][0]
                        t = time.time()
                        if name == 'aux1' and t > self.switch_wait_until_time:
                            self.values['aux1'] *= -1
                            self.switch_wait_until_time = t + self.switch_interval_time
                        elif name != 'aux1':
                            self.shift_value(name, sign)
                        elif key == pygame.K_q:
                            self.quit()
            self.slide_to_zero(keys)

    def get_value(self, key):
        return self.values[key]

    def shift_value(self, name, sign):
        ''' increment or decrement value of axis [name] in [sign] direction'''
        self.values[name] += sign * self.delta
        val = self.values[name]
        if abs(val) >= 1.0:
            val = 1.0 if val > 0 else -1.0
            if not self.limit_reached and self.print_limits:
                print('{} {} value reached'.format(name, 
                                            'max' if val > 0 else 'min'))
                self.limit_reached = True
        else:
            self.limit_reached = False

        if abs(val) < 1e-6:
            val = 0.
        self.values[name] = val
        
    def slide_to_zero(self, keys):
        ''' for x,y,z axes, push values closer to zero if not currently pressed 
            (joystick behavior)
        '''
        for n in ['x', 'y', 'z']:
            is_pressed = False
            for key in keys:
                if key in self.actions[self.actions['name']==n]['id']:
                    is_pressed = True
            if is_pressed:
                continue
                
            val = self.values[n]
            if abs(val) < 1e-6 and val != 0.:
                val = 0.
            elif val != 0.:
                val += self.delta if val < 0 else -self.delta
            self.values[n] = val
    
    def quit(self):
        pygame.quit()
        sys.exit(0)
