# -*- coding: utf-8 -*-
"""
Created on Fri Oct  8 15:57:39 2021

@author: Jlee
"""

"""
Description: Analysis from valve bench test setup. Pico Scope channels: A = PT downstream, B = PT upstream, C = Cmd valve, D = Sense valve.
Pico Log channels: Water reservoir tank pressure, air pressure to valve, flow rate, Cmd valve (same as Pico Scope, use this channel to sync).
PicoScope results stored in arrays: "opArr2", "clArr2".
PicoLog results stored in arrays: "piOpArr2", "piClArr2".

Last updated: Oct 20, 2021

"""

import numpy as np
from scipy import io
import os
import time
import pandas as pd

# User information here.
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000578 - Pneumatic Valve Tests/Test Data'
testStart = 5

# User defined thresholds / parameters.
vThresh = 10 # units voltage. valve signal switches from 0 to 24V. 
dutyCycle = 10 # seconds to detect end of phase during short duty cycle.



tic = time.time()
test = str(testStart)

# Initialize variables.


# Loop through all files in directory.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if test in filename and '.mat' in filename:
        
        testNum = int(test)
        # Initialize variables
        countOpen = 0
        opArr = np.array([])
        opArr2 = np.array([])
        countClose = 0
        clArr = np.array([])
        clArr2 = np.array([])
        pf1Arr = np.array([])
        pi1Arr = np.array([])
        chAp = np.array([])
        chBp = np.array([])
        vCmd0 = -99
        vAct0 = -99
        dt = -99
        chA = np.array([])
        chB = np.array([])
        chC = np.array([])
        chD = np.array([])
        
        
        # Load raw data from .mat file.
        rawData = io.loadmat(filename)
        chA = rawData['A']
        chB = rawData['B']
        chC = rawData['C']
        chD = rawData['D']
        dt = rawData['Tinterval']
        dt = float(dt[0])
        
        # Convert channels A and B to pressure psi units.
        chAp = (chA/250*1000-4)*3.75
        chBp = (chB/250*1000-4)*3.75
        
        # Find out the initial states of all channels, in first 2 seconds.
        pf0 = np.mean(chAp[0:round(2/dt)]) # water pressure downstream of valve.
        pi0 = np.mean(chBp[0:round(2/dt)]) # water pressure upstream of valve.
        vCmd0 = np.mean(chC[0:round(2/dt)]) # toggle switch commanding valve. Closed here.
        vAct0 = np.mean(chD[0:round(2/dt)]) # hall sensor indicating valve action completed (at least most of the way there). Closed here.
        
        # Analyze latencies during open phase.
        for i in range(round(2/dt),chC.shape[0]-round(dutyCycle/dt)):
            if chC[i] < vThresh and chC[i-1] > vThresh and chC[i+1] < vThresh and chC[i-2] > vThresh: # check for valve cmd to open.
                countOpen += 1
                opArr = np.append(opArr,int(test))
                opArr = np.append(opArr, countOpen)
                opArr = np.append(opArr, i*dt)
                endOpen = 0
                for n in range(i,i+round(dutyCycle/dt)):
                    if chC[n] > vThresh and chC[n-1] < vThresh: # detect when valve cmd to close.
                        endOpen = n
                        break
                pf1Arr = np.append(pf1Arr,np.mean(chAp[i+round(0.3/dt):endOpen]))
                pi1Arr = np.append(pi1Arr,np.mean(chBp[i+round(0.3/dt):endOpen]))
                for j in range(i,endOpen): # determine latencies after valve cmd to open.
                    if chD[j] < vThresh and chD[j-1] > vThresh: 
                        opArr = np.append(opArr, j*dt) # time at sense valve change.
                        break
                for k in range(i,endOpen):
                    if chAp[k] > pf0+1.5:
                        opArr = np.append(opArr, k*dt) # time at change in downstream pressure.
                        break
                for m in range(i,endOpen): 
                    if chBp[m] < pi0-1.5:
                        opArr = np.append(opArr, m*dt) # time at change in upstream pressure.
                        opArr = np.append(opArr,(k-i)*dt) # response time (cmd to first instance of valve movement via pressure response).
                        opArr = np.append(opArr, (j-k)*dt) # valve opening action time.
                        opArr = np.append(opArr, (j-i)*dt) # sensor lag (cmd to sense).
                        opArr = np.append(opArr, np.max(chAp[j:endOpen])) # peak pressure.
                        opArr = np.append(opArr, np.mean(chAp[j+round(0.5/dt):endOpen])) # avg pressure.
                        break
        
        opArr2 = np.reshape(opArr,(countOpen,int(opArr.shape[0]/countOpen)))
    

       
        # Analyze latencies during close phase.
        for i in range(round(2/dt),chC.shape[0]-round(dutyCycle/dt)):
            if chC[i] > vThresh and chC[i-1] < vThresh and chC[i+1] > vThresh: # check valve cmd to close.
                endClose = 0                
                for n in range(i,i+round(dutyCycle/dt)):
                    if chC[n] < vThresh and chC[n-1] > vThresh: # detect when valve cmd to open.
                        endClose = n
                        countClose += 1
                        clArr = np.append(clArr, int(test))
                        clArr = np.append(clArr, countClose)
                        clArr = np.append(clArr, i*dt)
                        break
                for j in range(i,endClose): #determine latencies after valve cmd to close.
                    if chD[j] > vThresh and chD[j-1] < vThresh:
                        clArr = np.append(clArr, j*dt) # time at sense valve change.
                        break
                for k in range(i,endClose):
                    if chAp[k] < pf1Arr[countClose-1]-1.5:
                        clArr = np.append(clArr,k*dt) # time at change in downstream pressure.
                        break
                for m in range(i,endClose):
                    if chBp[m] > pi1Arr[countClose-1]+1.5:
                        clArr = np.append(clArr,m*dt) # time at change in upstream pressure.
                        maxP = np.max(chBp[m:endClose]) # upstream pressure spike.
                        maxPt = np.nonzero(chBp[m:endClose]==maxP)
                        clArr = np.append(clArr, (maxPt[0][0]+m)*dt)
                        clArr = np.append(clArr, (j-i)*dt) # sensor lag (cmd to sense).
                        tInt = np.amin((k*dt,m*dt))-j*dt
                        clArr = np.append(clArr, tInt) # sense time between valve sense indicating close and realized change in fluid pressure.
                        break
        clArr2 = np.reshape(clArr,(countClose,int(clArr.shape[0]/countClose)))
        
        
        print('Pico Scope test '+str(testNum)+' done: '+str(time.time()-tic))
        
    if test in filename and '.csv' in filename:
        
        # Initialize variables.
        rawFR = np.array([])
        rawTankP = np.array([])
        rawAirP = np.array([])
        dfRaw = np.array([])
        rawCmd = np.array([])
        ctOpen = 0
        ctClose = 0
        piOpArr = np.array([])
        piTest = int(test)
        piClArr = np.array([])
        
        # Load raw csv file (Pico Log). 
        df = pd.read_csv(filename)
        dt2 = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        rawFR = dfRaw[:,1]
        rawTankP = dfRaw[:,2]
        rawAirP = dfRaw[:,3]
        rawCmd = dfRaw[:,4]
        
        # Get starting conditions of water/air pressures and flow rate.
        piTank0 = np.mean(rawTankP[0:round(2/dt2)])
        piAir0 = np.mean(rawAirP[0:round(2/dt2)])
        piFR0 = np.mean(rawFR[0:round(2/dt2)])
        
        # Analyze avg, min, max of flow rates, air and tank pressures during open phase.
        for i in range(round(2/dt2),rawFR.shape[0]-round(dutyCycle/dt2)):
            if rawCmd[i] == 0 and rawCmd[i-1] == 1:
                ctOpen += 1
                piOpArr = np.append(piOpArr,(piTest, ctOpen, i*dt2)) # test number, open count, time at open cmd. 
                for j in range(i,i+round(dutyCycle/dt2)):
                    if rawCmd[j] == 1 and rawCmd[j-1] == 0:
                        for k in range(i,j):
                            if rawFR[k] > piFR0 + 20 and rawFR[k+1] - rawFR[k] < -5: # Detect flow rate peak.
                                piOpArr = np.append(piOpArr, (np.mean(rawFR[k+round(0.5/dt2):j]), np.amin(rawFR[k:j]), np.max(rawFR[k:j]))) # flow rate data.
                                break
                        piOpArr = np.append(piOpArr, (np.mean(rawAirP[i:j]), np.amin(rawAirP[i:j]), np.max(rawAirP[i:j]))) # air pressure data.
                        piOpArr = np.append(piOpArr, (np.mean(rawTankP[i:j]), np.amin(rawTankP[i:j]), np.max(rawTankP[i:j]))) # air pressure data.       
                        piOpArr2 = np.reshape(piOpArr, (ctOpen,round(piOpArr.shape[0]/ctOpen)))
                        break     
        
        # Analyze avg, min, max of flow rates, air and tank pressures during close phase.
        for i in range(round(2/dt2),rawCmd.shape[0]-round(dutyCycle/dt2)):
            if rawCmd[i] == 1 and rawCmd[i-1] == 0:
                ctClose += 1
                piClArr = np.append(piClArr,(piTest, ctClose, i*dt2)) # tets number, close count, time at close cmd.
                for j in range(i,i+round(dutyCycle/dt2)):
                    if (rawCmd[j] == 0 and rawCmd[j-1] == 1): #or (j == i+round(8/dt2))
                        piClArr = np.append(piClArr, (np.mean(rawFR[i+round(1/dt2):j]), np.amin(rawFR[i:j]), np.max(rawFR[i:j]))) # flow rate data.
                        piClArr = np.append(piClArr, (np.mean(rawAirP[i:j]), np.amin(rawAirP[i:j]), np.max(rawAirP[i:j]))) # air pressure data.
                        piClArr = np.append(piClArr, (np.mean(rawTankP[i:j]), np.amin(rawTankP[i:j]), np.max(rawTankP[i:j]))) # air pressure data.
                        piClArr2 = np.reshape(piClArr, (ctClose,round(piClArr.shape[0]/ctClose)))
                        break
                    
                
                
                
                    
                
                
                
        
        
        
        
        
        
        
        
        
        

                    
                
                
        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                        
                
                
        
        
        
        
        
        