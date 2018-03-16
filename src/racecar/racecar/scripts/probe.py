#!/usr/bin/python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
import matplotlib.pyplot as plt
import math

DEBUG = True
DISPLAY = False
#RATE = 1 #1 = 40 Hz, 2 = 20 Hz, 4 == 10 Hz, 8 = 5 Hz, 20 == 2 Hz, 40 == 1 Hz, 80 == 0.5 Hz




class Probe:
    counter = 0

    if DISPLAY:
        plt.subplot(111,projection='polar')
        plt.show()
        #plt.figure().show()
        #plt.figure().canvas.draw()

    

    def __init__(self, data, theta):
        self.data = data
        self.theta = theta
        pass


    # def callback(self, data):
    # #    plt.close()    
    # #    plt.figure().clear()
        
    def doTheStuff(self):
        if DEBUG:
            print("subscripted to /scan")

        self.counter += 1

        # if ((self.counter%RATE)==0):
        if DEBUG:
            print("A")
        ranges = []  
        if REDUCED:  
            for x in xrange(0,1081,REDUCINGFACTOR):
                ranges.append(self.data.ranges[x] if self.data.ranges[x] < 10 else 10)
        else:
            for x in range(0,1081):
                ranges.append(self.data.ranges[x] if self/data.ranges[x] < 10 else 10)

        if DEBUG:
            print(self.counter)
        if DISPLAY:
            if DEBUG:
                print("B")
            plt.subplot(111,projection='polar')
            if DEBUG:
                print("C")
            plt.scatter(theta, ranges, s=1)
            if DEBUG:
                print("D")
            plt.draw()
            if DEBUG:
                print("E")
    #        plt.pause(RATE/float(80)) #one of these has to be a float otherwise value becomes 0 if RATE < 40
            plt.pause(0.00000001) 
            if DEBUG:
                print("F")
            #plt.figure().clear()
            plt.clf()
            if DEBUG:
                print("G")
            #plt.close()

        def createAnglesUsedToPlotGraph(): #Used in the polar graph as the angles
            REDUCED = False
            REDUCINGFACTOR = 10
            theta = []
            if REDUCED:
                for x in xrange(0,1081,REDUCINGFACTOR):
                    theta.append(x*0.00436332309619)
            else:
                for x in range(0,1081):
                    theta.append(x*0.00436332309619) #data.angle_increment == PI/(4*180) == 0.00436332309619

        
    def convertAngle(self, desiredAngle): #Input = angle normal people use. Counter clockwise from -135 to 135
        desiredAngle += 135
        return int(-desiredAngle*(1081/270)) #Output = closest point where desired angle matches up within the LiDAR's sweep

    def averageRanges(self, desiredAngle1, desiredAngle2): #Finds the average distance in meters of the LiDAR responses within the specified range
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

    def averageAllRanges(self): #Finds the average distance of the LiDAR to the full 270 degree FOV
        return self.averageRanges(-135, 135)

    # def averageIntensities(self, data): #May not be necessary
    #     averageIntensitiesReturn = 0
    #     for x in range(0,len(data.intensities)):
    #         averageIntensitiesReturn += data.intensities[x]
    #     return averageIntensitiesReturn / len(data.intensities)

    def offsetBetweenWalls(self, angleOfView, FOV): #How much closer car is to either wall. Negative = closer to left wall
        backRightAngle = (abs(angleOfView)+FOV/2)
        frontRightAngle = backRightAngle-FOV
        backLeftAngle = -backRightAngle
        frontLeftAngle = -frontRightAngle
        # print("BackRightAngle: " + str(backRightAngle))
        # print("FrontRightAngle: " + str(frontRightAngle))
        # print("BackLeftAngle: " + str(backLeftAngle))
        # print("FrontLeftAngle: " + str(frontLeftAngle))
        #print("Left: " + str(self.averageRanges(backLeftAngle,frontLeftAngle)) + "\tRight:" + str(self.averageRanges(backRightAngle,frontRightAngle)))
        distanceBetweenWalls = -(self.averageRanges(backRightAngle,frontRightAngle)-self.averageRanges(backLeftAngle,frontLeftAngle))
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
        print("Hypotenuse" + str(hypotenuse))
        print("adjacent" + str(adjacent))
        opposite = self.lawOfCosinesFindSide(hypotenuse, adjacent, deltaAngle)
        return 90-(self.lawOfCosinesFindAngle(opposite, adjacent, hypotenuse))
        

    def lawOfCosinesFindAngle(self, sideA, sideB, sideC): #Finds angle opposite sideC
        return math.acos(((float(sideA)**2)+(sideB**2)-(sideC**2))/(2*sideA*sideB))*(180/math.pi)

    def lawOfCosinesFindSide(self, sideA, sideB, angleC): #Finds side opposite angleC
        return math.sqrt((float(sideA)**2)+(sideB**2)-(2*sideA*sideB*math.cos(math.pi*angleC/180)))

    def theWalls(self):
        rearLeftWall = self.angleOfWall(-90,-125,2)
        frontLeftWall = self.angleOfWall(-55,-90,2)
        rearRightWall = self.angleOfWall(90,125,2)
        frontRightWall = self.angleOfWall(55,90,2)
        print("\n\nWall Angles:")
        print("Front Left\t\tFront Right")
        print(str(frontLeftWall)+"\t\t"+str(frontRightWall))
        print("Rear Left\t\tRear Right")
        print(str(rearLeftWall)+"\t\t"+str(rearRightWall))

    def getRanges(self):
        return self.data.ranges

    def getData(self):
        return self.data




    # def displayLidar(self. ranges): #Incomplete
    #     plt.subplot(111, projection='polar')
    #     plt.scatter(ranges, y, color='k', s=4)
    #     #plt.show()    
    #     plt.draw()
    #     plt.pause(0.001)
        
        
    if __name__ == '__main__':
        rp.init_node("lidarListener", anonymous=True)
        #probe = Probe()
        doTheStuff(self)
        try:
            print("asdf")
            rp.spin()
            print("fdsa")
        except KeyboardInterrupt:
            print "Shutting down ROS LiDAR feature dector module."


##########################
# std_msgs/Header header
# float32 angle_min
# float32 angle_max
# float32 angle_increment
# float32 time_increment
# float32 scan_time
# float32 range_min
# float32 range_max
# float32[] ranges
# float32[] intensities
##########################