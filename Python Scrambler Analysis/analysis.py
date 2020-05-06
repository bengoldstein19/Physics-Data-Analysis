#This script converts raw 6 flags data into x and y accelerations and velocities defined on fixed axes, as well as the magnitude of acceleration and velocity
#READ IMPLEMENTATION.TXT FOR MORE INFORMATION

import csv #module necessary for spreadsheet files
from math import cos, sin #used for sine and cosine
from numpy import arctan #used for tangent inverse

with open('/Users/bengoldstein/Downloads/scrambler-acc.csv', 'rU') as csvinput: #opens six flags data file to read (ENTER YOUR OWN FILE PATH HERE)
    reader = csv.reader(csvinput) #creates iterator object used to read file
    rawdataarray = [] #initializes an array
    for row in reader: #reads through spreadsheet adding each row to an array
        rawdataarray.append(row)
    xvalues = [] #initializes empty array to store time values
    xaccelvalues = [] #initializes empty array to store xacceleration from sensor kinetics pro
    yaccelvalues = [] #initializes empty array to store yacceleration from sensor kinetics pro
    for i in range(len(rawdataarray)-1): #iterates through raw data and adds appropriate information to each array
        xvalues.append(float(rawdataarray[i+1][0]))
        xaccelvalues.append(float(rawdataarray[i+1][1]))
        yaccelvalues.append(float(rawdataarray[i+1][2]))
    directionangles = [] #initializes empty array used to store angle of velocity vector
    thetaoffset = 0 #initializes temporary value to be used as angle of velocity vector
    yvels = [] #initializes empty array to store true y velocity values (according to axes defined by velocity at first time tick)
    xvels = [] #initializes empty array to store true x velocity values (according to axes defined by velocity at first time tick)
    realxaccelvalues = [] #initializes empty array to store true x acceleration values (according to axes defined by velocity at first time tick)
    realyaccelvalues = [] #initializes empty array to store true y acceleration values (according to axes defined by velocity at first time tick)
    for i in range(len(xvalues)): #iterates over all of the raw data points to calculate true x and y velocity and acceleration values
        if not i == 0: #in every iteration except first execute following code
            axaverage = (xaccelvalues[i] + xaccelvalues[i - 1])/2 #stores average x acceleration over time interval (assuming locally linear)
            ayaverage = (yaccelvalues[i] + yaccelvalues[i - 1])/2 #stores average x acceleration over time interval (assuming locally linear)
            deltat = xvalues[i] - xvalues[i - 1] #stores change in time between current point and past point
            if yvels[i - 1] > 0: #if y velocity is greater than zero execute following code
                xvel = xvels[i - 1] + axaverage*(deltat)*cos(directionangles[i - 1]) + ayaverage*deltat*sin(directionangles[i - 1]) #calculates true x velocity using trig
                yvel = yvels[i - 1] + ayaverage*deltat*cos(directionangles[i - 1]) - axaverage*deltat*sin(directionangles[i - 1]) #calculates true y velocity using trig
                thetaoffset = arctan(xvel/yvel) #calculates angle of direction vector using trig
                xvels.append(xvel) #adds x velocity to appropriate array
                yvels.append(yvel) #adds y velocity to appropriate array
                directionangles.append(thetaoffset) #adds direction angle to appropriate array
            else: #if y velocity is less than zero execute different code that accounts for opposite direction
                xvel = xvels[i - 1] - axaverage*(deltat)*cos(directionangles[i - 1]) - ayaverage*deltat*sin(directionangles[i - 1]) #calculates the true x velocity using trig
                yvel = yvels[i - 1] - ayaverage*deltat*cos(directionangles[i - 1]) + axaverage*deltat*sin(directionangles[i - 1]) #calculates the true y velocity using trig
                thetaoffset = arctan(xvel/yvel) #calculates angle of direction vector using trig
                xvels.append(xvel) #adds x velocity to appropriate array
                yvels.append(yvel) #adds y velocity to appropriate array
                directionangles.append(thetaoffset) #adds direction angle to appropriate array
        else: #on first iteration execute following code
            xvel = xaccelvalues[i]*xvalues[i]/2 #calculates x velocity assuming initial x acceleration and direction angle are 0
            yvel = yaccelvalues[i]*xvalues[i]/2 #calculates y velocity assuming initial y acceleration and direction angle are 0
            xvels.append(xvel) #adds x velocity to appropriate array
            yvels.append(yvel) #adds y velocity to appropriate array
            thetaoffset = arctan(xvel/yvel) #calculates direction angle using trig
            directionangles.append(thetaoffset) #adds direction angle to appropriate array
    for i in range(len(xvalues)): #iterates over x velocities to retroactively calculate true x and y acceleration values
        deltat = xvalues[i] #sets default value of change in time over interval between current and past point
        deltavx = xvels[i] #sets default value of change in x velocity over interval between current and past point
        deltavy = yvels[i] #sets default value of change in y velocity over interval between current and past point
        if not i == 0: #on first iteration further calculation is necessary
            deltat = deltat - xvalues[i - 1] #corrects default value of change in time
            deltavx = deltavx - xvels[i - 1] #corrects default value of change in x velocity
            deltavy = deltavy - yvels[i - 1] #corrects default value of change in y velocity
        realxaccelvalues.append(deltavx/deltat) #calculates real x accel value and adds it to appropriate array
        realyaccelvalues.append(deltavy/deltat) #calculates real y accel value and adds it to appropriate array
    outputfile = open('/Users/bengoldstein/Downloads/dataoutput.csv', 'w') #opens or creates file to write refined data to as variable CHANGE FILE PATH
    with outputfile: #initializes use of file
        somethingwriter = csv.writer(outputfile) #creates iterator object used to write to file
        # creates row of headers to be written to file
        row = ['time_tick', 'x acceleration', 'normal acceleration', 'y acceleration', 'tangential acceleration', 'x velocity', 'yvelocity', 'magnitude of acceleration', 'magnitude of velocity', 'x and y axes are defined by initial direction of motion (y axis is tangential x axis is normal)']
        somethingwriter.writerow(row) #writes headers to file

        index = 0 #initializes value to count number of iterations for following loop
        for row in rawdataarray: #iterates over raw data and adds refined data in desired positions to be written to file
            if not row[0] == 'time_tick': #as long as row is not the header row execute following code
                #add refined data to be in position beneath appropriate header in file
                row = [row[0]] + [realxaccelvalues[index - 1]] + [row[1]] + [realyaccelvalues[index - 1]] + [row[2]] + [xvels[index - 1]] + [yvels[index - 1]] + [(realxaccelvalues[index - 1]**2+realyaccelvalues[index - 1]**2)**0.5] + [(xvels[index - 1]**2 + yvels[index - 1]**2)**0.5]
                somethingwriter.writerow(row) #writes row of data to file
            index = index + 1 #increments counter
    exit(0) #terminates script
