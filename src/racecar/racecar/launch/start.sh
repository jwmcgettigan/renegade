#!/bin/bash

<launch>
  <arg name="racecar_version" default="racecar-v2" />
  <arg name="run_camera" default="false"/>
  <include file="$(find racecar)/launch/includes/$(arg racecar_version)-teleop.launch.xml">
    <arg name="racecar_version" value="$(arg racecar_version)" />
    <arg name="run_camera" value="$(arg run_camera)" />
  </include>
  <node pkg="racecar" name="crying_eyes" type="crying_eyes.py"/>
sleep 1
  <node pkg="racecar" name="eyes" type="eyes.py"/>
</launch>

