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
from sensor_msgs.msg import Image, LaserScan, Joy as JoyMsg

VERBOSE=False
DEBUG=False
DISPLAY=False
RECORD=False

class Car:
    mode = [0, 0, 0, 0] # lineFollow, laneCenter, serpentine

    def __init__(self):
        rp.init_node("car", anonymous=True)
        self.joy = Joy()
        self.zed = Zed()
        self.lidar = Lidar()
        self.vesc = Vesc()
        rp.Subscriber("vesc/joy", JoyMsg, self.joy_callback)
        rp.Subscriber("zed/normal", Image, self.zed_callback)
        rp.Subscriber("scan", LaserScan, self.lidar_callback)


    def controller(self, zed, vesc):
        joyData = self.joy.getData()
        print self.mode
        if joyData.buttons[5]: # Autonomous Mode
            if   joyData.buttons[0]: self.mode = [1, 0, 0, 0] # X
            elif joyData.buttons[1]: self.mode = [0, 1, 0, 0] # A
            elif joyData.buttons[2]: self.mode = [0, 0, 1, 0] # B
            elif joyData.buttons[3]: self.mode = [0, 0, 0, 1] # Y
            elif joyData.buttons[8]: self.mode = [0, 0, 0, 0] # BACK

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


    def lidar_callback(self, data):
        self.lidar.setData(data)


if __name__ == '__main__':
    renegade = Car()
    try:
        rp.spin()
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
