#!/usr/bin/python
# ----------------
#

import cv2, numpy as np, math
from mode import Mode
from lane import Lane
from wall import Wall
from sign import Sign

class LaneCenter(Mode):
    speedMod = 0
    angleList = []

    def __init__(self, pastMode, laps, stop):
        super(LaneCenter, self).__init__()
        self.createAngleList()
        self.pastMode = pastMode
        self.laps = laps
        self.stop = stop


    def run(self, zed, lidar, vesc, DISPLAY):
        self.DISPLAY = DISPLAY
        self.data = lidar.getData() # Get lidar data
        self.driveMsg = vesc.getDriveMsg() # Get AckermannDrive
        self.process(zed.getImage()) # Processes the the data
        vesc.setDriveMsg(self.driveMsg) # Set AckermannDrive
        vesc.publish() # Publish to vesc


    def process(self, image):
        image = cv2.resize(image, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        height, width = image.shape[:2]
        left = self.side(image[:height, :width/2], (540, 1055), 'left')
        right = self.side(image[:height, width/2:width], (25, 540), 'right')

        lane = self.detectLane(left[0], right[0], width/2)
        sign = self.interpretSigns(left[1], right[1])
        #sign = None
        return self.control(lane, sign, width/2)


    def interpretSigns(self, left, right):
        shortcut, stop = False, False
        lShortcutSign, lStopSign = left
        rShortcutSign, rStopSign = right
        shortcutSignCenter = (lShortcutSign.getCenter()[0] + rShortcutSign.getCenter()[0]) / 2, (lShortcutSign.getCenter()[1] + rShortcutSign.getCenter()[1]) / 2
        shortcutSignArea = (lShortcutSign.getArea() + rShortcutSign.getArea()) / 2
        shortcutSign = Sign(shortcutSignCenter, shortcutSignArea)
        stopSignCenter = (lStopSign.getCenter()[0] + rStopSign.getCenter()[0]) / 2, (lStopSign.getCenter()[1] + rStopSign.getCenter()[1]) / 2
        stopSignArea = (lStopSign.getArea() + rStopSign.getArea()) / 2
        stopSign = Sign(stopSignCenter, stopSignArea)
        if shortcutSign.getArea() > 200:
            shortcut = True
        if stopSign.getArea() > 200:
            stop = True
        return (shortcut, stop), (shortcutSign, stopSign)


    def side(self, image, ranges, label):
        height, width = image.shape[:2]
        red, green, blue = self.color[0], self.color[1], self.color[2]
        wall = self.detectWall(ranges, label)
        shortcutSign = self.detectSign(image, green)
        stopSign = self.detectSign(image, red)

        bounds = int(height*0.2), int(height*0.4), int(height*0.6), int(height*0.8)#int(height*0.3), int(height*0.4), int(height*0.5)
        centers, areas = self.determineCentersAndAreasOfSide(image, bounds, blue)

        if self.DISPLAY:
            x, y = [], []
            for center in centers:
                if center is not (0, 0):
                    x.append(center[0])
                    y.append(center[1])
            Y = y[0], y[len(y)-1]
            #y = mx + b --> x = (y - b)/m
            m, b = np.polyfit(x, y, 1)
            X = int((Y[0] - b) / m), int((Y[1] - b) / m)
            top, bottom = (X[0],Y[0]), (X[1],Y[1])
            cv2.line(image, top, bottom, [0, 0, 255], 3)
            cv2.imshow(label + ' Camera', image)
            cv2.waitKey(1)
        return (wall, centers, areas), (shortcutSign, stopSign)


    def determineCentersAndAreasOfSide(self, image, bounds, color):
        width = image.shape[:2][1]
        centers, areas = [], []
        for i in range(0, len(bounds) - 1):
            (x, y), area = self.imageAnalysis(image[bounds[i]:bounds[i+1], :width], color)
            center = x, y + bounds[i]
            centers.append(center)
            areas.append(area)
        return centers, areas


    def detectSign(self, image, color):
        #image = cv2.resize(image, None, fx=0.25, fy=0.25, interpolation=cv2.INTER_AREA)
        #print "sign image h/w " + str(image.shape[:2])
        center, area = self.imageAnalysis(image, color)
        print "area " + str(area)
        print color[1] + "area " + str(area)
        # cv2.circle(image, center, 5, (0, 0, 255), -1)
        # cv2.imshow(color[1]+ ' Camera', image)
        # cv2.waitKey(1)
        return Sign(center, area)


    def detectWall(self, ranges, label):
        angle, distance = self.rangeAnalysis(ranges, label)
        return Wall(angle, distance)


    def detectLane(self, left, right, width):
        lWall, lCenters, lAreas = left
        rWall, rCenters, rAreas = right
        walls = lWall, rWall
        lArea, rArea = 0, 0
        for a in lAreas:
            lArea += a
        for a in rAreas:
            rArea += a
        area = (lArea + rArea) / 2
        print "lane area " + str(area)
        centers = self.determineCentersOfLane(lCenters, rCenters)
        x, y = [], []
        for center in centers:
            x.append(center[0])
            y.append(center[1])
        #y = mx + b
        #slope = np.polyfit(x, y, 1)[0]
        try:
            if centers[0] is not (0,0) or centers[1] is not (0,0):
                m, b = np.polyfit(y, x, 1)
                Y = y[0], y[len(y)-1]
                X = int((Y[0] - b) / m), width/2
                print "x, y " + str((x, y))
                x, y = (X[0],X[1]), (Y[0],Y[1])
                print "x, y " + str((x, y))
                slope = np.polyfit(x, y, 1)[0]
            else:
                slope = None
        except:
            slope = 0.0
        if False:
            print "slope %.3f" % slope
        #slope = (x2-x1)/float(y2-y1) # I've inverted the slope so that 0 is vertical and infinity is horizontal
        return Lane(walls, centers, slope, area)


    def determineCentersOfLane(self, lCenters, rCenters):
        centers = []
        for i in range(0, len(lCenters)):
            center = self.centerCenters((lCenters[i], rCenters[i]))
            centers.append(center)
        return centers


    def centerCenters(self, centers):
        lCenter, rCenter = centers
        center = 0, 0
        if lCenter is not (0, 0) and rCenter is not (0, 0): center = (lCenter[0] + rCenter[0]) / 2, (lCenter[1] + rCenter[1]) / 2
        elif lCenter is (0, 0) and rCenter is not (0, 0): center = rCenter
        elif rCenter is (0, 0) and lCenter is not (0, 0): center = lCenter
        return center


    def control(self, lane, sign, width):
        print width
        shortcut, stop = sign[0]
        shortcutSign = sign[1][0]
        wall, paper = False, True
        #wall, paper = True, False
        angleConst, distanceConst, wallConst = 0, 1, 1
        #paperConst = 3.0/(width/2)#2.4/(width/2)
        paperConst = 0.3/10#0.3/10#0.3/100
        #=============================================================================
        triggerDistance = 1.5
        lWall, rWall = lane.getWalls()
        lAngle, rAngle = lWall.getAngle(), rWall.getAngle()
        lDistance, rDistance = lWall.getDistance(), rWall.getDistance()
        fDistance = (lDistance[1] + rDistance[1]) / 2
        lDistance, rDistance = lDistance[0], rDistance[0]
        # if fDistance < triggerDistance or lDistance < triggerDistance or rDistance < triggerDistance:
        #     paper, wall = False, True
        # if lDistance < triggerDistance and rDistance < triggerDistance:
        #     paper, wall = False, True
        angleOffset = lAngle - rAngle
        distanceOffset = lDistance - rDistance
        #angleConst, distanceConst = 1, 1
        wallOffset = (angleConst * angleOffset) + (distanceConst * distanceOffset)
        #=============================================================================
        #topCenter, bottomCenter = lane.getCenters()
        slope = lane.getSlope()
        if slope is None:
            paperOffset = 0
        else:
            paperOffset = math.degrees(math.atan(slope))

        if lane.getArea() < 4000:#10000:
            wall, paper = True, False
        #=============================================================================
        if wall:
            paperConst = 0
            speed = self.variableSpeed(fDistance) + self.speedMod
        if paper:
            wallConst = 0
            speed = 1 + self.speedMod
        #=============================================================================
        error = (paperConst * paperOffset) + (wallConst * wallOffset)
        #=============================================================================
        steeringAngle = error
        if wall:
            steeringAngle /= (2*speed)
        # if speed > 1 and fDistance > 2: steeringAngle *= 0.2 #If car is going fast (because distance is far) do not turn so hard.
        #if fDistance > 2: steeringAngle /= 3
        #if speed < 0: speed *=10 #If attempting to reverse. Then actually allow the car to reverse!
        # if speed < 0:
        #     speed = (speed-0.2)*10 #If attempting to reverse. Then actually allow the car to reverse!
        #     steeringAngle = 0
        if speed < 0.05:
            steeringAngle = 0
            speed = -1 #If attempting to reverse. Then actually allow the car to reverse!
            # if speed < -0.5: steeringAngle = 0
        elif wall: speed += 0.1
        if stop and self.laps is 1000:
            speed = 0
            print "WE ARE STOPING!!!!!!!!!!"
        else:
            if paper and self.laps is 1:
                self.laps = 1000
                print "WE ARE ON PAPER AND ONEING@@@@@@@@@"
            if stop and wall:
                self.laps = 1
                print "ADDING ONE NOW###########"


        # if self.pastMode is not (wall, paper):
        #     self.laps += 1

        print "laps " + str(self.laps)
        # if self.laps => 1:
        #     if shortcut:
        #         shortcutConst = 0.6/84
        #         shortcutOffset = (width/2) - shortcutSign.center()
        #         steeringAngle = shorcutConst * shortcutOffset
        #     if self.stop:
        #         speed = 0
        steeringAngle = np.clip(steeringAngle, -0.3, 0.3)
        #speed = 1
        #=============================================================================
        self.pastMode = wall, paper
        self.stop = stop
        if True:
            print "\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"
            print "---angleOffset(=)lAngle---(-)rAngle---------------------------------------"
            print " %9.3f %12.3f %11.3f" % (angleOffset, lAngle, rAngle)
            print "distanceOffset(=)lDistance(-)rDistance------------------------------------"
            print " %9.3f %12.3f %11.3f" % (distanceOffset, lDistance, rDistance)
            print "----wallOffset(=)(angleConst*angleOffset)(+)(distanceConst*distanceOffset)"
            print " %9.3f %12.3f %11.3f %15.3f %13.3f" % (wallOffset, angleConst, angleOffset, distanceConst, distanceOffset)
            print "-----fDistance---slope----------------------------------------------------"
            print "%8d %14.3f " % (fDistance, slope)
            print "---------error(=)(paperConst*paperOffset)(+)(wallConst*wallOffset)--------"
            print " %9.3f %12.3f %12.3f %27.3f" % (error, paperConst, paperOffset, (wallConst*wallOffset))
            print "---------speed---steeringAngle---paper/wall-------------------------------"
            print "%10.3f %12.3f %13s/%s" % (speed, steeringAngle, paper, wall)
        return self.decide(speed, steeringAngle)


    def variableSpeed(self, distance):
        power = 1
        # distances = [0.2, 0.5, 2] # min distance, max distance
        # speeds = [-0.4, 0.3, 1.5] # min speed, max speed
        distances = [0.16, 3]#2.3] # min distance, max distance
        speeds = [-0.2, 1.7] # min speed, max speed
        if power is 1: # linear
            a, b = np.polyfit(distances, speeds, power)
            return (a*distance) + b
        if power is 2: #quadratic
            a, b, c = np.polyfit(distances, speeds, power)
            print "speed = " + str(a) + "x^2 + " + str(b) + "x + " + str(c)
            return (a*(distance**2)) + (b*distance) + c
        if power is 3: #cubic
            a, b, c, d = np.polyfit(distances, speeds, power)
            print "speed = " + str(a) + "x^3 + "  + str(b) + "x^2 + " + str(c) + "x + " + str(d)
            return (a*(distance**3)) + (b*(distance**2)) + (c*distance) + d


    def decide(self, speed, steeringAngle):
        self.apply_control(speed, steeringAngle)


    def imageAnalysis(self, image, color):
        maskedImage = self.colorMask(image, color)
        imgray = cv2.cvtColor(maskedImage, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(imgray, (5,5), 0)
        thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY)[1]
        contours = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[1]
        cv2.drawContours(image, contours, -1, (0,255,0), 3)
        if len(contours) > 0:
            contour = max(contours, key = cv2.contourArea)
            center = self.findCenter(contour)
            area = cv2.contourArea(contour)
            if self.DISPLAY:
                cv2.circle(image, center, 5, (0, 0, 255), -1)
            return center, area
        else:
            print "THERE ARE NO CONTOURS"
            return (0, 0), 0



    def rangeAnalysis(self, ranges, label):
        #x = y = []
        x, y = [], []
        frontFocus, length = 0.05, (ranges[1] - ranges[0]) # 0.04
        ignoreBack, ignoreFront = 0.1, 0.1 #0.3->94.5 degrees # The percentage of the back and front that you want to ignore [0.1, 0.1 magic]
        backBound, frontBound = int(length*ignoreBack), int(length*(1 - ignoreFront))
        frontFocus = int(length*(1 - frontFocus))
        sideLength, frontLength = frontBound - backBound, length - frontFocus

        if label is "left":
            lowerBound, upperBound = ranges[1] - frontBound, ranges[1] - backBound
            frontRanges = list(self.data.ranges[ranges[0]:ranges[1] - frontFocus])
        if label is "right":
            lowerBound, upperBound = ranges[0] + backBound, ranges[0] + frontBound
            frontRanges = list(self.data.ranges[ranges[0] + frontFocus:ranges[1]])
        sideRanges = list(self.data.ranges[lowerBound:upperBound])

        sideDistance = self.findAverageDistance(sideLength, sideRanges, 2)
        frontDistance = self.findAverageDistance(frontLength, frontRanges, 8)

        for i in range(lowerBound, upperBound):
            x.append(self.data.ranges[i]*math.cos(self.toAngle(i)))
            y.append(self.data.ranges[i]*math.sin(self.toAngle(i)))
        slope = np.polyfit(x, y, 1)[0]
        angle = math.atan(slope)
        return angle, (sideDistance, frontDistance)


    def findAverageDistance(self, length, ranges, cap):
        for x in range(0, length):
            if ranges[x] > cap: ranges[x] = cap
        return np.average(ranges)

    def findCenter(self, c):
        M = cv2.moments(c)
        if M["m00"] > 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else: cX, cY = 0, 0
        return cX, cY


    def fromAngle(self, angle): #Input = angle normal people use. Counter clockwise from -135 to 135
        return int(1081-((angle + 135)*(float(1081)/270))) #1081 is max angle (back left). (Angle+135)*len(LidarRanges)/len(RearAngles)


    def toAngle(self, index):
        return -(index-1081)*(float(270)/1081) - 135


    def createAngleList(self):
        for x in range(0, 1081):
            self.angleList.append(self.toAngle(x))


    def setSpeedMod(self, speed):
        self.speedMod = speed
