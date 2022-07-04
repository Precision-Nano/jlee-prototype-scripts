# -*- coding: utf-8 -*-
"""
Created on Wed Feb  2 09:39:12 2022

Description: Process NG's long run flow meter tests on Prototype with load cell and 505L pump.

@author: Jlee
"""

import numpy as np
import os 
from scipy import io
import time
import pandas as pd
from scipy.integrate import simps, romb
import matplotlib.pyplot as plt


pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000679 Prototype Flowmeter Drift/Test Data'
testStart = '86'
testEnd = testStart
test = testStart
testnum = int(test)

wsCFs =  451.3478421 # from load cell calibration.
wsCFi =  0.013592749 #from load cell calibration.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).

# Test specific parameters.
t_top = 399 # unit seconds. Test 39
t_bot = 560 # unit seconds. Test 39
fillcycle = 7
# threshP = .2
threshSt = 0.4
threshEnd = 1.6
threshInc = 0.2
t_filt = 10 # unit seconds.


# Index for future reference.
'''
t_top = 556 # unit seconds. Test 23
t_bot = 1097 # unit seconds. Test 23
t_top = 1461 # unit seconds. Test 24
t_bot = 2290 # unit seconds. Test 24
t_top = 1630 # unit seconds. Test 26
t_bot = 1790 # unit seconds. Test 26
t_top = 397 # unit seconds. Test 27
t_bot = 586 # unit seconds. Test 27
'''

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if test in filename and '.mat' in filename and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        LCdm = np.array([])
        LCdt = np.array([])
        LCfr = np.array([])
        n1 = 0
        n2 = 0
        t1 = 0
        t2 = 0
        m1 = 0
        m2 = 0
        LCfr = 0
        resultsArr = np.array([])
        resultsArr2 = np.array([])
        resultsAll = np.array([])
       
        
        # Load raw data.
        rawData = io.loadmat(filename)
        rawFM = rawData['A'] # flowmeter
        rawLC = rawData['B'] # load cell.
        dt = rawData['Tinterval'][0,0]
        
        wsAvgN = round(wsAvgT/dt)
        n_top = round(t_top/dt)
        n_bot= round(t_bot/dt)
        
        # Determine SS load cell values & thresholds.
        LC_top = np.mean(rawLC[n_top-wsAvgN:n_top+wsAvgN])
        LC_bot = np.mean(rawLC[n_bot-wsAvgN:n_bot+wsAvgN])

        threshN = int((threshEnd-threshSt)/threshInc+1)
        
        check_thresh = 0
        for p in np.arange(threshSt, threshEnd+0.0001, threshInc):
            LCthresh1 = (1+p)*LC_bot
            LCthresh2 = (1-0.03)*LC_top
            
            
            t_off = 0
            n_off = 0
            fillcount = 0
            # Loop through each fill cycle
            # for i in range(1,fillcycle):
            #     n1 = 0
            #     n2 = 0
            #     t1 = 0
            #     t2 = 0
            #     m1 = 0
            #     m2 = 0
            #     LCfr = 0
            # Search for start/end of fill. Then jump ahead to start next search for fill.
            
            for j in range(0,rawLC.shape[0]):
                if rawLC[j+n_off]>LCthresh1 and fillcount < fillcycle:
                    n1 = 0
                    n2 = 0
                    t1 = 0
                    t2 = 0
                    m1 = 0
                    m2 = 0
                    LCfr = 0
                    
                    
                    n1 = j+n_off
                    t1 = dt*n1
                    m1 = np.mean(rawLC[n1-wsAvgN:n1+wsAvgN])*wsCFs+wsCFi
                    for k in range(n1,n1+round(6*60/dt)): # Note have to change check time depending on fill time.
                        if rawLC[k]>LCthresh2:
                            n2 = k
                            t2 = dt*n2
                            m2 = np.mean(rawLC[k-wsAvgN:k+wsAvgN])*wsCFs+wsCFi 
                            T = t2-t1
                            dm = m2-m1
                            
                            LCfr = (m2-m1)/(t2-t1)*60
                            FMfr = (np.mean(rawFM[n1:n2])-1)*800/4
                            x = np.linspace(t1,t2,round((t2-t1)/dt))
                            mArr = rawLC[n1:n2]*wsCFs
                            mArr = mArr+1
                            LCfr2 = np.polyfit(x,mArr,1)
                            LCfr2 = LCfr2[0][0]*60
                            
                            #Integration method for volume.
                            LCdm = m2-m1
                            fr_trapz10 = rawFM[::10]
                            FM_trapz = (rawFM[n1:n2]-1)*800/4
                            FMdm1_trapz = np.trapz(FM_trapz[:,0])/60*dt
                            FMdm_10 = np.trapz(FM_trapz[0:round(FM_trapz.shape[0]/10),0])/60*dt
                            FMdm1_simp = simps(FM_trapz[:,0])/60*dt
                            
                            # Create regression plot. Filter for every 1s.
                            x1 = np.linspace(round(t1), round(t2), round((t2-t1)/t_filt))
                            LC_plot = rawLC[round(t1/dt):round(t2/dt)]*wsCFs+wsCFi
                            LC_filt = np.array([])
                            # filt_count = filt_thresh
                            # filt_thresh = round(t_filt/dt)
                            for i in range(0,x1.shape[0]):
                                i1 = x1[i]
                                LC_filt = np.append(LC_filt, np.mean(rawLC[round(i1/dt-t_filt/2/dt):round(i1/dt+t_filt/2/dt)])*wsCFs+wsCFi)
                                
                            # fig1 = plt.plot(x,LC_plot,'o')
                            # m,b = np.polyfit(x,LC_plot,1)
                            # fig1 = plt.plot(x, m*x+b)
                            # fig1.set_xlim([0,100])
                            
                            fig2 = plt.plot(x1,LC_filt,'o')
                            m1,b1 = np.polyfit(x1,LC_filt,1)
                            fig2 = plt.plot(x1, m1*x1+b1)
                            fig2 = plt.title('Filtered mass v. time during fill for')
    
                            
    
                            # t1_hrs = t1/3600
                            resultsArr = np.append(resultsArr,(testnum, p, t1,t2, T, m1,m2, LCfr,LCfr2, FMfr, LCdm, FMdm1_trapz, FMdm1_simp))
                            
                            fillcount += 1 
                            n_off = 0
                            n_off = n2+round(5*60/dt) # Note have to change according to next fill time.
                            break
                if fillcount == fillcycle:
                    check_thresh += 1
                    break
                
        resultsAll2 = np.reshape(resultsArr,(fillcycle*int(threshN),13))
                        
                
                            
                            
                            
                    
                    
        
        
        
        
        
        