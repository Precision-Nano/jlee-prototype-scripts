# -*- coding: utf-8 -*-
"""
Created on Tue Nov 30 10:18:46 2021

@author: Jlee
"""

"""
Description: Script processes picoLog file from Prototype (back-flushing fluid path, valve array).
"""

import numpy as np
from scipy import io
import os
import time
import pandas as pd

# User information here.
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000561 Enfield Flow Capabilities/Data/12-01 10 Dil/Picologger Files'
TFR = 200 #test identifier.
ratio = 3 #:1 formulation ratio.

# Identify steady state references.
SSoff1 = 30 # unit seconds. Offset from start of first formulation. For SS reference values of system.
SSoff2 = 5 # unit seconds. Offset from end of first formulation. For SS reference values of system.

tic = time.time()
test = str(TFR)+"_"+str(ratio)

os.chdir(pathName)
for filename in os.listdir(pathName):
    if test in filename and '.csv' in filename:
        
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
        
    
        
        # Find Formulation start/end times for each mixer.
        F1Int = np.where(v5b == 1)[0]
        F2Int = np.where(v6b ==1)[0]
        F1i = np.append(F1i,F1Int[0])
        F2i = np.append(F2i,F2Int[0])
        for i in range(1,F1Int.shape[0]):
            if F1Int[i] != F1Int[i-1]+1:
                F1i = np.append(F1i, F1Int[i])
                F1f = np.append(F1f, F1Int[i-1])
        F1i = F1i[:-1]
        for i in range(1,F2Int.shape[0]):
            if F2Int[i] != F2Int[i-1]+1:
                F2i = np.append(F2i, F2Int[i])
                F2f = np.append(F2f, F2Int[i-1])
        F2i = F2i[:-1]       
        
        # Find Steady State Formulation flow rates and pressures through each mixer.
        
        for i in range(0,F1i.shape[0]):
            SSn1 = int(F1i[i]+round(SSoff1/dt))
            SSn2 = int(F1f[i]-round(SSoff2/dt))
            SSn3 = int(F2i[i]+round(SSoff1/dt))
            SSn4 = int(F2f[i]-round(SSoff2/dt))
            ssFrAq1 = np.append(ssFrAq1, np.mean(rawFrAq[SSn1:SSn2]))
            ssFrAq2 = np.append(ssFrAq2, np.mean(rawFrAq[SSn3:SSn4]))
            ssFrOrg1 = np.append(ssFrOrg1, np.mean(rawFrOrg[SSn1:SSn2]))
            ssFrOrg2 = np.append(ssFrOrg2, np.mean(rawFrOrg[SSn3:SSn4]))
            ssPAq1 = np.append(ssPAq1, np.mean(rawPAq[SSn1:SSn2]))
            ssPAq2 = np.append(ssPAq2, np.mean(rawPAq[SSn3:SSn4]))
            ssPOrg1 = np.append(ssPOrg1, np.mean(rawPOrg[SSn1:SSn2]))
            ssPOrg2 = np.append(ssPOrg2, np.mean(rawPOrg[SSn3:SSn4]))
        
        # # Find characteristics during backflush of aq line.
        # flushB2_int = np.where((v9b == 1) & (v1b == 1))[0]

        
        # for i in range(1,flushB2_int.shape[0]):
        #     if flushB2_int[i] != flushB2_int[i-1]:
        #         flushB2 = np.append(flushB2,i)
                
        
    
        

        print('test '+test+' done: '+str(time.time()-tic))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        