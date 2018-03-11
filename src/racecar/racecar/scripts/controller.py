global turningValues
turningValues = [0]
HISTORYSIZE = 10


def turn_control(ZEDvalue):
        length = len(turningValues)
	if (length > HISTORYSIZE-1): #if list is larger than the desired history size -1, remove item at index 0
		turningValues.pop(0)
	
	#turningValues.append(ZEDvalue)
	turningValues.append(ZEDvalue) #adds new ZEDvalue to last position in array
	
#	print turningValues #debug, shows all values in the list 
        P = I = 0
	for x in turningValues:
		I += x 
	
        #angleControlPyUsesToTurn
        const = (0.3/2.5)
        P = const * turningValues[length-1]
	I = const * (I/length) #averages values
        
        Kp = 1#0.9
        Ki = 0#1 - Kp
        output = (Kp * P) + (Ki * I)
	return output
	# Math explained:
	# negative is because the input and output angles will be reversed in positive and negative values
	# Max output angle / max input angle gives the turning ratio capping turning at the max output angle assuming the value coming in isn't larger than the max input angle
	# turningAngle[i] add up and divide by historysize to give the average of the angle
