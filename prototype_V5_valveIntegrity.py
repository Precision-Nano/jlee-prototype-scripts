# -*- coding: utf-8 -*-
"""

Description: Valve integrity test (pressurizing with air) through AQ pressure sensor. ENG-000805. Final results in "resultsArr".
Last updated: Jun 10, 22.
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd
# pd.set_option('display.float_format',lambda x: '%.9f' % x)


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000805 Install Fluid Path Workflow/PLC Data'

testStart = '19' # PLC test number
config = 1 # config 1 = A.3. config 2 = A.1

# testEnd = testStart
testEnd = '26'
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
        
        # Initialize variables.
        p_max = -99
        p_max_i = -99
        p_max_t = -99
        p_ini_i = -99
        p_ini_t = -99
        holdP_ini_i = -99
        holdP_ini_t = -99
        holdP_end_i = -99
        holdP_end_t = -99
        holdP_ini = -99
        holdP_end = -99
        holdP_dt = -99
    
        # calculate ramp-up to peak pressure.
        p_max = np.max(rawAq_p)
        p_max_i = rawAq_p.argmax()
        p_max_t = rawT[p_max_i]
        p_ini_i = np.where(rawAq_p >= 0)[0][0]
        p_ini_t = rawT[p_ini_i]
        ru_t = (p_max_t - p_ini_t)/1000
        
        # calculate decay over hold pressure time.
        holdP_ini_i = np.where(V4_cmd == 0)[0][0]+round(0.5/dt)
        holdP_ini_t = rawT[holdP_ini_i]/1000
        holdP_ini = rawAq_p[holdP_ini_i]

        holdP_end_i = np.where(V4_cmd == 0)[-1][-1]
        holdP_end_t = rawT[holdP_end_i]/1000
        holdP_end = rawAq_p[holdP_end_i]
        holdP_dt = holdP_end_t - holdP_ini_t
        holdP_dp = holdP_end - holdP_ini
        leakrate = holdP_dp/holdP_dt*60
        
        
        #compile results.
        resultsArr = np.vstack((testNum, ru_t, holdP_ini_t, holdP_end_t, holdP_dt, holdP_ini, holdP_end, holdP_dp, leakrate))
        resultsArr = np.transpose(resultsArr)
        resultsArr2 = np.append(resultsArr2, resultsArr)     

        
        print (filename + ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        