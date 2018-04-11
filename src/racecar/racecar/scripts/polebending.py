#!/usr/bin/python
# ----------------
#

from mode import Mode
from cone import Cone
from serpentine import Serpentine
from parallel import Parallel
from roundabout import Roundabout
import cv2, numpy as np

DISPLAY=True

class Polebending(Mode):

    def __init__(self, zed, vesc):
        super(Polebending, self).__init__(vesc)
        #cv2.imshow('ZED', zed.getImage())
        self.process(zed.getImage())


    def control(self):

        Parallel() # part 1
        Roundabout() # part 2
        Serpentine() # part 3
        Roundabout() # part 4
        Serpentine() # part 5
        Roundabout() # part 6
        Parallel() # part 7
