####################################################################################################################
# IMPORTS
import logging
import os
import time
from typing import Any

import cv2  # If not working, add the path manually to the interpreter

# from djitellopy import tello
from DJITelloPy.djitellopy import tello
from time import sleep
from win32api import GetSystemMetrics

from PyUtils.Logging.ZAGLogger import ZAGLogger


####################################################################################################################
# CORE
class TelloMK1(tello.Tello):
    """
        This class adds some utils such as a custom logger
        and some parameters to simplify basic movement

        For more detailed documentation, see the original class djitellopy.tello class
    """

    # ---> CONSTANTS
    CRITICAL_BATTERY = 15
    WARNING_BATTERY = 35
    LOG_NAME = "TELLO_PLUS"

    # ---> CONSTRUCTOR
    def __init__(self):

        # Logger init
        self._logx = ZAGLogger(self.LOG_NAME, write_file=True)

        # Create a Tello instance and connect it to the drone
        self._logx.print_log(logging.INFO, "Initialization...")
        super().__init__()

        try:
            self._logx.print_log(logging.INFO, "Connecting to Tello...")
            self.connect()
        except Exception:
            self._logx.print_log(logging.CRITICAL, "Connection refused")
            raise Exception()

        if self.get_battery() > 0:
            self._logx.print_log(logging.INFO, "Successfully connected!")
        else:
            self._logx.print_log(logging.ERROR, "Connection refused")
            raise Exception()

        # Check if drone is ready to Take-Off
        self._logx.print_log(logging.INFO, "Battery Level:" + str(self.get_battery()))
        if self.get_battery() >= TelloMK1.CRITICAL_BATTERY:
            if self.get_battery() <= TelloMK1.WARNING_BATTERY:
                self._logx.print_log(logging.WARNING, "Low Battery Level")
            self._logx.print_log(logging.INFO, "Ready to fly!")

        else:
            self._logx.print_log(logging.ERROR, "Battery level too low: unable to Take-Off")
            raise Exception()

    # ---> FUNCTIONS
    def send_rc_controlx(self,
                         left_right_velocity: int,
                         forward_backward_velocity: int,
                         up_down_velocity: int,
                         yaw_velocity: int,
                         sleep_time: float):
        """
            Flying movement with the addiction of a time interval ( overloading base method )
            It will check also battery level, starting emergency landing if it is too low
        """

        super().send_rc_control(left_right_velocity,
                                forward_backward_velocity,
                                yaw_velocity,
                                up_down_velocity)
        if sleep_time > 0:
            sleep(sleep_time)

        if left_right_velocity != 0 or forward_backward_velocity != 0 or yaw_velocity != 0 or up_down_velocity != 0:
            log_msg = "Movement -> |"
            log_msg = log_msg + f'left_right: {left_right_velocity} |'
            log_msg = log_msg + f'forward_backward: {forward_backward_velocity} |'
            log_msg = log_msg + f'yaw: {yaw_velocity} |'
            log_msg = log_msg + f'up_down: {up_down_velocity} |'
            log_msg = log_msg + f'sleep: {sleep_time} |'

            self._logx.print_log(logging.DEBUG, log_msg)

        if self.get_battery() < self.CRITICAL_BATTERY:
            self._logx.print_log(logging.CRITICAL, "Battery level too low: Starting Emergency Landing")
            self.land()
            raise Exception()

    def takeoff(self):
        """
            Start Take-Off with the addiction of a waiting interval of 2 secs.
            In this way, the drone will takes-off avoiding unwanted movements
        """

        self._logx.print_log(logging.INFO, "Starting Take-Off")

        super().takeoff()
        self.send_rc_controlx(0, 0, 0, 0, 2)

        self._logx.print_log(logging.INFO, "Take-Off completed")

    def land(self):
        """
            Start landing with the addiction of a waiting interval of 2 secs.
            In this way, the drone will land avoiding unwanted movements
        """

        self._logx.print_log(logging.INFO, "Starting Landing")

        self.send_rc_controlx(0, 0, 0, 0, 2)
        super().land()

        self._logx.print_log(logging.INFO, "Landing completed")

    def start_streaming(self):
        if not self.stream_on:
            self.streamon()
            sleep(0.3)
            self._logx.print_log(logging.INFO, "Streaming: ON")
        else:
            self._logx.print_log(logging.WARNING, "Streaming already ON")

    def stop_streaming(self):
        if self.stream_on:
            self.streamoff()
            sleep(0.3)
            self._logx.print_log(logging.INFO, "Streaming: OFF")
        else:
            self._logx.print_log(logging.WARNING, "Streaming already OFF")

    def get_img(self) -> Any | None:
        """
            Returns the frame captured by tello.
        """
        img = None
        if self.stream_on:
            img = self.get_frame_read().frame

        return img

    def show_img(self, resize_x: int, resize_y: int) -> Any | None:
        """
            It will show with CV2 the captured frame on you screen.
            If resize params are given, the image will be resized
                for example 720 x 480.
            If zero is passed, it will use the half of resolution of your screen
        """
        img = self.get_img()
        if img is None:
            return img

        width = int(GetSystemMetrics(0) / 2)
        height = int(GetSystemMetrics(1) / 2)

        if resize_x > 0:
            width = resize_x

        if resize_y > 0:
            height = resize_y

        resized_img = cv2.resize(img, (width, height))

        cv2.imshow("Tello Frame", resized_img)
        cv2.waitKey(1)

        return img

    def save_img(self, img):
        """
            Save image on your desktop
        """

        if img is None:
            self._logx.print_log(logging.ERROR, "Unable to save Img. No frame captured")
            return

        img_name = f'\\{time.time()}.jpg'
        out_path = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
        out_path = out_path + '\\TelloCaptures'
        if not os.path.isdir(out_path):
            os.makedirs(out_path)

        out_path = out_path + img_name

        cv2.imwrite(out_path, img)
        time.sleep(0.3)

        log_msg = "Frame captured: " + out_path
        self._logx.print_log(logging.INFO, log_msg)

    def get_log_entries(self):
        return self._logx.get_log_entries()
