#!/bin/bash

scp cicc@172.21.83.10:"/home/cicc/Documents/Autonomous\ Robotic\ Systems/Lidar/probe.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
scp cicc@172.21.83.10:"/home/cicc/Documents/Autonomous\ Robotic\ Systems/Lidar/auto.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
scp cicc@172.21.83.10:"/home/cicc/Documents/Autonomous\ Robotic\ Systems/Lidar/run.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
python ~/racecar-ws/src/racecar/racecar/scripts/new/run.py
