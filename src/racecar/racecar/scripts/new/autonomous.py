#!/usr/bin/python
# ----------------
#

from zed import Utility as zedUtil
from lidar import Utility as lidarUtil

# Should I have start and kill functions?
# I need to relate the processing functions to the mode rather than the component.
class Autonomous:

    def __init__(self):


    def apply_control(self, speed, steeringAngle):
        self.drive_msg.speed = speed
        self.drive_msg.steering_angle = steeringAngle


    def stop(self):
        self.drive_msg.speed = 0


class LineFollow(Autonomous):

    def __init__(self, zed):
        self.logic(self.controller(zed.getProccessedData()))


    def controller(self, leftSlope, rightSlope, linesExist, firstLinesSeen):
        direction = ""
        error = leftSlope + rightSlope # sum of slopes
        steeringAngle = self.pid(error, (0.3/2.5), 0, 0)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.02: direction = "Left"
        elif steeringAngle < -0.02: direction = "Right"
        else: direction = "Center"
        speedLimit = 0.6
        speedPower = 1.13678
        speed = speedLimit * (1 - abs(steeringAngle))**speedPower
        if DEBUG and firstLinesSeen:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "Direction:\t "       +                                                 direction
            print "Steering Angle:\t"   + (' ' if steeringAngle > 0 else '')   + "%.4f" % steeringAngle
            print "Speed:\t\t"          + (' ' if speed > 0 else '')           + "%.4f" % speed
            print "\nError:\t\t"        + (' ' if error > 0 else '')           + "%.4f" % error
            print "Left Slope\t"        + (' ' if leftSlope > 0 else '')       + "%.4f" % leftSlope
            print "Right Slope:\t"      + (' ' if rightSlope > 0 else '')      + "%.4f" % rightSlope
        self.zedData = [speed, steeringAngle, linesExist]


    def logic(self, speed, steeringAngle, linesExist):
        if linesExist:
            self.apply_control(speed, steeringAngle)
        else:
            self.apply_control(1, 0)



class LaneCenter(Autonomous):

    def __init__(self, lidar):
        self.logic(self.controller(lidar.getProccessedData()))


    def controller(self):
        direction = ""
        wallOffsetWeight = 2
        forwardOffsetWeight = 3
        slopeWeight = 4
        maxTurningAngle = 0.3
        slopeLimit = 30
        inchToMeter = 0.0254

        slope *= (maxTurningAngle/slopeLimit)
        wallOffset *= (maxTurningAngle/(12*inchToMeter))
        forwardOffset *= (maxTurningAngle/(12*inchToMeter))
        error = ((slopeWeight*slope) + (wallOffsetWeight*wallOffset) + (forwardOffsetWeight*forwardOffset))/(wallOffsetWeight+forwardOffsetWeight+slopeWeight)

        steeringAngle = self.pid(error, 1, 0, 0)
        if steeringAngle > 0.3: steeringAngle = 0.3
        if steeringAngle < -0.3: steeringAngle = -0.3
        if steeringAngle > 0.05: direction = "Left"
        elif steeringAngle < -0.05: direction = "Right"
        else: direction = "Center"

        speedLimit = 1.7
        speedPower = 0.4
        speed = speedLimit - (1/forwardDistance)**speedPower

        if DEBUG:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "Direction:\t "       +                                                 direction
            print "Steering Angle:\t"   + (' ' if steeringAngle > 0 else '')   + "%.4f" % steeringAngle
            print "Speed:\t\t"          + (' ' if speed > 0 else '')           + "%.4f" % speed
            print "\nError:\t\t"        + (' ' if error > 0 else '')           + "%.4f" % error
            print "Wall Offset\t"       + (' ' if wallOffset > 0 else '')      + "%.4f" % wallOffset
            print "Forward Offset:\t"   + (' ' if forwardOffset > 0 else '')   + "%.4f" % forwardOffset
            print "Slope:\t\t"          + (' ' if slope > 0 else '')           + "%.4f" % slope
            print "Forward Distance:\t:"+ (' ' if forwardDistance > 0 else '') + "%.4f" % forwardDistance
        reverseCondition = forwardDistance < 0.35
        self.lidarData = [speed, steeringAngle, stopCondition, reverseCondition, stopList]


    def logic(self, speed, steeringAngle, stopCondition, reverseCondition, stopList):
        if reverseCondition:
            speed = -2
            steeringAngle = 0
            stopList.append(1)

        if len(stopList) > 60:
            steeringAngle = 0
            speed = 0

        self.apply_control(speed, steeringAngle)


class Serpentine(Autonomous):

    def __init__(self, zed, lidar):
