#!/usr/bin/python
# ----------------
#

from mode import Mode

class LaneCenter(Mode):

    def __init__(self, lidar):
        self.decide(self.control(self.process( lidar.getUtil(), lidar.getData() )))


    def process(self, util, data):
        slope           = util.theWalls(data, 70,90,110,3)
        wallOffset      = util.offsetBetweenWalls(data, 90,5)
        forwardOffset   = util.offsetBetweenWalls(data, 45,5)
        forwardDistance = util.averageRanges(data, -20,20)
        stopCondition   = util.averageRanges(data, -10,10) < .25
        return slope, wallOffset, forwardOffset, forwardDistance, stopCondition


    def control(self):
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


    def decide(self, speed, steeringAngle, stopCondition, reverseCondition, stopList):
        if reverseCondition:
            speed = -2
            steeringAngle = 0
            stopList.append(1)

        if len(stopList) > 60:
            steeringAngle = 0
            speed = 0

        self.apply_control(speed, steeringAngle)
