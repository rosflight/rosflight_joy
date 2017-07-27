#!/usr/bin/python

# author: James Jackson

import time
import pygame
import re

class rosflight_joystick_base():
    def __init__(self, device = 0):
        pygame.display.init()
        pygame.joystick.init()

        self.joy = pygame.joystick.Joystick(device)
        self.joy.init()

        print "joystick:", self.joy.get_name()

        self.mapping = dict()

        self.look_for_button_press_events = False

        self.values = dict()
        self.values['x'] = 0
        self.values['y'] = 0
        self.values['F'] = 0
        self.values['z'] = 0
        self.values['aux1'] = -1
        self.values['aux2'] = -1
        self.values['aux3'] = -1
        self.values['aux4'] = -1

        self.next_update_time = time.time()

        if 'Taranis' in self.joy.get_name():
            print "found Taranis"
            self.mapping['x'] = 0
            self.mapping['y'] = 1
            self.mapping['z'] = 3
            self.mapping['F'] = 2
            self.mapping['xsign'] = 1
            self.mapping['ysign'] = 1
            self.mapping['zsign'] = 1
            self.mapping['Fsign'] = 1
            self.mapping['aux1'] = {'type': 'axis', 'id': 4}
            self.mapping['aux2'] = {'type': 'switch', 'id': 0}
            self.mapping['aux3'] = {'type': 'switch', 'id': 1}
            self.mapping['aux4'] = {'type': 'switch', 'id': 2}
        elif 'Xbox' in self.joy.get_name() or 'X-Box' in self.joy.get_name():
            print "found xbox"
            self.mapping['x'] = 3
            self.mapping['y'] = 4
            self.mapping['z'] = 0
            self.mapping['F'] = 1
            self.mapping['xsign'] = 1
            self.mapping['ysign'] = 1
            self.mapping['zsign'] = 1
            self.mapping['Fsign'] = -1
            self.mapping['aux1'] = {'type': 'button', 'id': 0}
            self.mapping['aux2'] = {'type': 'button', 'id': 1}
            self.mapping['aux3'] = {'type': 'button', 'id': 2}
            self.mapping['aux4'] = {'type': 'button', 'id': 3}
            self.look_for_button_press_events = True
        else:
            print "using realflght mapping"
            self.mapping['x'] = 1
            self.mapping['y'] = 2
            self.mapping['z'] = 4
            self.mapping['F'] = 0
            self.mapping['xsign'] = 1
            self.mapping['ysign'] = 1
            self.mapping['zsign'] = 1
            self.mapping['Fsign'] = 1
            self.mapping['aux1'] = {'type': 'axis', 'id': 3}
            self.mapping['aux2'] = {'type': 'switch', 'id': 0}
            self.mapping['aux3'] = {'type': 'switch', 'id': 1}
            self.mapping['aux4'] = {'type': 'switch', 'id': 2}

        if self.look_for_button_press_events:
            self.prev_button_values = []
            for key in self.mapping.iterkeys():
                if 'aux' in key and self.mapping[key]['type'] == 'button':
                    self.prev_button_values.append(self.joy.get_button(self.mapping[key]['id']))
                    self.mapping[key]['value'] = self.joy.get_button(self.mapping[key]['id'])

    def update(self):
        pygame.event.pump()

        # Look for button press events in the case of a joystick controller
        # (switch value on button press)
        if self.look_for_button_press_events:
            current_button_values = []
            for key in self.mapping.iterkeys():
                if 'aux' in key and self.mapping[key]['type'] == 'button':
                    current_button_values.append(self.joy.get_button(self.mapping[key]['id']))

            for (current, prev, key) in zip(current_button_values,
                                            self.prev_button_values,
                                            ['aux1', 'aux2', 'aux3', 'aux4']):
                if current != prev and current == 1:
                    self.values[key] = -1*self.values[key]
            self.prev_button_values = current_button_values


        # 50 Hz update
        if time.time() > self.next_update_time:
            self.next_update_time += 0.02

            self.values['x'] = self.joy.get_axis(self.mapping['x']) * self.mapping['xsign']
            self.values['y'] = self.joy.get_axis(self.mapping['y']) * self.mapping['ysign']
            self.values['F'] = self.joy.get_axis(self.mapping['F']) * self.mapping['Fsign']
            self.values['z'] = self.joy.get_axis(self.mapping['z']) * self.mapping['zsign']

            print "\nupdate"
            for key, item in self.values.iteritems():
                print key, ":", item


            for key in ['aux1', 'aux2', 'aux3', 'aux4']:
                if self.mapping[key]['type'] == 'axis':
                    self.values[key] = self.joy.get_axis(self.mapping[key]['id'])
                elif self.mapping[key]['type'] == 'switch':
                    self.values[key] = 2.0 * self.joy.get_button(self.mapping[key]['id']) - 1.0
            return True
        else:
            return False

    def get_value(self, key):
        return self.values[key]
