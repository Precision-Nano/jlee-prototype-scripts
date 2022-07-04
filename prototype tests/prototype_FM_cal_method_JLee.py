# -*- coding: utf-8 -*-
"""
@author: Jlee
Created: Jan 26, 2022

Description: Script processes picoLog file from Prototype during a pump calibration to load cell (Bubble Introduction and Dependencies.xlsx testing) 
to assess efficacy of FM calibration/validation with volume comparisons to load cell.  
"""

import numpy as np
import os
import time
import pandas as pd
# import scipy

# User information here.
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000617 - Bubble Introduction and Dependencies/Test Data'
testNum = 57
LC_slope = 0.998
LC_int = -1.099

# Analysis parameters.
dx = 0.001 # Integration time step. Unit seconds.
T = 60 # Duration of usable time to evaluate ramp-up and SS. Unit seconds.
SSoff1 = 300 # unit seconds. Offset from start of first formulation. For SS reference values of system.
SSoff2 = 60 # unit seconds. Offset from end of run. For SS reference values of system.
segN = 5000 # unit index. Bin times to average min/maxes.

tic = time.time()
# test = str(TFR)+"_"+str(ratio)
test = str(testNum)

os.chdir(pathName)
for filename in os.listdir(pathName):
    if test and '.csv' and 'JLee' in filename:
        
        # Initialize variables.
        tStart = -99 # Detected start of ramp up. Unit seconds.
        nStart = -99 # Detected start of ramp up, index.
        ssFrAqMaxArr = np.array([])
        ssFrAqMinArr = np.array([])
        ssFrAqAvgArr = np.array([])
        frAq = np.array([])
        tRU1 = -99
        tRU2= -99
        nRU1 = -99
        nRU2 = -99
        check = 1
        frAqAdj = np.array([])
        
        
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dt = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        # raw data.
        rawFrAq = dfRaw[:,2]
        rawLC = dfRaw[:,1]
        rawFrOrg = dfRaw[:,2]
        

        
        # Delete gaps in data. Specific to these early test runs on Prototype with PicoLogger.           
        frAqAdj = rawFrAq.astype(np.float) 
        LC_adj = rawLC.astype(np.float)
        frAqAdj = frAqAdj[~np.isnan(frAqAdj)]
        LC_adj = LC_adj[~np.isnan(LC_adj)]
        print('raw data adjusted.')
        
        # Find Steady State Formulation flow rates and pressures through each mixer.
        ssN1 = round(SSoff1/dt)
        ssN2 = rawFrAq.shape[0]-round(SSoff2/dt)
        ssN3 = round(T/dt)

        for i in range(ssN1,ssN2-segN,segN):
            ssFrAqMaxArr = np.append(ssFrAqMaxArr, np.max(rawFrAq[i:i+segN]))
            ssFrAqMinArr = np.append(ssFrAqMinArr, np.min(rawFrAq[i:i+segN]))
            ssFrAqAvgArr= np.append(ssFrAqAvgArr,np.mean(rawFrAq[i:i+segN]))
    
    
        # Remove nan entries and calculate min/max.
        
        ssFrAqMaxArr = ssFrAqMaxArr[~np.isnan(ssFrAqMaxArr)]
        ssFrAqMinArr = ssFrAqMinArr[~np.isnan(ssFrAqMinArr)]
        ssFrAqAvgArr = ssFrAqAvgArr[~np.isnan(ssFrAqAvgArr)]
        ssFrAqMax = np.mean(ssFrAqMaxArr)        
        ssFrAqMin = np.mean(ssFrAqMinArr) 
        ssFrAqAvg = np.mean(ssFrAqAvgArr) 
        
        # Detect start and end of ramp-up.
        frStart = 2 # unit ml/min.
        for i in range(0,60000,1):
            if rawFrAq[i]>frStart:
                nRU1 = i
                tRU1 = dt*nRU1
                break
        for i in range(nRU1,60000,1):
            if rawFrAq[i]>=0.95*ssFrAqAvg:
                for j in range(i,i+round(3*dt)):
                    if rawFrAq[j]<0.95*ssFrAqAvg:
                        check = 0
                        break
                    else:
                        check = 1
                if check == 1:
                    nRU2 = i
                    tRU2 = dt*nRU2
                    break
                else:
                    continue
        
        # Interval over which to do integration.
        n1 = nRU1
        n2 = nRU2
        t1 = n1*dt
        t2 = n2*dt
        dn = round(dx/dt)
        check_dn = np.mod(n2-n1,dn)
        if check_dn > 0:
            print('dn not evenly distributed')
        
        # LC mass.
        LC1 = LC_adj[n1]*LC_slope+LC_int
        LC2 = LC_adj[n2]*LC_slope+LC_int
        LC_dm = LC2-LC1
        
        # Trapezoidal rule to integrate FM flow rate for volume.
        trapzsum = 0
        for i in range(n1+dn,n2-dn,dn):
            if np.isnan(frAqAdj[i]):
                continue
            else:  
                trapzsum = trapzsum+frAqAdj[i]
        trapzInt = 0.5*(2*trapzsum+frAqAdj[n1]+frAqAdj[n2])*(dx)/60
        print('Trapz integration done')
        # Simpson rule to integrate FM flow rate for volume.
        check_sim = 0
        simsum = 0
        simsumArr = np.array([])
        for i in range(n1+dn,n2-dn,dn):
            if check_sim == 0:
                simsum = simsum + 4*frAqAdj[i]
                simsumArr = np.append(simsumArr,frAqAdj[i])
                check_sim = 1
            else:
                simsum = simsum + 2*frAqAdj[i]
                simsumArr = np.append(simsumArr,frAqAdj[i])
                check_sim = 0
        simInt = (frAqAdj[n1] + simsum + frAqAdj[n2])*dx/3/60
        
        # Compile results.
        results = np.vstack((testNum, dx,t2-t1,LC_dm, trapzInt, simInt))
        
            
        
                    
                
        
        

        print('test '+test+' done: '+str(time.time()-tic))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        