#!/usr/bin/python
# ----------------
# this file interacts with all of its components
# instantiates lidar, zed, and vesc

import cv2, rospy as rp

from sensor_msgs.msg import Image, LaserScan, Joy as JoyMsg
from zed import Zed
from lidar import Lidar
from vesc import Vesc
from joy import Joy

from linefollow import LineFollow
from polebending import Polebending
from parallel import Parallel
from roundabout import Roundabout
from serpentine import Serpentine

VERBOSE=False
DEBUG=False
RECORD=False

class Car:
    mode = [0, 0, 0, 0] # lineFollow, laneCenter, serpentine
    DISPLAY = False
    displayList = []

    def __init__(self):
        """Initialize the components of the car."""
        rp.init_node("car", anonymous=True)
        self.joy = Joy()
        self.zed = Zed()
        self.lidar = Lidar()
        self.vesc = Vesc()

        rp.Subscriber("vesc/joy", JoyMsg, self.joy_callback)
        rp.Subscriber("zed/normal", Image, self.zed_callback)
        rp.Subscriber("scan", LaserScan, self.lidar_callback)

        """
        lineFollow = LineFollow(vesc)
        laneCenter = LaneCenter(vesc)
        polebending = Polebending(vesc)
        parallel = Parallel(vesc)
        roundabout = Roundabout(vesc)"""


    def controller(self, zed, lidar, vesc):
        joyData = self.joy.getData()
        #Serpentine(zed, lidar, vesc, self.DISPLAY)
        if joyData.buttons[5]: # Autonomous Mode
            if   joyData.buttons[0]: self.mode = [1, 0, 0, 0] # X
            elif joyData.buttons[1]: self.mode = [0, 1, 0, 0] # A
            elif joyData.buttons[2]: self.mode = [0, 0, 1, 0] # B
            elif joyData.buttons[3]: self.mode = [0, 0, 0, 1] # Y
            elif joyData.buttons[8]: self.mode = [0, 0, 0, 0] # BACK

            if joyData.buttons[9]: # START
                self.displayList.append(1)
                if len(self.displayList) > 3:
                    cv2.destroyAllWindows()
                    self.DISPLAY = not self.DISPLAY
                    self.displayList = []


            if self.mode[0]:
                LineFollow(zed, vesc, self.DISPLAY)
            elif self.mode[1]:
                #LaneCenter(lidar, vesc)
                pass
            elif self.mode[2]:
                #Polebending(zed, vesc)
                #Parallel(zed, lidar, vesc)
                Serpentine(zed, lidar, vesc, self.DISPLAY)
                #Roundabout(zed, lidar, vesc)


    def joy_callback(self, data):
        self.joy.setData(data)


    def zed_callback(self, data):
        self.zed.setImage(data)
        self.controller(self.zed, self.lidar, self.vesc)


    def lidar_callback(self, data):
        self.lidar.setData(data)


if __name__ == '__main__':
    renegade = Car()
    try:
        rp.spin()
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
