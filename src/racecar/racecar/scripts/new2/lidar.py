#!/usr/bin/python
# ----------------
# lidar data can be retrieved from this file
# subscribe to lidar

import rospy as rp
from sensor_msgs.msg import LaserScan

class Lidar:
    processedData = []

    def __init__(self):
        #rp.init_node('car/lidar', anonymous=True)
        pass

    """
    def callback(self, data):
        #Do these need to run in a certain order?
        self.util = Utility(data)
        self.data = data


    def getUtil(self):
        return self.util"""

    def setData(self, data):
        self.data = data


    def getData(self):
        return self.data


class Utility:

    def __init__(self, data):
        self.data = data


    def createAnglesUsedToPlotGraph(self):
        """CURRENTLY NOT BEING USED
           Used in the polar graph as the angles
           data.angle_increment == PI/(4*180) == 0.00436332309619"""
        REDUCED = False
        REDUCINGFACTOR = 10
        theta = []
        if REDUCED:
            for x in xrange(0,1081,REDUCINGFACTOR):
                self.theta.append(x*0.00436332309619)
        else:
            for x in range(0,1081):
                self.theta.append(x*0.00436332309619)
        return theta


    def convertAngle(self, desiredAngle):
        """Input  = angle normal people use. Counter clockwise from -135 to 135
           Output = closest point where desired angle matches up within the LiDAR's sweep"""
        desiredAngle += 135
        return int(-desiredAngle*(1081/270))


    def averageRanges(self, desiredAngle1, desiredAngle2):
        """Finds the average distance in meters of the LiDAR responses within the specified range"""
        angle1 = self.convertAngle(desiredAngle1)
        angle2 = self.convertAngle(desiredAngle2)
        #print(str(angle1) + " :angles: " + str(angle2))
        averageRangesReturn = 0
        if (angle1 < angle2):
            for x in range(angle1,angle2):
                averageRangesReturn += self.data.ranges[x]
        elif (angle1 > angle2):
            for x in range(angle2, angle1):
                averageRangesReturn += self.data.ranges[x]
        else:
            averageRangesReturn = 0
            print("Error, cannot evaluate average a single position.")
        return averageRangesReturn / abs(angle2-angle1)


    def averageAllRanges(self):
        """CURRENTLY NOT BEING USED
           Finds the average distance of the LiDAR to the full 270 degree FOV"""
        return self.averageRanges(-135, 135)


    def distanceToWall(self, angleOfView, FOV):
        backAngle = angleOfView+FOV/2
        frontAngle = backAngle-FOV
        return self.averageRanges(backAngle,frontAngle)


    def offsetBetweenWalls(self, angleOfView, FOV):
        """How much closer car is to either wall. Negative = closer to left wall"""
        rightWall = self.distanceToWall(abs(angleOfView),FOV)
        leftWall = self.distanceToWall(-abs(angleOfView), FOV)
        distanceBetweenWalls = leftWall - rightWall
        if DEBUG:
            if (distanceBetweenWalls > 0.2):
                print(str(distanceBetweenWalls) + "\tRight wall is closer")
            elif (distanceBetweenWalls < -0.2):
                print(str(distanceBetweenWalls) + "\tLeft wall is closer")
            else:
                print(str(distanceBetweenWalls) + "\tEvenly between walls")
        return distanceBetweenWalls


    def angleOfWall(self, frontAngle, rearAngle, FOV):
        deltaAngle = frontAngle - rearAngle
        hypotenuse = self.averageRanges(frontAngle+FOV/2,frontAngle-FOV/2)
        adjacent = self.averageRanges(rearAngle+FOV/2,rearAngle-FOV/2)
        if DEBUG: print("Hypotenuse" + str(hypotenuse))
        if DEBUG: print("adjacent" + str(adjacent))
        opposite = self.lawOfCosinesFindSide(hypotenuse, adjacent, deltaAngle)
        return 90-(self.lawOfCosinesFindAngle(opposite, adjacent, hypotenuse))


    def lawOfCosinesFindAngle(self, sideA, sideB, sideC):
        """Finds angle opposite sideC"""
        return math.acos(((float(sideA)**2)+(sideB**2)-(sideC**2))/(2*sideA*sideB))*(180/math.pi)


    def lawOfCosinesFindSide(self, sideA, sideB, angleC):
        """Finds side opposite angleC"""
        return math.sqrt((float(sideA)**2)+(sideB**2)-(2*sideA*sideB*math.cos(math.pi*angleC/180)))


    def theWalls(self, frontAngle, wallAngle, rearAngle, FOV):
        """frontAngle = 70 #45 #70
           wallAngle = 90 #67.5 #90
           rearAngle = 110 #90 #110
           FOV = 3#5#2"""
        frontLeftWall = -self.angleOfWall(-frontAngle,-wallAngle,FOV)
        rearLeftWall = self.angleOfWall(-rearAngle,-wallAngle,FOV)
        frontRightWall = -self.angleOfWall(frontAngle,wallAngle,FOV)
        rearRightWall = self.angleOfWall(rearAngle,wallAngle,FOV)
        if DEBUG | VERBOSE: print("\n\nWall Angles:")
        if DEBUG | VERBOSE: print("Front Left\t\tFront Right")
        if DEBUG | VERBOSE: print(str(frontLeftWall)+"\t\t"+str(frontRightWall))
        if DEBUG | VERBOSE: print("Rear Left\t\tRear Right")
        if DEBUG | VERBOSE: print(str(rearLeftWall)+"\t\t"+str(rearRightWall))

        slopeOfRightWall = (frontRightWall+rearRightWall)/2
        slopeOfLeftWall = -(frontLeftWall+rearLeftWall)/2
        overallSlope = (slopeOfLeftWall+slopeOfRightWall)/2
        if DEBUG | VERBOSE: print("\nRight Wall Slope " + str(slopeOfRightWall))
        if DEBUG | VERBOSE: print("Left Wall Slope  " + str(slopeOfLeftWall))
        if DEBUG | VERBOSE: print("Overall Slope    " + str(overallSlope))
        return -overallSlope

    def averageWallSlope(self, data, frontAngle, rearAngle):
        """NOT CURRENTLY BEING USED"""
        tempArray = []
        angle1 = self.convertAngle(frontAngle)
        angle2 = self.convertAngle(rearAngle)

        if (angle1 < angle2):
            for x in range(angle1, angle2):
                tempArray.append(data.ranges[x])
        elif (angle1 > angle2):
            for x in range(angle2, angle1):
                tempArray.append(data.ranges[x])
        else:
            print("Error, cannot evaluate average a single position. Wall Slope array is now empty.")
        npArray = np.array(tempArray, dtype=np.float)
        npDiff = np.diff(npArray)
        #print("\n\n\n\n\nnpArray:\t"+str(len(npArray))+" "+str(npArray))
        #print("npDiff: \t"+str(len(npDiff))+" "+str(npDiff))
        slopes= []
        for x in range(0, len(npDiff)):
            slopes.append(math.atan(npDiff[x])*180/math.pi)
        #print("Slopes Array: "+str(slopes))
        print("Average of slopes: "+str(sum(slopes)))
