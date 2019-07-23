#!/usr/bin/env python3

# author: James Jackson

import os
import time
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
        self.values['aux1'] =  1
        self.values['aux2'] = -1
        self.values['aux3'] = -1
        self.values['aux4'] = -1
        
        self.actions = dict()
        self.actions[pygame.K_UP]    = {'name':    'y', 'sign': -1, 'state': 0}
        self.actions[pygame.K_DOWN]  = {'name':    'y', 'sign':  1, 'state': 0}
        self.actions[pygame.K_LEFT]  = {'name':    'x', 'sign': -1, 'state': 0}
        self.actions[pygame.K_RIGHT] = {'name':    'x', 'sign':  1, 'state': 0}
        self.actions[pygame.K_w]     = {'name':    'F', 'sign':  1, 'state': 0}
        self.actions[pygame.K_s]     = {'name':    'F', 'sign': -1, 'state': 0}
        self.actions[pygame.K_a]     = {'name':    'z', 'sign': -1, 'state': 0}
        self.actions[pygame.K_d]     = {'name':    'z', 'sign':  1, 'state': 0}
        self.actions[pygame.K_o]     = {'name': 'aux1', 'sign':  1, 'state': 0}

        self.delta = 0.05  # amount per interval that axis values slide towards zero

        self.next_update_time = time.time()
        self.switch_wait_until_time = time.time()
        self.switch_interval_time = 0.25

    def update(self):

        if self.auto_arm and not self.init:
            self.values['F'] = -1
            self.values['z'] =  1
            return False
        
        pygame.event.pump()

        # 50 Hz update
        if time.time() > self.next_update_time:
            self.next_update_time += 0.02
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and event.key in self.actions:
                    name = self.actions[event.key]['name']
                    sign = self.actions[event.key]['sign']
                    t = time.time()
                    if name == 'aux1' and t > self.switch_wait_until_time:
                        self.values['aux1'] *= -1
                        self.switch_wait_until_time = t + self.switch_interval_time
                    elif name != 'aux1':
                        self.shift_value(name, sign)
                    elif event.key == pygame.K_q:
                        exit(0)
                    self.actions[event.key]['state'] = 1
                elif event.type == pygame.KEYUP and event.key in self.actions:
                    self.actions[event.key]['state'] = 0
            self.slide_to_zero(self.actions)
            return True
        else:
            return False

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
        
    def slide_to_zero(self, actions):
        ''' for x,y,z axes, push values closer to zero if not currently pressed 
            (joystick behavior)
        '''
        for n in ['x', 'y', 'z']:
            is_pressed = False
            for key in actions:
                if self.actions[key]['name'] == n and self.actions[key]['state']:
                    is_pressed = True
            if is_pressed:
                continue
                
            val = self.values[n]
            if abs(val) < 1e-6 and val != 0.:
                val = 0.
                if self.print_limits:
                    print('{} axis returned to 0'.format(n))
            elif val != 0.:
                val += self.delta if val < 0 else -self.delta
            self.values[n] = val
    
