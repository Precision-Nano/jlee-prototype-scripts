# -*- coding: utf-8 -*-
"""

Description: Process Levitronix pump and Levitronix FM setup in wetlab for water-ethanol tests run by Paul Shen & Anastasia Lazic. (ENG-000680).
Test plan E, G. Compiled results in "resultsArr2".
Last updated: Mar 31, 2021

@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd



pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000680 - Levitronix flow meter tests for water-ethanol workflows/Data and Scripts/data'
testStart = '126'
testEnd = testStart
# testEnd = '137'
test = testStart

nameStr = 'T_'+test+'_'

# Test specific parameters.
wsCFs =  0.000250394 # from load cell calibration. Using microVolts, so slope is smaller than usual.
wsCFi =  0.730152798 # from load cell calibration.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).
thresh_rpm = 300 #unit rpm. When to consider pump ON.
thresh_fm = 0.05 # accuracy threshold.

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
        avgP = 0
        ssRPM = 0
        dLFM_err = np.array([])
        dBFM_err = np.array([])
        n1_dLFM = n1_dBFM = 0
        t1_dLFM = t1_dBFM = 0
        dLFM_err_count = dBFM_err_count = 0
        
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dt = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        rawLFM = dfRaw[:,2]
        rawBFM = dfRaw[:,5]
        rawLC = dfRaw[:,1]
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
        tEnd2 = tEndp - 10
        nEnd2 = round(tEnd2/dt)
        
        # find pump ON time. ********* sometimes need to offset start of search.
        for i in range(0,rawPump.shape[0]): #usually start at 0.
            if rawPump[i]> thresh_rpm:
                nPumpi = i
                tPumpi = nPumpi*dt
                break
            
        ssRPM = np.mean(rawPump[nEnd2-wsAvgN:nEnd2+wsAvgN])
        avgP = np.mean(rawP[nEnd2-wsAvgN:nEnd2+wsAvgN])
            
        
        
        # # manual intervention to find end time for config A.*********
        # for i in range(round(540000),1,-1):
        #     if rawPump[i]> 50:
        #         nEndp = i
        #         tEndp = i*dt
        #         break
        # tEnd2 = tEndp - 10
        # nEnd2 = round(tEnd2/dt)  
        
                
        # Find SS values near end of dataset.*********
        n_ss = nEnd2
          
        ssLFM = np.mean(rawLFM[n_ss-wsAvgN:n_ss+wsAvgN])
        ssBFM = np.mean(rawBFM[n_ss-wsAvgN:n_ss+wsAvgN])
        
        # Find flow meters' individual steady state times. 
        def find_FMSS(rawFM, ssFM,thresh, n1, n_ss):
            for i in range(n1,n_ss):
                if rawFM[i] > ssFM*(1-thresh):
                    check_FM = rawFM[i:i+round(9/dt)]
                    if all(j > ssFM*(1-thresh) for j in check_FM):
                        n1 = i
                        t1 = n1*dt
                        return n1, t1
                        break
        
        [n1_LFM, t1_LFM] = find_FMSS(rawLFM, ssLFM, 0.1, nPumpi, n_ss)
        [n1_BFM, t1_BFM] = find_FMSS(rawBFM, ssBFM, 0.1, nPumpi, n_ss)
        
        # Alternate method for finding SS in LFM. FR rate of change. Also find out how long between bubble errors.
        def find_dFMss(rawFM, thresh_fm, nPumpi):
            FM_diff = np.diff(rawFM)
            FM_pdiff = abs(FM_diff/(rawFM[:-1]+0.0000000001))
            Err = 0
            Err_dt = np.array([])
            
            for i in range(nPumpi,FM_pdiff.shape[0]):
                # Detect dips from bubble errors.
                if FM_pdiff[i] > 0.3:
                    Err += 1
                    Err_dt = np.append(Err_dt, i)
                # Detect ss.
                if FM_pdiff[i]<= thresh_fm:
                    check_dFM = FM_pdiff[i:i+round(10/dt)]
                    if all(j < thresh_fm for j in check_dFM):
                        dFM_n1 = i
                        dFM_t1 = dFM_n1*dt
                        #convert bubble errors to change in time based.
                        Err_dt = Err_dt*dt
                        Err_dt_diff = np.diff(Err_dt)
                        Err_dt_diff = Err_dt_diff[Err_dt_diff > 0.1]
                        return dFM_n1, dFM_t1, Err_dt_diff, Err
                        break
        [n1_dLFM, t1_dLFM, dLFM_err, dLFM_err_count] = find_dFMss(rawLFM, thresh_fm, nPumpi)
        [n1_dBFM, t1_dBFM, dBFM_err, dBFM_err_count] = find_dFMss(rawBFM, thresh_fm, nPumpi)
        # max time between bubble/flow errors.
        if dLFM_err.shape[0]>0:    
            maxErr_LFM = np.max(dLFM_err)
        else:
            maxErr_LFM = -99
        if dBFM_err.shape[0]>0:
            maxErr_BFM= np.max(dBFM_err)
        else:
            maxErr_BFM = -99
        
        
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
        
        # Find temperature at start, middle and end of SS (for config D).
        temp1 = np.mean(rawT[n1_LFM-wsAvgN:n1_LFM+wsAvgN])
        temp2 = np.mean(rawT[round((n1_LFM+nEnd2)/2)-wsAvgN:round((n1_LFM+nEnd2)/2)+wsAvgN])
        temp3 = np.mean(rawT[nEnd2-wsAvgN:nEnd2+wsAvgN])
        
        
        # Find load cell start of flow to bag.
        thresh_LC = 200000 #unit microvolts. Threshold above starting state to indicate flow.
        v1 = np.mean(rawLC[round(10/dt):round(15/dt)]) #******** usually 10 and 15s.
        for i in range(round(55/dt),rawLC.shape[0]):
            if rawLC[i]>v1+thresh_LC:
                n1_LC = i
                t1_LC = i*dt
                break
            
            
        
        # Find load cell avg flow rate.
        n2_LC = nEnd2
        t2_LC = n2_LC*dt
        m1 = np.mean(rawLC[n1_LC-wsAvgN:n1_LC+wsAvgN])*wsCFs+wsCFi
        m2 = np.mean(rawLC[n2_LC-wsAvgN:n2_LC+wsAvgN])*wsCFs+wsCFi
        dm = m2-m1
        LCfr = (dm)*60/(t2_LC-t1_LC)
        
        
        
        
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
        cstInd= filename.index('cSt') # for G.
        cst = filename[minInd+4:cstInd] # for G.
        
        
        
        
        
        resultsArr = np.hstack((testNum, wat, eth, cst, ssRPM, tPumpi, t1_LFM, t1_BFM, t1_dLFM, t1_dBFM, maxErr_LFM, maxErr_BFM, tEnd2, ssLFM, ssBFM, min_LFM, min_BFM, max_LFM, max_BFM, t1_LC, t2_LC, dm, LCfr, avgP, temp2))
        resultsArr = np.transpose(resultsArr)
        resultsArr = np.reshape(resultsArr, (1,resultsArr.shape[0]))
        resultsArr2 = np.append(resultsArr2, resultsArr)
        
        print ('test '+test+ ' done.')
        print(filename)
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T_'+test+'_'
        
        
        
    

resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
       
        
        
                
                            
                            
                            
                    
                    
        
        
        
        
        
        