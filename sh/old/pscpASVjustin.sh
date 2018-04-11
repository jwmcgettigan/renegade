#!/bin/bash

scp cicc@172.21.82.46:"C:/Git-repos/renegade/src/racecar/racecar/scripts/new/probe.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
scp cicc@172.21.82.46:"C:/Git-repos/renegade/src/racecar/racecar/scripts/new/auto.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
scp cicc@172.21.82.46:"C:/Git-repos/renegade/src/racecar/racecar/scripts/new/run.py" ~/racecar-ws/src/racecar/racecar/scripts/new/
python ~/racecar-ws/src/racecar/racecar/scripts/new/run.py
