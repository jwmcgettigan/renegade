#!/usr/bin/python
import rospy as rp
from sensor_msgs.msg import LaserScan
from sensor_msgs.msg import Image
import matplotlib.pyplot as plt
import math
import numpy as np

DEBUG = False
VERBOSE = False
DISPLAY = False
objDebug = False
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

        
    def doTheStuff(self):
        if DEBUG: print("subscripted to /scan")

        self.counter += 1

        # if ((self.counter%RATE)==0):
        if DEBUG: print("A")
        ranges = []  
        if REDUCED:  
            for x in xrange(0,1081,REDUCINGFACTOR):
                ranges.append(self.data.ranges[x] if self.data.ranges[x] < 10 else 10)
        else:
            for x in range(0,1081):
                ranges.append(self.data.ranges[x] if self/data.ranges[x] < 10 else 10)

        if DEBUG: print(self.counter)
        if DISPLAY:
            if DEBUG: print("B")
            plt.subplot(111,projection='polar')
            if DEBUG: print("C")
            plt.scatter(theta, ranges, s=1)
            if DEBUG: print("D")
            plt.draw()
            if DEBUG: print("E")
    #        plt.pause(RATE/float(80)) #one of these has to be a float otherwise value becomes 0 if RATE < 40
            plt.pause(0.00000001) 
            if DEBUG: print("F")
            #plt.figure().clear()
            plt.clf()
            if DEBUG: print("G")
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
        return int(1081-(desiredAngle*(1081/270))) #1081 is max angle (back left). (Angle+135)*len(LidarRanges)/len(RearAngles)

    def unconvertAngle(self, arrayIndex): #Input = angle normal people use. Counter clockwise from -135 to 135
        return -(arrayIndex-1081)*(270/1081)-135


    def convertAngleIncorrect(self, desiredAngle): #Input = angle normal people use. Counter clockwise from -135 to 135
        desiredAngle += 135
        return int(-desiredAngle*(1081/270)) #Output = closest point where desired angle matches up within the LiDAR's sweep

    def averageRanges(self, desiredAngle1, desiredAngle2): #Finds the average distance in meters of the LiDAR responses within the specified range
        angle1 = self.convertAngleIncorrect(desiredAngle1)
        angle2 = self.convertAngleIncorrect(desiredAngle2)
        
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

    def averageRangesSpecial(self, desiredAngle1, desiredAngle2, tempRanges): #Finds the average distance in meters of the LiDAR responses within the specified range
        angle1 = self.convertAngleIncorrect(desiredAngle1)
        angle2 = self.convertAngleIncorrect(desiredAngle2)
        #print(str(angle1) + " :angles: " + str(angle2))
        averageRangesReturn = 0
        if (angle1 < angle2):
            for x in range(angle1,angle2):
                averageRangesReturn += tempRanges[x]
        elif (angle1 > angle2):
            for x in range(angle2, angle1):
                averageRangesReturn += tempRanges[x]
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

    def distanceToWall(self, angleOfView, FOV):
        backAngle = angleOfView+FOV/2
        frontAngle = backAngle-FOV
        return self.averageRanges(backAngle,frontAngle)

    def offsetBetweenWalls(self, angleOfView, FOV): #How much closer car is to either wall. Negative = closer to left wall
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
        

    def lawOfCosinesFindAngle(self, sideA, sideB, sideC): #Finds angle opposite sideC
        return math.acos(((float(sideA)**2)+(sideB**2)-(sideC**2))/(2*sideA*sideB))*(180/math.pi)

    def lawOfCosinesFindSide(self, sideA, sideB, angleC): #Finds side opposite angleC
        return math.sqrt((float(sideA)**2)+(sideB**2)-(2*sideA*sideB*math.cos(math.pi*angleC/180)))

    def theWalls(self, frontAngle, wallAngle, rearAngle, FOV):
        # frontAngle = 70 #45 #70
        # wallAngle = 90 #67.5 #90
        # rearAngle = 110 #90 #110 
        # FOV = 3#5#2
        if DEBUG & VERBOSE: print("Front Left")
        frontLeftWall = -self.angleOfWall(-frontAngle,-wallAngle,FOV)
        if DEBUG & VERBOSE: print("Rear Left")
        rearLeftWall = self.angleOfWall(-rearAngle,-wallAngle,FOV)
        if DEBUG & VERBOSE: print("Front Right")
        frontRightWall = -self.angleOfWall(frontAngle,wallAngle,FOV)
        if DEBUG & VERBOSE: print("Rear Right")
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
        return overallSlope

    def averageWallSlope(self, frontAngle, rearAngle):
        tempArray = []
        angle1 = self.convertAngleIncorrect(frontAngle)
        angle2 = self.convertAngleIncorrect(rearAngle)

        if (angle1 < angle2):
            for x in range(angle1, angle2):
                tempArray.append(self.data.ranges[x])
        elif (angle1 > angle2):
            for x in range(angle2, angle1):
                tempArray.append(self.data.ranges[x])
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




    def averageRangesSpecial(self, desiredAngle1, desiredAngle2, tempRanges): #Finds the average distance in meters of the LiDAR responses within the specified range
        angle1 = self.convertAngleIncorrect(desiredAngle1)
        angle2 = self.convertAngleIncorrect(desiredAngle2)
        #print(str(angle1) + " :angles: " + str(angle2))
        averageRangesReturn = 0
        if (angle1 < angle2):
            for x in range(angle1,angle2):
                averageRangesReturn += tempRanges[x]
        elif (angle1 > angle2):
            for x in range(angle2, angle1):
                averageRangesReturn += tempRanges[x]
        else:
            averageRangesReturn = 0
            print("Error, cannot evaluate average a single position.")
        return averageRangesReturn / abs(angle2-angle1)



