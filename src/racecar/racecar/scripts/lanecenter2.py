#!/usr/bin/python
# ----------------
#

from mode import Mode

class LaneCenter(Mode):

    def __init__(self, lidar):
        super(LaneCenter, self).__init__()


    def run(self, zed, lidar, vesc, DISPLAY):
        self.DISPLAY = DISPLAY
        self.data = lidar.getData() # Get lidar data
        self.driveMsg = vesc.getDriveMsg() # Get AckermannDrive
        self.process(zed.getImage()) # Processes the the data
        self.vesc.setDriveMsg(self.driveMsg) # Set AckermannDrive
        self.vesc.publish() # Publish to vesc


    def process(self, image):
        height, width = image.shape[:2]
        left = self.side(image[:height, :width/2], (540, 1055), 'left')
        right = self.side(image[:height, width/2:width], (25, 540), 'right')
        lane = self.detectLane(left, right)
        return self.control(left, right)


    def side(self, image, ranges, label):
        wall = self.detectWall(ranges)

        height, width = image.shape[:2]
        leftLine = self.detectLine(image[:height, :width/2], 'left')
        rightLine = self.detectLine(image[:height, width/2:width], 'right')
        if self.DISPLAY:
            cv2.imshow(label + ' Camera',  np.hstack([leftLine.draw(), rightLine.draw()]))
            cv2.waitKey(1)


    def detectWall(self):
        return Wall()


    def detectLine(self):
        return Line()


    def detectLane(self):
        return Lane()


    def control(self):
        pass


    def decide(self, speed, steeringAngle):
        self.apply_control(speed, steeringAngle)


    def imageAnalysis(self):



    def rangeAnalysis(self, ranges):
        filteredRanges = filterRanges(ranges)


    def filterRanges(self, ranges):
        tempRanges = []
        for x in range(0, ranges[0]): tempRanges.append(65)
        for x in range(ranges[0], ranges[1]): tempRanges.append(self.data.ranges[x])
        for x in range(ranges[1], 1081): tempRanges.append(65)
        return tempRanges
