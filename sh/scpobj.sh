#!/bin/bash

scp cicc@172.21.82.154:"/home/cicc/Documents/Autonomous\ Robotic\ Systems/Lidar/ObjectFollower.py" ~/racecar-ws-develop/src/racecar/racecar/scripts/
#python ~/racecar-ws-develop/src/racecar/racecar/scripts/zed.py & disown
~/racecar-ws-develop/sh/car.sh