#Current Stuff
####################################
    def averageDistanceWithWeight2(self, frontAngle, midAngle, rearAngle, tempRanges): #midAngle is more weighted, front and rear are less weighted. Can be used for values on either side of 0 degrees.
        # print "front" + str(frontAngle)
        # print "mid  " + str(midAngle)
        # print "rear " + str(rearAngle)
        # print "front < mid " + str(frontAngle < midAngle)
        # print "front < mid " + str(midAngle < rearAngle)

        if((frontAngle < midAngle) & (midAngle < rearAngle)): #Working from right side typically
            
            convertedFrontAngle = self.convertAngle(frontAngle)
            convertedMidAngle = self.convertAngle(midAngle)
            convertedRearAngle = self.convertAngle(rearAngle)
            if objDebug: print "\nconvFrontAngle:\t" + str(convertedFrontAngle)
            if objDebug: print "convMidAngle:\t" + str(convertedMidAngle)
            if objDebug: print "convRearAngle:\t" + str(convertedRearAngle)
            if objDebug: print "tempRanges[" + str(convertedFrontAngle) + "]:" + str(tempRanges[convertedFrontAngle])
            if objDebug: print "tempRanges[" + str(convertedMidAngle) + "]:" + str(tempRanges[convertedMidAngle])
            if objDebug: print "tempRanges[" + str(convertedRearAngle) + "]:\t" + str(tempRanges[convertedRearAngle])
            
            sumDistanceWithWeightFrontMid = 0
            averagingDivisorFrontMid = 0
            if False: print "\n\nfront to mid\n"
            for x in range(convertedFrontAngle, convertedMidAngle, -1): #341,181
                averagingDivisorFrontMid += (convertedFrontAngle-x)
                sumDistanceWithWeightFrontMid += tempRanges[x]*(convertedFrontAngle-x)
                # print "\ntempRanges[x]:\t" + str(tempRanges[x])
                # print "conFrontAngle:\t" + str(convertedFrontAngle)
                # print "x:\t\t" + str(x)
                # print "result:\t" + str(tempRanges[x]*(convertedFrontAngle-x))
                
            
            sumDistanceWithWeightMidRear = 0
            averagingDivisorMidRear = 0
            if False: print "\n\nmid to rear\n"
            for x in range(convertedMidAngle, convertedRearAngle, -1): #45,90
                averagingDivisorMidRear += (x-convertedRearAngle)
                sumDistanceWithWeightMidRear += tempRanges[x]*(x-convertedRearAngle) #90-45
                if False: print sumDistanceWithWeight
            
            # if True: print "sumDistWithWeightFrontMid:\t" + str(sumDistanceWithWeightFrontMid)
            # if True: print "averagingDivisorFrontMid:\t" + str(averagingDivisorFrontMid)
            # if True: print "sumDistWithWeightMidRear:\t" + str(sumDistanceWithWeightMidRear)
            # if True: print "averagingDivisorMidRear:\t" + str(averagingDivisorMidRear)
            # if True: print "sumDistWithWeightFM/avgDiv:\t" + str(sumDistanceWithWeightFrontMid/averagingDivisorFrontMid)
            # if True: print "sumDistWithWeightMR/avgDiv:\t" + str(sumDistanceWithWeightMidRear/averagingDivisorMidRear)
            averageDistanceWithWeight = ((sumDistanceWithWeightFrontMid/averagingDivisorFrontMid)+(sumDistanceWithWeightMidRear/averagingDivisorMidRear))/2
            averageDistanceWithoutWeight = (self.averageRangesSpecial(frontAngle, midAngle, tempRanges)+(self.averageRangesSpecial(midAngle, rearAngle, tempRanges)))/2
            if False: print "averageDistanceWithoutWeight:\t" + str(averageDistanceWithoutWeight)
            if False: print "averageDistanceWithWeight:\t" + str(averageDistanceWithWeight)
            #if averageDistanceWithWeight < averageDistanceWithoutWeight*0.99: print "Turn!"
            #if averageDistanceWithWeight < averageDistanceWithoutWeight*0.99: return -3 
            else: return 0
            #sumDistanceWithWeight /= (convertedRearAngle-convertedFrontAngle)**2 #length is squared. 
            #Divided once to get the weighting factor to a value factional value which maxes out at 1. 
            #Divided again to average the values since they were all summed.

            #Still need to add the rear-mid summing and need to manipulate the averaging as a result. 
            #if objDebug: print "distanceWithWeight\t" + str(sumDistanceWithWeight)
            return averageDistanceWithWeight
        elif((frontAngle > midAngle) & (midAngle > rearAngle)): #Working from left side typically
            return 0
        else: 
            print("Weighted Distance Averaging received invalid angle measurements")
            return 0


    def objectDetection3(self, frontAngle, midAngle, rearAngle, tempMaxDistance, objectDetectionCutoffDistance, debugDirectionString):
        if False: print debugDirectionString
        if objDebug: print "\n\n\n\n\nfrontAngle:\t " + str(frontAngle)
        if objDebug: print "midAngle:\t " + str(midAngle)
        if objDebug: print "rearAngle:\t " + str(rearAngle)
        if objDebug: print "tempMaxDistance: " + str(tempMaxDistance)
        if objDebug: print "objDetCutOffDist:" + str(objectDetectionCutoffDistance)
        tempRanges = self.reduceMaxDistance(tempMaxDistance)

        if objDebug: print "AvgRangesSpec:\t" + str((self.averageRangesSpecial(frontAngle, midAngle, tempRanges)+(self.averageRangesSpecial(midAngle, rearAngle, tempRanges)))/2)
        averageSpecialDistance = self.averageDistanceWithWeight2(frontAngle, midAngle, rearAngle, tempRanges)
        if False: print "\n\n\n\n\n"
        return averageSpecialDistance
        #if True: print("\n\n"+debugDirectionString+":\tAverage Special Range:\t"+str(averageSpecialDistance))
