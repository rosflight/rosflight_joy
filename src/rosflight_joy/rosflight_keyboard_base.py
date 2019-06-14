#!/usr/bin/env python3

# author: James Jackson

import os
import time
import pygame


class rosflight_keyboard_base():
    def __init__(self, device=0):
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.display.init()
        screen = pygame.display.set_mode((100, 100))

        print("pygame with keyboard control")

        self.mapping = dict()

        self.look_for_button_press_events = False
        self.keypress = False

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

        self.mapping['x'] = 1  # R - L/R
        self.mapping['y'] = 2  # R - U/D
        self.mapping['z'] = 3  # L - L/R
        self.mapping['F'] = 0  # L - U/D
        self.mapping['xsign'] = 1
        self.mapping['ysign'] = -1
        self.mapping['zsign'] = 1
        self.mapping['Fsign'] = 1
        self.mapping['aux1'] = {'type': 'axis', 'id': 4}
        self.mapping['aux2'] = {'type': 'axis', 'id': 5}
        self.mapping['aux3'] = {'type': 'axis', 'id': 6}
        self.mapping['aux4'] = {'type': 'switch', 'id': 2}

        self.keys_increase = [pygame.K_RIGHT, pygame.K_UP, pygame.K_d, pygame.K_w]

        self.keys_decrease = [pygame.K_LEFT, pygame.K_DOWN, pygame.K_a, pygame.K_s, pygame.K_o]

        if self.look_for_button_press_events:
            # get keys for all inputs typed as 'button'
            self.button_keys = [key for key in self.mapping.iterkeys()
                                if 'aux' in key and self.mapping[key]['type'] == 'button']
            # initialize values for the buttons
            self.prev_button_values = []
            for key in self.button_keys:
                button_value = self.joy.get_button(self.mapping[key]['id'])
                self.prev_button_values.append(button_value)

    def update(self):
        pygame.event.pump()

        # Look for button press events in the case of a joystick controller
        # (switch value on button press)
        if self.look_for_button_press_events:
            # get values for the buttons
            current_button_values = [self.joy.get_button(
                self.mapping[key]['id']) for key in self.button_keys]

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

        
                # self.keypress = True

        # 50 Hz update
        if time.time() > self.next_update_time:
            self.next_update_time += 0.02


            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_DOWN:
                        print("Pressing down!")
                if event.type == pygame.KEYUP:
                    print('\nkey up: {}, {}\n'.format(event.key, pygame.key.name(event.key)))

            self.values['x'] = self.mapping['xsign']
            self.values['y'] = self.mapping['ysign']
            self.values['F'] = self.mapping['Fsign']
            self.values['z'] = self.mapping['zsign']


            for key in ['aux1', 'aux2', 'aux3', 'aux4']:
                if self.mapping[key]['type'] == 'axis':
                    self.values[key] = 10
                    # self.values[key] = self.joy.get_axis(
                        # self.mapping[key]['id'])
                elif self.mapping[key]['type'] == 'switch':
                    self.values[key] = 1
                    # self.values[key] = 2.0 * \
                    #     self.joy.get_button(self.mapping[key]['id']) - 1.0

            self.keypress = False
            return True
        else:
            return False

    def get_value(self, key):
        return self.values[key]
