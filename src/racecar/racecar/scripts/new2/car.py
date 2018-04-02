#!/usr/bin/python
# ----------------
# this file interacts with all of its components
# instantiates lidar, zed, and vesc

import cv2, rospy as rp
from zed import Zed
from lidar import Lidar
from vesc import Vesc
from joy import Joy
import autonomous as auto
from linefollow import LineFollow
from sensor_msgs.msg import Image, Joy as JoyMsg

VERBOSE=False
DEBUG=False
DISPLAY=False
RECORD=False

class Car:
    mode = [0, 0, 0] # lineFollow, laneCenter, serpentine

    def __init__(self):
        rp.init_node("car", anonymous=True)
        """joy = joy.getJoy()
        joyData = joy.getData()
        joyData = Joy().getData()"""
        self.joy = Joy()
        self.zed = Zed()
        self.vesc = Vesc()
        rp.Subscriber("vesc/joy", JoyMsg, self.joy_callback)
        rp.Subscriber("zed/cropped", Image, self.zed_callback)
        #lidar = Lidar()
        # Need to implement a way to kill a mode when a new one is activated.


    def controller(self, zed, vesc):
        joyData = self.joy.getData()
        print self.mode
        if joyData.buttons[5]: # Autonomous Mode
            if joyData.buttons[1]: # A
                self.mode = [1, 0, 0]
            elif joyData.buttons[2]: # B
                self.mode = [0, 1, 0]
            elif joyData.buttons[0]: # X
                self.mode = [0, 0, 1]

            if self.mode[0]:
                LineFollow(zed, vesc)
            elif self.mode[1]:
                #LaneCenter(lidar, vesc)
                pass
            elif self.mode[2]:
                #Serpentine(zed, lidar, vesc)
                pass


    def joy_callback(self, data):
        self.joy.setData(data)


    def zed_callback(self, data):
        self.zed.setImage(data)
        self.controller(self.zed, self.vesc)


if __name__ == '__main__':
    renegade = Car()
    try:
        rp.spin()
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
