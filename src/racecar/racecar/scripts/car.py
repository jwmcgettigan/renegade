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
#from polebending import Polebending
from parallel import Parallel
from orbit import Orbit
from serpentine import Serpentine
from parking import Parking
from avoiding import Avoiding
from lanecenter2 import LaneCenter

VERBOSE=False
DEBUG=False
RECORD=False

class Car:
    controlMode = [0, 0, 0, 0] # lineFollow, laneCenter, serpentine
    utilMode = [0]
    speed = 0

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

        self.serpentine = Serpentine("", False, -1, -2)
        self.lineFollow = LineFollow()
        self.laneCenter = LaneCenter((False, True), 0, False)

        #self.laneCenter = LaneCenter()
        #self.orbit = Orbit()
        #self.parallel = Parallel()
        #self.roundabout = Roundabout()

        #self.serpentine = Serpentine(self.vesc)
        """
        lineFollow = LineFollow(vesc)
        laneCenter = LaneCenter(vesc)
        polebending = Polebending(vesc)
        parallel = Parallel(vesc)
        roundabout = Roundabout(vesc)"""


    def controller(self, zed, lidar, vesc):
        #try:
        joyButtons = self.joy.getData().buttons
        self.setMode(joyButtons)
        if joyButtons[5]: # Autonomous Mode
            self.runMode(zed, lidar, vesc)
        else:
            self.serpentine.resetValues()
        #except:
            #print "You've got an error! (Controller probably can't connect.)"


    def setMode(self, buttons):
        if   buttons[0]: self.controlMode = [1, 0, 0, 0] # X      |
        elif buttons[1]: self.controlMode = [0, 1, 0, 0] # A      |
        elif buttons[2]: self.controlMode = [0, 0, 1, 0] # B      |
        elif buttons[3]: self.controlMode = [0, 0, 0, 1] # Y      |
        elif buttons[9]: self.utilMode    = [1]          # START  | ENABLE DISPLAY MODE (Independent from other modes)
        elif buttons[8]:                                 # BACK   | TURNS OFF ALL MODES
            self.controlMode = [0, 0, 0, 0]
            self.utilMode = [0]
            cv2.destroyAllWindows()
            self.speed = 0
        if buttons[6]:
            self.speed -= 0.05
            print "speed %f" % self.speed
        if buttons[7]:
            self.speed += 0.05
            print "speed %f" % self.speed


    def runMode(self, zed, lidar, vesc, DISPLAY=False):
        if self.utilMode[0]:
            DISPLAY = True
        if self.controlMode[0]: # X
            self.lineFollow.run(zed, vesc, DISPLAY)
        elif self.controlMode[1]: # A
            self.laneCenter.run(zed, lidar, vesc, DISPLAY)
            self.laneCenter.setSpeedMod(self.speed)
        elif self.controlMode[2]: # B
            self.serpentine.run(zed, lidar, vesc, DISPLAY)
        elif self.controlMode[3]: # Y
            pass


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
