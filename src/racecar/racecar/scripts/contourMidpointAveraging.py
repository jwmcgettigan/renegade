# contour = [0.2,0.2,0.2,0.2,-0.5]
contour = [-0.2,-0.05,0,0.05]

#contour midpoint values are averaged with weight given to the further contours

length = len(contour) #because Justin does not like calling len multiple times
sums = 0 
divisor = 0

for x in range(0, length):
    weight = float(length)/(x+0.3) #Do NOT change the number to an integer below 1. Usable range is (0,inf) but (0.2,2) is recommended
    sums += weight*(contour[x]) #sums the values while multiplying them by the weight
    divisor += weight #keeps track of the weights so that when you divide the want to "remove" the weight, it goes back to a value relative to the original
    print "average:" + str(sums/divisor) + "\n sums: " + str(sums) + "\n  divisor: " + str(divisor) + "\n   current contour: " + str(contour[x]) + "\n    \t\t\t\tweight: " + str(weight)
averageOffset = sums/divisor
print averageOffset