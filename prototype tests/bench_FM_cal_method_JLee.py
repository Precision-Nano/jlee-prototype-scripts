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
# import pandas as pd
from scipy import io
from scipy.integrate import simps, romb
# import matplotlib.pyplot as plt

# User information here.
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000555 - Levitronix flow meter testing/Test Data'
testNum = 165
LC_slope = 248.5258656
LC_int = -21.81439723

# Analysis parameters.
dx =0.01 # Integration time step. Unit seconds.
T = 60 # Duration of usable time to evaluate ramp-up and SS. Unit seconds.
SSoff1 = 45 # unit seconds. Offset from start of first formulation. For SS reference values of system.
SSoff2 = 10 # unit seconds. Offset from end of run. For SS reference values of system.
segN = 5000 # unit index. Bin times to average min/maxes.

tic = time.time()
# test = str(TFR)+"_"+str(ratio)
test = str(testNum)

os.chdir(pathName)
for filename in os.listdir(pathName):
    if 'T165_FG_4.3mA' in filename:
        
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
        

        # Load .mat file (from PicoScope).
        rawData = io.loadmat(filename)
        # chD = rawData['D'] # load cell.
        dt = rawData['Tinterval'][0,0]
        rawFrAq = rawData['B']*800/5 #flow rate.
        rawLC = rawData['D'] #load cell data.
        
           
        # Find Steady State Formulation flow rates and pressures through each mixer.
        ssN1 = round(SSoff1/dt)
        ssN2 = rawFrAq.shape[0]-round(SSoff2/dt)
        ssN3 = round(T/dt)

        for i in range(ssN1,ssN2-segN,segN):
            ssFrAqMaxArr = np.append(ssFrAqMaxArr, np.max(rawFrAq[i:i+segN]))
            ssFrAqMinArr = np.append(ssFrAqMinArr, np.min(rawFrAq[i:i+segN]))
            ssFrAqAvgArr= np.append(ssFrAqAvgArr,np.mean(rawFrAq[i:i+segN]))
    
    

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
        n1 = 38640
        n2 = ssN2-9932
        t1 = n1*dt
        t2 = n2*dt
        dn = round(dx/dt)
        check_dn = np.mod(n2-n1,dn)
        if check_dn > 0:
            print('dn not evenly distributed: '+str((n2-n1)))
            break
        
        # LC mass.
        LC1 = np.mean(rawLC[n1-round(3/dt):n1+round(3/dt),0]*LC_slope+LC_int)
        LC2 = np.mean(rawLC[n2-round(3/dt):n2+round(3/dt),0]*LC_slope+LC_int)
        LC_dm = LC2-LC1
        LC_fr = LC_dm/(t2-t1)*60
        
        # create subarrays to run trapz function through. (n-intervals)
        fr_trapz10 = rawFrAq[::10]
        fr_trapz100 = rawFrAq[::100]
        fr_trapz1000 = rawFrAq[::1000]
        

        # trapzsum = np.sum(rawFrAq[n1+dn:n2-dn])
        # trapzInt = 0.5*(2*trapzsum+rawFrAq[n1]+rawFrAq[n2])*(dx)/60  
        trapzInt2 = np.trapz(rawFrAq[n1:n2,0])/60*dt
        trapzInt10 = np.trapz(fr_trapz10[round(n1/10):round(n2/10),0])/60*dt*10
        trapzInt100 = np.trapz(fr_trapz100[round(n1/100):round(n2/100),0])/60*dt*100
        trapzInt1000 = np.trapz(fr_trapz1000[round(n1/1000):round(n2/1000),0])/60*dt*1000
        
        print('Trapz integration done')
        # Simpson rule to integrate FM flow rate for volume.
        # check_sim = 0
        # simsum = 0
        # simInt=0
        simInt2 = simps(rawFrAq[n1:n2,0])*dt/60
        simInt10 = simps(fr_trapz10[round(n1/10):round(n2/10),0])*dt/60*10
        simInt100 = simps(fr_trapz100[round(n1/100):round(n2/100),0])*dt/60*100
        simInt1000 = simps(fr_trapz1000[round(n1/1000):round(n2/1000),0])*dt/60*1000
        
        # simsumArr = np.array([])
        # for i in range(n1+dn,n2-dn,dn):
        #     if check_sim == 0:
        #         simsum = simsum + 4*rawFrAq[i]
        #         simsumArr = np.append(simsumArr,rawFrAq[i])
        #         check_sim = 1
        #     else:
        #         simsum = simsum + 2*rawFrAq[i]
        #         simsumArr = np.append(simsumArr,rawFrAq[i])
        #         check_sim = 0
        # simInt = (rawFrAq[n1] + simsum + rawFrAq[n2])*dx/3/60
        
        # Compile results.
        results = np.vstack((testNum, dx,t1, t2, t2-t1,LC_dm, trapzInt2, trapzInt10, trapzInt100, trapzInt1000, simInt2, simInt10, simInt100, simInt1000, LC_fr, ssFrAqAvg))
       
         # Plot differences.
        # x1 = np.linspace(t1,t2,n2-n1)
        # plt.plot(x1,rawFrAq[n1:n2,0])
            
        
                    
                
        
        

        print('test '+test+' done: '+str(time.time()-tic))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        