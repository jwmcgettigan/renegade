import rospy
from threading import Thread
from std_msgs.msg import String, Header
import numpy as np
from ackermann_msgs.msg import AckermannDriveStamped, AckermannDrive

PUBLISH_RATE = 20.0 # number of control commands to publish per second
SPEED = 22
MIN_SPEED = 0.1

class Control():
    def __init__(self):
        self.pub = rospy.Publisher("/vesc/high_level/ackermann_cmd_mux/input/nav_0",\
                                   AckermannDriveStamped, queue_size=1)

        self.last_error = None

        self.drive_thread = Thread(target=self.apply_control)
        self.drive_thread.start()


    def apply_control(self):
        while not rospy.is_shutdown():
            drive_msg_stamped = AckermannDriveStamped()
            drive_msg = AckermannDrive()
            drive_msg.speed = SPEED
            drive_msg.steering_angle = -0.5
            drive_msg.acceleration = 0
            drive_msg.jerk = 0
            drive_msg.steering_angle_velocity = 0
            drive_msg_stamped.drive = drive_msg
            self.pub.publish(drive_msg_stamped)

            rospy.sleep(1.0/PUBLISH_RATE)


if __name__ == "__main__":
    rospy.init_node("eye_of_sauron")
    vs = Control()
    rospy.spin()


