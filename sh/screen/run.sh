#!/bin/bash
./teleop.sh
screen -dmS zed python ~/racecar-ws-develop/src/racecar/racecar/scripts/new2/zed.py
python ~/racecar-ws-develop/src/racecar/racecar/scripts/new2/car.py
