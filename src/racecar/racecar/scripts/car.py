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
from orbit import Orbit
from serpentine import Serpentine
from parking import Parking
from avoiding import Avoiding

VERBOSE=False
DEBUG=False
RECORD=False

class Car:
    mode = [0, 0, 0, 0], [0] # lineFollow, laneCenter, serpentine
    DISPLAY = False
    displayList = []
    serpentineValues = ["", False, -1, -2]

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

        self.laneCenter = LaneCenter()
        self.orbit = Orbit()
        self.parallel = Parallel()
        self.roundabout = Roundabout()

        #self.serpentine = Serpentine(self.vesc)
        """
        lineFollow = LineFollow(vesc)
        laneCenter = LaneCenter(vesc)
        polebending = Polebending(vesc)
        parallel = Parallel(vesc)
        roundabout = Roundabout(vesc)"""


    def controller(self, zed, lidar, vesc):
        joyButtons = self.joy.getData().buttons
        #self.serpentine.run(zed, lidar, self.DISPLAY)
        #Serpentine(zed, lidar, vesc, self.DISPLAY, self.distanceOffsetction)
        self.setMode(joyButtons)
        if joyButtons[5]: # Autonomous Mode
            self.runMode(zed, lidar, vesc)
        else:
            self.serpentine.resetValues()

        """
        if joyButtons[5]: # Autonomous Mode

            #
            if self.mode[1][0]: # START
                self.DISPLAY = True
            else:
                cv2.destroyAllWindows()
                self.DISPLAY = False
                """
                """
                self.displayList.append(1)
                if len(self.displayList) > 3:
                    cv2.destroyAllWindows()
                    self.DISPLAY = not self.DISPLAY
                    self.displayList = []
                """
            """
            if self.mode[0][0]: # X
                #LineFollow(zed, vesc, self.DISPLAY)
                Avoiding(zed, lidar, vesc, self.DISPLAY)
            elif self.mode[0][1]: # A
                Parking(zed, lidar, vesc, self.DISPLAY)
                #LaneCenter(lidar, vesc)
                pass
            elif self.mode[0][2]: # B
                #Polebending(zed, vesc)
                #Parallel(zed, lidar, vesc)
                serpentine = Serpentine(zed, lidar, vesc, self.DISPLAY, self.serpentineValues)
                self.serpentineValues[0] = serpentine.getLastDirection()
                self.serpentineValues[1] = serpentine.getLastOrbit()
                self.serpentineValues[2] = serpentine.getCount()
                self.serpentineValues[3] = serpentine.getNumberOfCones()
                # self.serpentine.run(zed, lidar, self.DISPLAY)
                #Roundabout(zed, lidar, vesc)
            elif self.mode[0][3]: # Y
                Parallel(zed, lidar, vesc, self.DISPLAY)
        else:
            self.serpentineValues = ["", False, -1, -2]
        """


    def setMode(self, buttons):
        if   buttons[0]: self.mode[0] = [1, 0, 0, 0] # X      |
        elif buttons[1]: self.mode[0] = [0, 1, 0, 0] # A      |
        elif buttons[2]: self.mode[0] = [0, 0, 1, 0] # B      |
        elif buttons[3]: self.mode[0] = [0, 0, 0, 1] # Y      |
        elif buttons[9]: self.mode[1] = [1]          # START  | ENABLE DISPLAY MODE (Independent from other modes)
        elif buttons[8]: self.mode = [0, 0, 0, 0], [0] # BACK | TURNS OFF ALL MODES


    def runMode(self, zed, lidar, vesc):
        if self.mode[0][0]: # X
            self.lineFollow.run(zed, vesc, DISPLAY)
        elif self.mode[0][1]: # A
            pass
        elif self.mode[0][2]: # B
            self.serpentine.run(zed, lidar, vesc, self.DISPLAY)
        elif self.mode[0][3]: # Y
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
