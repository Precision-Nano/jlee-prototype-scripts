# -*- coding: utf-8 -*-
"""

Description: Prototype fluid path schematic updated to calibrate with Bronkhorst FM (for now), with no switching. Script analyzes manual flooding tests (ENG-000730).
Compiled results in "resultsArr2".
Last updated: Apr 21, 22

@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000730 - Priming Sequence - Centrifugal Pumps/PLC files/Manual gravity flood'
# pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000730 - Priming Sequence - Centrifugal Pumps/PLC files/Manual gravity flood part II'
testStart = '6' # PLC test number
pump = 2 # 1=aq, 2=org, 3=dil pump.

# userTest = '2' # Test number  



testEnd = testStart
# testEnd = '137'
test = testStart
nameStr = 'PLC_FastLog_V4_'+test+'_cleaned' # Format for "Manual gravity flood" folder.
# nameStr = 'PLC_FastLog_V4_'+test+ '_T' # Format for "Manual gravity flood II" folder.




# Test specific parameters.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).
thresh_rpm = 300 #unit rpm. When to consider pump ON.
thresh_fm = 0.05 # accuracy threshold.




# Initialize variables.
resultsArr2 = np.array([])

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if nameStr in filename and '_cleaned.csv' in filename and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        resultsArr = np.array([])
        
        
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dfRaw = pd.DataFrame(df).to_numpy()
        rawT = dfRaw[1:,0].astype(np.float)
        rawAq_set_rpm = dfRaw[1:,2].astype(np.float)
        rawAq_rpm = dfRaw[1:,3].astype(np.float)
        rawAq_fr = dfRaw[1:,5].astype(np.float)
        rawAq_err = dfRaw[1:,6].astype(np.float)
        rawAq_p = dfRaw[1:,7].astype(np.float)
        rawOrg_set_rpm = dfRaw[1:,9].astype(np.float)
        rawOrg_rpm = dfRaw[1:,10].astype(np.float)
        rawOrg_fr = dfRaw[1:,12].astype(np.float)
        rawOrg_err = dfRaw[1:,13].astype(np.float)
        rawOrg_p = dfRaw[1:,14].astype(np.float)
        rawDil_set_rpm = dfRaw[1:,16].astype(np.float)
        rawDil_rpm = dfRaw[1:,17].astype(np.float)
        rawDil_fr = dfRaw[1:,19].astype(np.float)
        rawDil_err = dfRaw[1:,20].astype(np.float)
        rawDil_p = dfRaw[1:,21].astype(np.float)
        v1_cmd = dfRaw[1:,23].astype(np.float)
        v2_cmd = dfRaw[1:,24].astype(np.float)
        v3_cmd = dfRaw[1:,25].astype(np.float)


        
        dt = np.mean(np.diff(rawT))/1000 # unit seconds.
        

        
        # Analyze LFM error during flooding.
        def LFM_err(rawT, raw_err, v_cmd, raw_fr, raw_set_rpm):
            err0_tArr = np.array([])
            err0_vStat = np.array([])
            err0_dtArr = np.array([])
            err0_fr = np.array([])
            err0_set_rpm = np.array([])
            err1_tArr = np.array([])
            err1_vStat = np.array([])
            err0_arr = np.array([])
            err1_arr = np.array([])
            err1_fr = np.array([])
            err1_set_rpm = np.array([])

            for i in range(1,rawT.shape[0]):
                if raw_err[i] == 0 and raw_err[i-1] == 1:
                    err0_tArr = np.append(err0_tArr,rawT[i]/1000)
                    err0_vStat = np.append(err0_vStat,v_cmd[i])
                    err0_fr = np.append(err0_fr, raw_fr[i])
                    err0_set_rpm = np.append(err0_set_rpm, raw_set_rpm[i])
                    for j in range(i+1,rawT.shape[0]-1): # Look for length of time that error is cleared.
                        if raw_err[j] == 1 and raw_err[j-1] == 0:
                            err1_tArr = np.append(err1_tArr, rawT[j]/1000)
                            err0_dtArr = np.append(err0_dtArr,(rawT[j]-rawT[i])/1000)
                            err1_vStat = np.append(err1_vStat, v_cmd[i])
                            err1_fr = np.append(err1_fr, raw_fr[j])
                            err1_set_rpm = np.append(err1_set_rpm, raw_set_rpm[j])
                            break
                       
            # Ended with no error.
            if err0_dtArr.shape[0] < err0_tArr.shape[0]:
                err0_dtArr = np.append(err0_dtArr, rawT[-1]/1000 - err0_tArr[-1])
            err0_arr = np.vstack((err0_tArr, err0_vStat, err0_fr, err0_set_rpm, err0_dtArr))
            err0_arr = np.transpose(err0_arr)
            err1_arr = np.vstack((err1_tArr, err1_vStat, err1_fr, err1_set_rpm))
            err1_arr = np.transpose(err1_arr)  
            return err0_arr, err1_arr
        
        if pump == 2:
            [err0_arr, err1_arr] = LFM_err(rawT, rawOrg_err, v2_cmd, rawOrg_fr, rawOrg_set_rpm)
        elif pump == 1:
            [err0_arr, err1_arr] = LFM_err(rawT, rawAq_err, v1_cmd, rawAq_fr, rawAq_set_rpm)
        elif pump == 3:
            [err0_arr, err1_arr] = LFM_err(rawT, rawDil_err, v3_cmd, rawDil_fr, rawDil_set_rpm)
        
        # Compile error results. 
        if err0_arr.shape[0] == err1_arr.shape[0]:
            errResults = np.hstack((err0_arr, err1_arr))
        elif err0_arr.shape[0]>err1_arr.shape[0]:
            b = np.repeat(-99, err1_arr.shape[1])
            err1_arr = np.vstack((err1_arr, b))
            errResults = np.hstack((err0_arr, err1_arr))
        
        # Add other test details.
        filename_arr = np.repeat(filename, errResults.shape[0])

        # Aq, Org, or Dil pump.
        pumpTest = ''
        if pump == 1:
            pumpTest = 'Aq'
        elif pump == 2:
            pumpTest = 'Org'
        elif pump == 3:
            pumpTest = 'Dil'
        pumpTest_arr = np.repeat(pumpTest, errResults.shape[0])
            
        resultsArr = np.vstack((filename_arr, pumpTest_arr))
        resultsArr = np.transpose(resultsArr)    
        resultsArr2 = np.hstack((resultsArr, errResults))
                

        
        print (pumpTest + ' line in ' + filename+ ' analysis complete.')
        print(filename)
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T_'+test+'_'
        
        
        
                            
                            
                            
                    
                    
        
        
        
        
        
        