# -*- coding: utf-8 -*-
"""

Description: Process Levitronix pump and Levitronix FM setup in wetlab for water-ethanol tests run by Paul Shen & Anastasia Lazic. (ENG-000680).
Last updated: Feb 18, 2021

@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd



pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000680 - Levitronix flow meter tests for water-ethanol workflows/Data and Scripts/data'
testStart = '26'
testEnd = testStart
# testEnd = '24'
test = testStart

nameStr = 'T_'+test+'_'

# Test specific parameters.
wsCFs =  0.000249491 # from load cell calibration. Using microVolts, so slope is smaller than usual.
wsCFi =  -0.371683686 # from load cell calibration.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).
thresh_rpm = 300 #unit rpm. When to consider pump ON.


# Initialize variables.
resultsArr2 = np.array([])

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if nameStr in filename and 'Eth.csv' in filename and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        resultsArr = np.array([])
        ssLFM = 0
        ssBFM = 0
        ssSFM = 0
        n1_LC = 0
        n2_LC = 0
        t1_LC = 0
        t2_LC = 0
        m1 = 0
        m2 = 0
        LCfr = 0
        rawLFM = np.array([])
        rawBFM = np.array([])
        rawLC = np.array([])
        rawSFM = np.array([])
        rawPump = np.array([])
        rawP = np.array([])
        rawT = np.array([])
        min_LFM = max_LFM = 0
        minArr_LFM = maxArr_LFM = np.array([])
        min_BFM = max_BFM = 0
        minArr_BFM = maxArr_BFM = np.array([])
        min_SFM = max_SFM = 0
        minArr_SFM = maxArr_SFM = np.array([])
        n1_LFM = t1_LFM = 0
        n1_BFM = t1_BFM = 0
        n1_SFM = t1_SFM = 0
        
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
        
        
        # find end time via pump rpm.*********
        for i in range(rawPump.shape[0]-1,-1,-1):
            if rawPump[i]> 50:
                nEndp = i
                tEndp = i*dt
                break
        tEnd2 = tEndp - 15
        nEnd2 = round(tEnd2/dt)
        
        # # manual intervention to find end time for config A.*********
        # for i in range(round(540000),1,-1):
        #     if rawPump[i]> 50:
        #         nEndp = i
        #         tEndp = i*dt
        #         break
        # tEnd2 = tEndp - 10
        # nEnd2 = round(tEnd2/dt)  
        
        # find pump ON time.
        for i in range(0,rawPump.shape[0]):
            if rawPump[i]> thresh_rpm:
                nPumpi = i
                tPumpi = nPumpi*dt
                break
        
                
        # Find SS values from middle of dataset.*********
        n_mid = round(rawLFM.shape[0]/2)
        
        # SS values manual for config A.***********
        # n_mid = round(75/dt)
        
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
        [n1_SFM, t1_SFM] = find_FMSS(rawSFM, ssSFM, 0.6)
        
        
        # Find number of Levitronix flow meter errors (bubbles, improper fluid properties.). Config A.***
        # ErrCount = 0
        # for i in range(0,round(30/dt)):
        #     if rawPump[i]>50:
        #         n1_bub = i
        #         t1_bub = n1_bub*dt
        #         break
        # for i in range(n1_bub,nEnd2):
        #     if rawLFM[i] < 20:
        #         ErrCount += 1
        # #total bubble error time.
        # ErrTime = ErrCount*dt

        
        
        # Find min/max throughout test time.
        def find_FM_hilo(rawFM,n1,n2,tSeg):
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
        
        [min_LFM, max_LFM, minArr_LFM, maxArr_LFM] = find_FM_hilo(rawLFM, n1_LFM, nEnd2, 4)
        [min_BFM, max_BFM, minArr_BFM, maxArr_BFM] = find_FM_hilo(rawBFM, n1_BFM, nEnd2, 4)
        [min_SFM, max_SFM, minArr_SFM, maxArr_SFM] = find_FM_hilo(rawSFM, n1_SFM, nEnd2, 4)
        
        # Find temperature at start, middle and end of SS (for config D).
        temp1 = np.mean(rawT[n1_LFM-wsAvgN:n1_LFM+wsAvgN])
        temp2 = np.mean(rawT[round((n1_LFM+nEnd2)/2)-wsAvgN:round((n1_LFM+nEnd2)/2)+wsAvgN])
        temp3 = np.mean(rawT[nEnd2-wsAvgN:nEnd2+wsAvgN])
        
        

            
        
        # Find load cell avg flow rate.
        n1_LC = n1_LFM
        n2_LC = nEnd2
        t1_LC = n1_LC*dt
        t2_LC = n2_LC*dt
        m1 = np.mean(rawLC[n1_LC-wsAvgN:n1_LC+wsAvgN])*wsCFs+wsCFi
        m2 = np.mean(rawLC[n2_LC-wsAvgN:n2_LC+wsAvgN])*wsCFs+wsCFi
        LCfr = (m2-m1)/(t2_LC-t1_LC)*60    
        
        
        
        
        #Find water/ethanol mixture in filename. 
        watInd = filename.find('Wat_')
        ethInd = filename.find('Eth')
        minInd = filename.find('min_')
        eth = filename[watInd+4:ethInd]
        mlInd = filename.find('ml')
        ind1 = filename.find('_',2)
        ind2 = filename.find('_',3)
        wat = filename[minInd+4:watInd] # for C&D.
        # wat = filename[ind2+1:watInd] # for A.
        tarFR = filename[ind1+1:mlInd] #for C&D.
        # tarFR = filename[ind1+1:ind2] #for A.
        
        
        
        resultsArr = np.hstack((testNum, tarFR, wat, eth, tPumpi, t1_LFM, t1_BFM, t1_SFM, tEnd2, ssLFM, ssBFM, ssSFM, min_LFM, min_BFM, min_SFM, max_LFM, max_BFM, max_SFM, LCfr, temp1, temp2, temp3))
        # resultsArr = np.transpose(resultsArr)
        resultsArr = np.reshape(resultsArr, (1,resultsArr.shape[0]))
        resultsArr2 = np.append(resultsArr2, resultsArr)
        
        print ('test '+test+ ' done.')
        print(filename)
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T_'+test+'_'
        
        
        
    

resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
       
        
        
                
                            
                            
                            
                    
                    
        
        
        
        
        
        