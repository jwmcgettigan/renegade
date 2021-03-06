#!/usr/bin/python
# ----------------
# this file interacts with all of its components
# instantiates lidar, zed, and vesc

import rospy as rp
from zed import Zed
from lidar import Lidar
from vesc import Vesc
import joy
import autonomous as auto

VERBOSE=False
DEBUG=False
DISPLAY=False
RECORD=False

class Car:

    def __init__(self):
        #rp.init_node("car", anonymous=True)
        joyData = joy.Joy().getData()
        vesc = Vesc()
        zed = Zed()
        lidar = Lidar()
        # Need to implement a way to kill a mode when a new one is activated.
        if joyData.buttons[1]: #A
            mode = auto.LineFollow(zed)
        elif joyData.buttons[2]: #B
            mode = auto.LaneCenter(lidar)
        elif joyData.buttons[3]: #X
            mode = auto.Serpentine(zed, lidar)



if __name__ == '__main__':
    renegade = Car()
    try:
        rp.spin()
    except KeyboardInterrupt:
        pass
    cv2.destroyAllWindows()
