#!/usr/bin/python
# ----------------
#

from mode import Mode

class Parallel(Mode):

    def __init__(self, zed, lidar, vesc):
        super(Serpentine, self).__init__(vesc)
        self.process(zed.getImage())


    def process(self, image):
        pass
