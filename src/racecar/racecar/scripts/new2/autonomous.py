#!/usr/bin/python
# ----------------
#

# Should I have start and kill functions?
# I need to relate the processing functions to the mode rather than the component.
class Autonomous:

    def __init__(self, vesc):


    def apply_control(self, speed, steeringAngle):
        self.drive_msg.speed = speed
        self.drive_msg.steering_angle = steeringAngle


    def stop(self):
        self.drive_msg.speed = 0


    def getCommands(self):
