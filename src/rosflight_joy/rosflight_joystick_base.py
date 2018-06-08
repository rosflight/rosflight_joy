#!/usr/bin/python

# author: James Jackson

import os
import time
import pygame


class rosflight_joystick_base():
    def __init__(self, device=0):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.init()
        screen = pygame.display.set_mode((1,1))
        pygame.joystick.init()
        
        self.joy = pygame.joystick.Joystick(device)
        self.joy.init()

        print "joystick: {} (axes: {}, buttons: {}, hats: {})".format(
            self.joy.get_name(), self.joy.get_numaxes(), self.joy.get_numbuttons(), self.joy.get_numhats())

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
            self.mapping['aux2'] = {'type': 'axis', 'id': 5}
            self.mapping['aux3'] = {'type': 'axis', 'id': 6}
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

        elif 'Extreme 3D' in self.joy.get_name():
            print "found Logitech Extreme 3D"
            self.mapping['x'] = 0
            self.mapping['y'] = 1
            self.mapping['z'] = 2
            self.mapping['F'] = 3
            self.mapping['xsign'] = 1
            self.mapping['ysign'] = 1
            self.mapping['zsign'] = 1
            self.mapping['Fsign'] = -1
            self.mapping['aux1'] = {'type': 'button', 'id': 0}
            self.mapping['aux2'] = {'type': 'button', 'id': 1}
            self.mapping['aux3'] = {'type': 'button', 'id': 2}
            self.mapping['aux4'] = {'type': 'button', 'id': 3}
            # the Extreme 3D has actually 12 buttons, but rc_joy forwards only 4 aux keys
            self.look_for_button_press_events = True

        else:
            print "using realflight mapping"
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
            # get keys for all inputs typed as 'button'
            self.button_keys = [key for key in self.mapping.iterkeys()
                                if 'aux' in key and self.mapping[key]['type'] == 'button']
            # initialize values for the buttons
            self.prev_button_values = []
            for key in self.button_keys:
                button_value = self.joy.get_button(self.mapping[key]['id'])
                self.prev_button_values.append(button_value)
                self.mapping[key]['value'] = button_value

    def update(self):
        pygame.event.pump()

        # Look for button press events in the case of a joystick controller
        # (switch value on button press)
        if self.look_for_button_press_events:
            # get values for the buttons
            current_button_values = [self.joy.get_button(self.mapping[key]['id']) for key in self.button_keys]

            for (current, prev, key) in zip(current_button_values,
                                            self.prev_button_values,
                                            self.button_keys):
                if current != prev and current == 1:
                    self.values[key] = -1 * self.values[key]
                    # print "button action: key:",key, "id:",self.mapping[key]['id'], "toggle-state:",self.values[key]

            # Note that storing the values as a plain, key-less list between loops does only work if the
            # self.mapping dict is not modified at all. std-dict iterates in arbitrary order.
            self.prev_button_values = current_button_values

        # For 'switch' type aux keys, the published value is directly the current state of being pressed.
        # Updated in below loop. Same for 'axis' type aux keys.

        # 50 Hz update
        if time.time() > self.next_update_time:
            self.next_update_time += 0.02

            self.values['x'] = self.joy.get_axis(self.mapping['x']) * self.mapping['xsign']
            self.values['y'] = self.joy.get_axis(self.mapping['y']) * self.mapping['ysign']
            self.values['F'] = self.joy.get_axis(self.mapping['F']) * self.mapping['Fsign']
            self.values['z'] = self.joy.get_axis(self.mapping['z']) * self.mapping['zsign']

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