####################################
#NextCurrent
####################################


    def edgeDetection(self, frontAngle, rearAngle, tempMaxDistance):
        convertedFrontAngle = self.convertAngle(frontAngle)
        convertedRearAngle = self.convertAngle(rearAngle)
        tempRanges = self.reduceMaxDistance(tempMaxDistance)
        print "\n\n\n\n\n\nfrontAngle:\t" + str(frontAngle)
        print "rearAngle:\t" + str(rearAngle)
        print "frontAngleCon:\t" + str(convertedFrontAngle)
        print "rearAngleCon:\t" + str(convertedRearAngle)
        frontEdge = 0
        rearEdge = 0
        print "index\tangle\tdistance\tdistance-2"
        for x in range(convertedFrontAngle, convertedRearAngle, -1): #starts looking from the front and continue looking backwards
            print str(x) + "\t" + str(self.unconvertAngle(x)) + "\t" + str(tempRanges[x]) + "\t" + str(tempRanges[x-2])
            if ((tempRanges[x] * 0.8) > tempRanges[x-2]): #If the distance 2 array positions towards the rear is less than the current position * 0.8. We have the front edge
                frontEdge = x-2
                print "Front Edge Found"
            if ((tempRanges[x]) < tempRanges[x-2] * 0.8): #Same concept for rear edge, but now the more forward position must be the object, so it should be the object.
                rearEdge = x
                print "Rear Edge Found"
        print ("objFrontAng:\t" + str(frontEdge))
        print ("objRearAng:\t" + str(rearEdge))





        #This takes input of an angle from the LiDAR and pulls the distance found at that angle
        #and performs sin(theta) = opposite/hypotenuse to find the length of the line perpencular to the car, thus the distance from the wall.
        #|hypotenuse*sin(theta)| = opposite #The || or abs() is to account for negative or left angles
    def perpendicularLineDistance(self, angle):
        radianAngle = angle*0.0174533 #degree to radian conversion
        hypotenuse = self.data.ranges[self.convertAngle(angle)]
        sinOfAngle = math.sin(radianAngle)


        adjacentDistance = abs(hypotenuse*sinOfAngle)
        # print str(angle) + "\t" + str(self.data.ranges[self.convertAngle(angle)]) + "\t" + str(abs(self.data.ranges[self.convertAngle(angle)]*math.sin(angle)))
        print str(angle) + "\t" + str(hypotenuse) + "\t" + str(adjacentDistance)
        return adjacentDistance

    def closestObjectsAngleFullRanges(self): #distance from closest object, angle of closest object
        tempRanges = []
        for x in range(0,21):
            tempRanges.append(65)
        for x in range(21,1080):
            tempRanges.append(self.data.ranges[x])
        #print tempRanges
        return min(tempRanges), tempRanges.index(min(tempRanges))

