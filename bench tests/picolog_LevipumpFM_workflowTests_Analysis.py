# -*- coding: utf-8 -*-
"""

Description: Process Levitronix pump and Levitronix FM setup in wetlab for water-ethanol tests run by Paul Shen & Anastasia Lazic. (ENG-000680).
Last updated: Feb 16, 2021

@author: Jlee
"""

import numpy as np
import os 
from scipy import io
import time
import pandas as pd
from scipy.integrate import simps, romb
import matplotlib.pyplot as plt


pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000680 - Levitronix flow meter tests for water-ethanol workflows/Data and Scripts/data'
testStart = '2'
testEnd = testStart
test = testStart
# testnum = int(test)



# Test specific parameters.
ssOff_end = 60 # unit seconds.
wsCFs =  0.000249491 # from load cell calibration. Using microVolts, so slope is smaller than usual.
wsCFi =  -0.371683686 #from load cell calibration.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).



tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if test in filename and '_100Wat_0Eth.csv' in filename and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        resultsArr = np.array([])

        
        # Load raw data.
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dt = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        rawLFM = dfRaw[:,2]
        rawBFM = dfRaw[:,5]
        rawLC = dfRaw[:,1]
        rawSFM = dfRaw[:,7]
        rawPump = dfRaw[:,3]
        rawP = dfRaw[:,4]
        rawT = dfRaw[:,6]
        
        
        wsAvgN = round(wsAvgT/dt)
        nEnd = rawLFM.shape[0]-round(ssOff_end/dt)        
        # Find SS values from middle of dataset.
        n_mid = round(rawLFM.shape[0]/2)
        ssLFM = np.mean(rawLFM[n_mid-wsAvgN:n_mid+wsAvgN])
        ssBFM = np.mean(rawBFM[n_mid-wsAvgN:n_mid+wsAvgN])
        ssSFM = np.mean(rawSFM[n_mid-wsAvgN:n_mid+wsAvgN])
        
        # Find flow meters' individual steady state times. 
        def find_FMSS(rawFM, ssFM,thresh):
            for i in range(0,n_mid):
                if rawFM[i] > ssFM*(1-thresh):
                    check_FM = rawFM[i:i+round(3/dt)]
                    if all(j > ssFM*(1-thresh) for j in check_FM):
                        n1 = i
                        t1 = n1*dt
                        return n1, t1
                        break
        
        [n1_LFM, t1_LFM] = find_FMSS(rawLFM, ssLFM, 0.05)
        [n1_BFM, t1_BFM] = find_FMSS(rawBFM, ssBFM, 0.05)
        [n1_SFM, t1_SFM] = find_FMSS(rawSFM, ssSFM, 0.4)
        
        # Find min/max throughout test time.
        def find_FM_hilo(rawFM, n1,n2, tSeg):
            count = 0
            nSeg = round(tSeg/dt)
            maxArr = np.array([])
            minArr = np.array([])
            for i in range(n1,n2):
                if count >= nSeg:
                    maxArr = np.append(maxArr, np.max(rawFM[i-nSeg+1:i]))
                    minArr = np.append(minArr, np.min(rawFM[i-nSeg+1:i]))
                    count = 0
                count+= 1
            FM_max = np.mean(maxArr)
            FM_min = np.mean(minArr)
            return FM_min, FM_max, minArr, maxArr
        
        [min_LFM, max_LFM, minArr_LFM, maxArr_LFM] = find_FM_hilo(rawLFM, n1_LFM, nEnd, 4)
        [min_BFM, max_BFM, minArr_BFM, maxArr_BFM] = find_FM_hilo(rawBFM, n1_BFM, nEnd, 4)
        [min_SFM, max_SFM, minArr_SFM, maxArr_SFM] = find_FM_hilo(rawSFM, n1_SFM, nEnd, 4)
                    
        
        # Find load cell avg flow rate.
        n1_LC = n1_LFM
        n2_LC = rawLC.shape[0]-round(ssOff_end)
        t1_LC = n1_LC*dt
        t2_LC = n2_LC*dt
        m1 = np.mean(rawLC[n1_LC-wsAvgN:n1_LC+wsAvgN]*wsCFs+wsCFi)
        m2 = np.mean(rawLC[n2_LC-wsAvgN:n2_LC+wsAvgN]*wsCFs+wsCFi)
        LCfr = (m2-m1)/(t2_LC-t1_LC)*60    
        
        # print('progress')
        
        tEnd = nEnd*dt
        resultsArr = np.hstack((testNum, t1_LFM, t1_BFM, t1_SFM, tEnd, ssLFM, ssBFM, ssSFM, min_LFM, min_BFM, min_SFM, max_LFM, max_BFM, max_SFM, LCfr))
        print ('test '+testStart+ ' done.')
        
        testNum +=1 
        test = str(testNum)
       
        
        
                
                            
                            
                            
                    
                    
        
        
        
        
        
        