############## CLOSEST STEERING CONTROL ###############################

import math

sensor =  int(input("position now (deg) : "))
target = int(input("destination (deg) : "))

distance_degree = 0

error_absolute = abs(int(target) - int(sensor))



if (error_absolute <= 180):
    if(int(target) - int(sensor) < 0):
        print("CCW")
        distance_degree = sensor - target
        print("distance (deg) : ", distance_degree)
    else:
        print("CW")
        distance_degree = target - sensor
        print("distance (deg) : ", distance_degree)


if (error_absolute > 180):
    if(int(target) - int(sensor) < 0):
        print("CW")
        distance_degree = (360 - sensor) + target
        print("distance (deg) : ", distance_degree)
    else:
        print("CCW")
        distance_degree = (360 - target) + sensor
        print("distance (deg) : ", distance_degree)
        


    
