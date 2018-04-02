#!/usr/bin/python
# ----------------
#

# Should I have start and kill functions?
# I need to relate the processing functions to the mode rather than the component.
class Autonomous(object):

    def __init__(self, vesc):
        self.driveMsg = vesc.getDriveMsg()


    def apply_control(self, speed, steeringAngle):
        self.driveMsg.speed = speed
        self.driveMsg.steering_angle = steeringAngle


    def stop(self):
        self.driveMsg.speed = 0


    def getCommands(self):
        pass
