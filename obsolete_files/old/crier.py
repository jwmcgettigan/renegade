import rospy as rp
from random import randint
from std_msgs.msg import String


def poly_talker():
    rp.init_node('Crier', anonymous=True)
    pub = rp.Publisher('polycrier', String, queue_size=10)
    rate = rp.Rate(21)  # 21 Hz

    while not rp.is_shutdown():
        num = randint(0, 2)
        name = ["Dean", "Zane", "Vamsi"]
        output = name[num]
        rp.loginfo(output)
        pub.publish(output)
        rate.sleep()


if __name__ == "__main__":
    try:
        poly_talker()
    except rp.ROSInterruptException:
        pass

