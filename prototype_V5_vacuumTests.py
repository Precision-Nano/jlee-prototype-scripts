# -*- coding: utf-8 -*-
"""

Description: Calibration through Promass flow meter. ENG-000810. Final results in "resultsArr".
Last updated: Jun 13, 22.
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000810 WM Peristaltic Pump Vacuum/PLC files'

testStart = '7' # PLC test number



testEnd = testStart
# testEnd = '6'
test = testStart
nameStr = '_T'+test+ '_cleaned.csv' # Format for "Manual gravity flood II" folder.




# Test specific parameters.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).
thresh_rpm = 300 #unit rpm. When to consider pump ON.
thresh_fm = 0.05 # accuracy threshold.




# Initialize variables.
resultsArr = np.array([])
resultsArr2 = np.array([])

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if nameStr in filename and 'PLC_FastLog_V5_' and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        # resultsArr = np.array([])

    
        # Load csv file from PLC.
        df = pd.read_csv(filename)
        dfRaw = pd.DataFrame(df).to_numpy()
        rawT = dfRaw[:,0].astype(np.float)
        rawAq_set_fr = dfRaw[:,1].astype(np.float)
        rawAq_rpm = dfRaw[:,3].astype(np.float)
        rawAq_fr = dfRaw[:,5].astype(np.float)
        rawAq_err = dfRaw[:,6].astype(np.float)
        rawAq_p = dfRaw[:,7].astype(np.float)
        rawOrg_set_fr = dfRaw[:,8].astype(np.float)
        rawOrg_rpm = dfRaw[:,10].astype(np.float)
        rawOrg_fr = dfRaw[:,12].astype(np.float)
        rawOrg_err = dfRaw[:,13].astype(np.float)
        rawOrg_p = dfRaw[:,14].astype(np.float)
        rawDil_set_fr = dfRaw[:,15].astype(np.float)
        rawDil_rpm = dfRaw[:,17].astype(np.float)
        rawDil_fr = dfRaw[:,19].astype(np.float)
        rawDil_err = dfRaw[:,20].astype(np.float)
        rawCFM_fr = dfRaw[:,21].astype(np.float)
        rawCFM_den = dfRaw[:,22].astype(np.float)
        rawCFM_p = dfRaw[:,23].astype(np.float)
        rawLC = dfRaw[:,24].astype(np.float)
        raw_vp = dfRaw[:,25].astype(np.float)
        rawAirp = dfRaw[:,26].astype(np.float)
        V1_cmd = dfRaw[:,27].astype(np.float)
        V2_cmd = dfRaw[:,28].astype(np.float)
        V3_cmd = dfRaw[:,29].astype(np.float)
        V4_cmd = dfRaw[:,30].astype(np.float)
        V5_cmd = dfRaw[:,31].astype(np.float)
        V6_cmd = dfRaw[:,32].astype(np.float)
        V7_cmd = dfRaw[:,33].astype(np.float)
        V8_cmd = dfRaw[:,34].astype(np.float)
        V1_close = dfRaw[:,35].astype(np.float)
        V2_close = dfRaw[:,36].astype(np.float)
        V3_close = dfRaw[:,37].astype(np.float)
        V4_close = dfRaw[:,38].astype(np.float)
        V5_close = dfRaw[:,39].astype(np.float)
        V6_close = dfRaw[:,40].astype(np.float)
        V7_close = dfRaw[:,41].astype(np.float)
        V8_close = dfRaw[:,42].astype(np.float)
        V1_open = dfRaw[:,43].astype(np.float)
        V2_open = dfRaw[:,44].astype(np.float)
        V3_open = dfRaw[:,45].astype(np.float)
        V4_open = dfRaw[:,46].astype(np.float)
        V5_open = dfRaw[:,47].astype(np.float)
        V6_open = dfRaw[:,48].astype(np.float)
        V7_open = dfRaw[:,49].astype(np.float)
        V8_open = dfRaw[:,50].astype(np.float)
      

        dt = np.mean(np.diff(rawT))/1000 # unit seconds.
        
        # calculate average pressure from vaccuum gauge and other characteristics at SS pressure.
        t_ss = 60 # unit seconds. user identified.
        t_avg = 10 # unit seconds. Average +/- 1/2 time on either side of target time.
        n_st = np.where(V4_cmd == 1)[0][0]
        t_st = rawT[n_st]/1000
        t_ss_adj = t_ss + t_st
        n_ss_adj = np.where(rawT >=t_ss_adj*1000)[0][0]
        t_ss_adj = rawT[n_ss_adj]/1000
        t_ss_1 = t_ss_adj - t_avg/2
        t_ss_2 = t_ss_adj+t_avg/2
        n_ss_1 = np.where(rawT >= t_ss_1*1000)[0][0]
        n_ss_2 = np.where(rawT >= t_ss_2*1000)[0][0]
        
        # average results.
        vP_avg = np.mean(raw_vp[n_ss_1:n_ss_2])
        fr_avg = np.mean(rawOrg_fr[n_ss_1:n_ss_2])
        rpm_avg = np.mean(rawOrg_rpm[n_ss_1:n_ss_2])
        
        #compile results.
        resultsArr = np.vstack((testNum, t_ss_adj, vP_avg, fr_avg, rpm_avg))
        resultsArr = np.transpose(resultsArr)
        resultsArr2 = np.append(resultsArr2, resultsArr)   

                    
        
        
      
        
        print (filename + ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        