# #implement closest object on either side
#     def closestObjectsAngle(self, frontAngle, rearAngle): #distance from closest object, angle of closest object
#         tempRanges = []
#         if frontAngle < rearAngle:
#             for x in range(0,):
#                 tempRanges.append(65)
#         return min(self.data.ranges), self.data.ranges.index(min(self.data.ranges))

####################################









    def objectDetection2(self, frontAngle, midAngle, rearAngle, tempMaxDistance, objectDetectionCutoffDistance, debugDirectionString):
        tempRanges = self.reduceMaxDistance(tempMaxDistance)

        

        averageSpecialDistance = self.averageRangesSpecial(frontAngle, rearAngle, tempRanges)
        if False: print("\n\n"+debugDirectionString+":\tAverage Special Range:\t"+str(averageSpecialDistance))

####################################

    def averageDistanceWithWeight(self, lesserWeightAngle, greaterWeightAngle, weight):
        sumDistancesWithWeight = 0
        convertedLesserAngle = convertAngleIncorrect(lesserWeightAngle)
        for position in range(convertedLesserAngle, convertAngleIncorrect(greaterWeightAngle)):
            sumDistancesWithWeight += self.data.ranges[position]*(10**())
            sumDistancesWithWeight += self.data.ranges[position]*(convertedLesserAngle**(1+((position-lesserWeightAngle)/10))) #540^(1+((position)/10))
        return sumDistancesWithWeight



    def objectDetection(self, frontAngle, rearAngle, tempMaxDistance, objectDetectionCutoffDistance, debugDirectionString):
        tempRanges = self.reduceMaxDistance(tempMaxDistance)
        averageSpecialDistance = self.averageRangesSpecial(frontAngle, rearAngle, tempRanges)
        if False: print("\n\n"+debugDirectionString+":\tAverage Special Range:\t"+str(averageSpecialDistance))

####################################
    def reduceMaxDistance(self, newMaxDistance): #To make this a permanent change, assign the result to data.ranges
        reducedArray = []
        for x in range(0,len(self.data.ranges)):
            if self.data.ranges[x] > newMaxDistance: 
                reducedArray.append(newMaxDistance)
            else:
                reducedArray.append(self.data.ranges[x])
        return reducedArray



        #if DEBUG: print(debugDirectionString+"Average Special Range:\t"+str(averageSpecialRange))
        #turn (averageSpecialDistance < objectDetectionCutoffDistance)
        #Return True/there is an object, if the average distance within this range is less the the cutoff distance, then there must be an object present
        #\Example: objectDectection(90, 120, 2, 0.9)
        #If average distance within this range is less than 90% the max possible distance, then there is an object.

    #def stopCondition(self):
        #return (self.averageRanges(-10,10) < .25)
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
        try: rp.spin()
        except KeyboardInterrupt: print "Shutting down ROS LiDAR feature dector module."


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
