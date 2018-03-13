global turningAngles
turningAngles = [0,0,0,0,0	]
HISTORYSIZE = 5
MAXOUTPUTANGLE = 0.3 #left
MAXINPUTANGLE = 45 #right

def turn_control(ZEDangle):
	if (len(turningAngles) > HISTORYSIZE-1): #if list is larger than the desired history size -1, remove item at index 0
		turningAngles.pop(0)
	
	#turningAngles.append(ZEDangle)
	turningAngles.append(ZEDangle) #adds new ZEDangle to last position in array
	
	#print turningAngles #debug, shows all values in the list
	return (-(MAXOUTPUTANGLE/MAXINPUTANGLE)*(turningAngles[0]+turningAngles[1]+turningAngles[2]+turningAngles[3]+turningAngles[4])/HISTORYSIZE)
	# Math explained:
	# negative is because the input and output angles will be reversed in positive and negative values
	# Max output angle / max input angle gives the turning ratio capping turning at the max output angle assuming the value coming in isn't larger than the max input angle
	# turningAngle[i] add up and divide by historysize to give the average of the angles
	

print(turn_control(45))
print(turn_control(45))
print(turn_control(45))
print(turn_control(45))
print(turn_control(45))
print(turn_control(-22))
print(turn_control(-45))
print(turn_control(-8))
#drive_msg.steering_angle = turn_control(45)
