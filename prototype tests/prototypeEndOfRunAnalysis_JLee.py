# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 10:18:46 2021

@author: Jlee
"""

"""
Description: Script processes picoLog file from Prototype (back-flushing fluid path, valve array) to 
"""

import numpy as np
import os
import time
import pandas as pd

# User information here.
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000621 Prototype Backflushing Initial Testing/Data/Picologger Files'
testNum = 1
pFilter = 1 #unit seconds. Filter time of raw pressure reading.
fmFilter = 0.5 #unit seconds. Filter time of raw flow meter reading.
# TFR = 200 #test identifier.
# ratio = 3 #:1 formulation ratio.

# Identify steady state references.
SSoff1 = 60 # unit seconds. Offset from start of first formulation. For SS reference values of system.
SSoff2 = 90 # unit seconds. Offset from end of run. For SS reference values of system.
segN = 5000 # unit milliseconds. Bin times to average min/maxes.

tic = time.time()
# test = str(TFR)+"_"+str(ratio)
test = 'end_of_run'+str(testNum)+'.csv'

os.chdir(pathName)
for filename in os.listdir(pathName):
    if test in filename:
        
        # Initialize variables.
        F1i = np.array([])
        F1f = np.array([])
        F2i = np.array([])
        F2f = np.array([])
        ssFrAq1 = np.array([])
        ssFrOrg1 = np.array([])
        ssPAq1 = np.array([])
        ssPOrg1 = np.array([])
        ssFrAq2 = np.array([])
        ssFrOrg2 = np.array([])
        ssPAq2 = np.array([])
        ssPOrg2 = np.array([])
        flushB2 = np.array([])
    
        
        
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dt = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        
        rawFrAq = dfRaw[:,1]
        rawFrOrg = dfRaw[:,2]
        v1a = dfRaw[:,3]#.astype(int)
        v1b = dfRaw[:,4]#.astype(int)
        v2a = dfRaw[:,5]#.astype(int)
        v2b = dfRaw[:,6]#.astype(int)
        v3a = dfRaw[:,7]#.astype(int)
        v3b = dfRaw[:,8]#.astype(int)
        v4a = dfRaw[:,9]#.astype(int)
        v4b = dfRaw[:,10]#.astype(int)
        v5a = dfRaw[:,11]#.astype(int)
        v5b = dfRaw[:,12]#.astype(int)
        v6a = dfRaw[:,13]#.astype(int)
        v6b = dfRaw[:,14]#.astype(int)
        v7a = dfRaw[:,15]#.astype(int)
        v7b = dfRaw[:,16]#.astype(int)
        v9a = dfRaw[:,17]#.astype(int)
        v9b = dfRaw[:,18]#.astype(int)
        rawPAq = dfRaw[:,27]
        rawPOrg = dfRaw[:,28]
        rawPCle = dfRaw[:,29]
        rawPDil = dfRaw[:,30]
        rawPAir = dfRaw[:,31]
        rawFrDil = dfRaw[:,32]
        rawFrCle = dfRaw[:,33]
        rawLC = dfRaw[:,34]
        
    
        # Find Steady State Formulation flow rates and pressures through each mixer.
        ssN1 = round(SSoff1/dt)
        ssN2 = rawFrAq.shape[0]-round(SSoff2/dt)
        ssFrAq = np.mean(rawFrAq[ssN1:ssN2])
        ssFrAqMax = np.max(rawFrAq[ssN1:ssN2])
        ssFrAqMin = np.min(rawFrAq[ssN1:ssN2])
        ssFrOrg = np.mean(rawFrOrg[ssN1:ssN2])
        ssFrOrgMax = np.max(rawFrOrg[ssN1:ssN2])
        ssFrOrgMin = np.min(rawFrOrg[ssN1:ssN2])
        ssPaq = np.mean(rawPAq[ssN1:ssN2])
        ssPaq = np.max(rawPAq[ssN1:ssN2])
        ssPaq = np.min(rawPAq[ssN1:ssN2])
        ssPorg = np.mean(rawPOrg[ssN1:ssN2])
        
        ssFrAqMaxArr = np.array([])
        ssFrAqMinArr = np.array([])
        ssFrOrgMaxArr = np.array([])
        ssFrOrgMinArr = np.array([])


        
        for i in range(ssN1,ssN2-segN,segN):
            ssFrAqMaxArr = np.append(ssFrAqMaxArr, np.max(rawFrAq[i:i+segN]))
            ssFrAqMinArr = np.append(ssFrAqMinArr, np.min(rawFrAq[i:i+segN]))
            ssFrOrgMinArr = np.append(ssFrOrgMinArr, np.min(rawFrOrg[i:i+segN]))
            ssFrOrgMaxArr = np.append(ssFrOrgMaxArr, np.max(rawFrOrg[i:i+segN]))
        ssFrAqMax = np.mean(ssFrAqMaxArr)    
        ssFrAqMin = np.mean(ssFrAqMinArr)        
        ssFrOrgMax = np.mean(ssFrOrgMaxArr)    
        ssFrOrgMin = np.mean(ssFrOrgMinArr)    
        
        devArr = np.arange(0.05,0.21,0.01,dtype=float)
        frAqArr_thresh = (1-devArr)*ssFrAq
        frOrgArr_thresh = (1-devArr)*ssFrOrg
        pAqArr_thresh = (1-devArr)*ssPaq
        pOrgArr_thresh = (1-devArr)*ssPorg

        def func_threshTimes(rawX, threshArr,n1,n2,tf,dt):
            tArr = np.array([])
            for i in range(0,threshArr.shape[0]):
                for j in range(n1,n2-round(tf/dt)):
                    avgX = np.mean(rawX[j-round(tf/dt):j])
                    if avgX < threshArr[i]:
                        tArr = np.append(tArr,j*dt)
                        break
            print('thresh array complete.')
            return tArr    
        
        frAqArr_threshTimes = func_threshTimes(rawFrAq, frAqArr_thresh, ssN2,rawFrAq.shape[0],fmFilter,dt)            
        frOrgArr_threshTimes = func_threshTimes(rawFrOrg, frOrgArr_thresh, ssN2,rawFrOrg.shape[0],fmFilter,dt)            
        # pAqArr_threshTimes = func_threshTimes(rawPAq, pAqArr_thresh, ssN2,rawPAq.shape[0],pFilter,dt)            
        # pOrgArr_threshTimes = func_threshTimes(rawPOrg, pOrgArr_thresh, ssN2,rawPOrg.shape[0],pFilter,dt)            
                        
          

        print('test '+test+' done: '+str(time.time()-tic))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        