####################################################################################################################
# IMPORTS
import pygame
import json

from pygame.key import ScancodeWrapper
from TelloMK2 import TelloMK2


# IN CV2 Colors are not defined in RGB but in BGR

####################################################################################################################
# CORE
class Cockpit:
    # ---> CONSTANTS
    TELLO_SPEED = 0.05

    # ---> CONSTRUCTOR
    def __init__(self, tello: TelloMK2):
        self._tello = tello
        self._key_pressed = None
        self._movement_list = []

        self._recording_path = False
        self._recorded_path = []

        with open("../res/kb_map.json", "r") as file:
            json_content = json.load(file)

            # Get Keyboard mapping from json file
            self.kb_map = json_content["kb_map"]
            file.close()

    # ---> FUNCTIONS
    def update_pressed(self, key_pressed: ScancodeWrapper):
        self._key_pressed = None
        self._key_pressed = key_pressed

    def if_key_pressed(self, key_name) -> bool:
        # Check if input keyboard has been pressed
        pressed = False

        my_key = getattr(pygame, 'K_{}'.format(key_name))
        if self._key_pressed[my_key]:
            pressed = True

        return pressed

    def get_movements(self) -> list[int]:
        """
            Returns an array which contains the movements based on keyboard input
                right_left = Right and Left YAW movement
                forward_backward = Forward and Backward movement
                up_down = Right and Left Clockwise Movement
                yaw_vel = Take-Off and Landing Movement

            Variable name is determined by documentation of
            send_rc_control function of Tello library
        """

        right_left, forward_backward, up_down, yaw_vel = 0, 0, 0, 0
        speed = 100

        move = self.kb_map["move"]

        # Right and Left YAW movement
        if self.if_key_pressed(move["right_yaw"]):
            right_left = speed
        elif self.if_key_pressed(move["left_yaw"]):
            right_left = -speed

        # Forward and Backward movement
        if self.if_key_pressed(move["forward"]):
            forward_backward = speed
        elif self.if_key_pressed(move["backward"]):
            forward_backward = -speed

        # Right and Left Clockwise Movement
        if self.if_key_pressed(move["right_clock"]):
            up_down = speed
        elif self.if_key_pressed(move["left_clock"]):
            up_down = -speed

        # Take-Off and Landing Movement
        if self.if_key_pressed(move["takeoff"]):
            yaw_vel = speed
        elif self.if_key_pressed(move["landing"]):
            yaw_vel = -speed

        movements = [right_left, forward_backward, up_down, yaw_vel]

        self._movement_list.append(movements)
        if self._recording_path:
            self._recorded_path.append(movements)

        return movements

    def exe_command(self) -> bool:
        """
            Executes command from keyboard
            -> Take-Off
            -> Landing
            -> Fly where you want
            -> Start/Stop Streaming
            -> Capture images saving on desktop
            -> Record Path and follows it
            -> Return Home
        """

        is_flying = True
        func = self.kb_map["func"]

        # --> Take-Off
        if self.if_key_pressed(func["takeoff"]):
            self._tello.start_streaming()
            self._tello.takeoff()

        # --> Landing
        if self.if_key_pressed(func["landing"]):
            self._tello.land()
            self._tello.stop_streaming()
            self._movement_list.clear()
            is_flying = False

        # --> Start/Stop Streaming
        if self.if_key_pressed(func["stream"]):
            if not self._tello.stream_on:
                self._tello.start_streaming()
            else:
                self._tello.stop_streaming()

        # --> Capture Image and Save on Desktop
        if self._tello.stream_on:
            img = self._tello.show_img(0, 0)
            if self.if_key_pressed(func["save_img"]):
                self._tello.save_img(img)

        # ### In Flying functions ### #
        if self._tello.is_flying:
            movement = self.get_movements()

            # --> Move Tello with keyboard
            self._tello.send_rc_controlx(movement[0],
                                         movement[1],
                                         movement[2],
                                         movement[3],
                                         self.TELLO_SPEED)

            # --> Start/Stop Recording Path
            if self.if_key_pressed(func["recording_path"]):
                self.switch_recording_path()

            # --> Tello will fly following recorded path
            if self.if_key_pressed(func["follow_path"]):
                self.follow_path()

            # --> Tello will come back following recorded path
            if self.if_key_pressed(func["return"]):
                self.return_home()

        return is_flying

    def emergency_landing(self):
        self._tello.land()
        self._tello.stop_streaming()
        self._movement_list.clear()

    def get_movement_list(self):
        return self._movement_list

    def switch_recording_path(self):
        if not self._recording_path:
            self._enable_recording_path()
            self._recorded_path.clear()
        else:
            self._disable_recording_path()

    def _enable_recording_path(self):
        self._recording_path = True

    def _disable_recording_path(self):
        self._recording_path = False

    def get_recorded_path(self):
        return self._recorded_path

    def follow_path(self):
        path = self.get_recorded_path()
        if not path:
            # TODO implement log
            pass
        else:
            self._disable_recording_path()
            for move in path:
                self._movement_list.append(move)
                self._tello.send_rc_controlx(move[0],
                                             move[1],
                                             move[2],
                                             move[3],
                                             self.TELLO_SPEED)
            # TODO implement emergency stop
            # TODO implement log
            self._recorded_path.clear()

    def return_home(self):
        path = self.get_movement_list()
        if not path:
            # TODO implement log
            pass
        else:

            # TODO implement emergency stop
            # TODO implement reversed path to follow

            for move in path:
                self._tello.send_rc_controlx(move[0],
                                             move[1],
                                             move[2],
                                             move[3],
                                             self.TELLO_SPEED)
            self._movement_list.clear()
