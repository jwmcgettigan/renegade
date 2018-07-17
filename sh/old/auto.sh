#!/bin/bash
key="q"
python ~/racecar-ws/src/racecar/racecar/scripts/crying_eyes.py &
crying_eyes_pid=$!
python ~/racecar-ws/src/racecar/racecar/scripts/controller.py &
controller_pid=$!
while read -n1 char ; do
  if [ "$char" = "$q" ] ; then
    kill "$crying_eyes_pid"
    kill "$controller_pid"
  fi
done
