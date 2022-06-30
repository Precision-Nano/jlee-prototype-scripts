# -*- coding: utf-8 -*-
"""

Description: Prototype fluid path schematic updated to calibrate with Bronkhorst FM (for now), with no switching. Script analyzes peristaltic draw (ENG-000730).
Compiled results in "resultsArr2".
Last updated: May 4, 22
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd
# pd.set_option('display.float_format',lambda x: '%.9f' % x)


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000730 - Priming Sequence - Centrifugal Pumps/PLC files/Peristaltic draw - 2022.05.03'
testStart = '10' # PLC test number
pump = 3 # 1=aq, 2=org, 3=dil pump.


testEnd = testStart
# testEnd = '7'
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
    if nameStr in filename and 'PLC_FastLog_V4_' and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        # resultsArr = np.array([])

        
        
        # Load csv file from PLC.
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
        
        # rawT = dfRaw[2:,0].astype(np.float)
        # rawAq_set_rpm = dfRaw[1:,2].astype(np.float)
        # rawAq_rpm = dfRaw[1:,3].astype(np.float)
        # rawAq_fr = dfRaw[1:,5].astype(np.float)
        # rawAq_err = dfRaw[1:,6].astype(np.float)
        # rawAq_p = dfRaw[1:,7].astype(np.float)
        # rawOrg_set_rpm = dfRaw[1:,9].astype(np.float)
        # rawOrg_rpm = dfRaw[1:,10].astype(np.float)
        # rawOrg_fr = dfRaw[1:,12].astype(np.float)
        # rawOrg_err = dfRaw[1:,13].astype(np.float)
        # rawOrg_p = dfRaw[1:,14].astype(np.float)
        # rawDil_set_rpm = dfRaw[1:,16].astype(np.float)
        # rawDil_rpm = dfRaw[1:,17].astype(np.float)
        # rawDil_fr = dfRaw[1:,19].astype(np.float)
        # rawDil_err = dfRaw[1:,20].astype(np.float)
        # rawDil_p = dfRaw[1:,21].astype(np.float)
        # v1_cmd = dfRaw[1:,23].astype(np.float)
        # v2_cmd = dfRaw[1:,24].astype(np.float)
        # v3_cmd = dfRaw[1:,25].astype(np.float)


        
        dt = np.mean(np.diff(rawT))/1000 # unit seconds.
        
        # Analyze LFM flow detection.
        #initialize variables.
        errCount = 0
        t_fr_detect = -99
        t_err0 = -99
        t_cl = -99
        t_drawEnd = -99
        fr_draw = -99
        err_end = -99
        errCount2 = 0
        fr_ini = -99
        
        # # find starting flow rate (in error condition).
        # fr_ini = np.mean(rawAq_fr[0:round(3/dt)])
        # fr_thresh = 5 #unit ml/min.
        # threshCount = 0

        # for i in range(1, rawT.shape[0]):
        #     if rawAq_fr[i] < fr_ini/2 and v1_cmd[i] == 1 and t_fr_detect == -99:
        #         t_fr_detect = rawT[i]/1000
        #     if rawAq_err[i] == 0:
        #         for j in range(i,i+round(2/dt)):
        #             if rawAq_err[j] == 1:
        #                 errCount = 1
        #                 break
        #             else:
        #                 errCount = 0
        #         if errCount == 0 and t_err0 == -99:
        #             t_err0 = rawT[i]/1000
        #             fr_draw = np.mean(rawAq_fr[i:i+round(3/dt)]) # if error never clears but flow is detected, then want to start at detection (except for spike/dip at start).
        #     if rawAq_fr[i] < fr_thresh and threshCount == 0:
        #         threshCount = 1
        #         t_drawEnd = rawT[i]/1000
                
        #     if rawAq_err[i] == 1 and rawAq_err[i-1] == 0:
        #         errCount2 = errCount2 +1

        #     if v1_cmd[i] == 0 and v1_cmd[i-1] == 1:
        #         t_cl = rawT[i]/1000
        #         err_end = rawAq_err[i]
        #         break
            
        # dt_err0_draw = t_drawEnd - t_err0
        # dt_err0_drawV = t_cl - t_err0
        # dt_err0 = t_err0 - t_fr_detect
        
        # find starting flow rate (in error condition).
        def peristaltic_draw(v_cmd, raw_fr, raw_err, rawT):
            fr_ini = np.mean(raw_fr[0:round(3/dt)])
            fr_thresh = 5 #unit ml/min.
            threshCount = 0
            
            #initialize variables.
            errCount = 0
            t_fr_detect = -99
            t_err0 = -99
            t_cl = -99
            t_drawEnd = -99
            fr_draw = -99
            err_end = -99
            errCount2 = 0
            fr_ini = -99
    
            for i in range(1, rawT.shape[0]):
                if raw_fr[i] < fr_ini/2 and v_cmd[i] == 1 and t_fr_detect == -99:
                    t_fr_detect = rawT[i]/1000
                    fr_draw = np.mean(raw_fr[i+round(0.1/dt):i+round(3/dt)]) # for tests where LFM error doesn't clear.
                if raw_err[i] == 0:
                    for j in range(i,i+round(2/dt)):
                        if raw_err[j] == 1:
                            errCount = 1
                            break
                        else:
                            errCount = 0
                    if errCount == 0 and t_err0 == -99:
                        t_err0 = rawT[i]/1000
                        # fr_draw = np.mean(raw_fr[i:i+round(3/dt)]) # if error never clears but flow is detected, then want to start at detection (except for spike/dip at start).
                if raw_fr[i] < fr_thresh and threshCount == 0:
                    threshCount = 1
                    t_drawEnd = rawT[i]/1000
                    
                if raw_err[i] == 1 and raw_err[i-1] == 0:
                    errCount2 = errCount2 +1
    
                if v_cmd[i] == 0 and v_cmd[i-1] == 1:
                    t_cl = rawT[i]/1000
                    err_end = raw_err[i]
                    break
                
            dt_err0_draw = t_drawEnd - t_err0
            dt_err0_drawV = t_cl - t_err0
            dt_err0 = t_err0 - t_fr_detect
            resArr = np.hstack((t_fr_detect, t_err0, fr_draw, t_drawEnd, t_cl, err_end, errCount2, dt_err0, dt_err0_draw, dt_err0_drawV))
            return(resArr)
        
        # resArr = peristaltic_draw(v1_cmd, rawAq_fr, rawAq_err, rawT)
        resArr = peristaltic_draw(v3_cmd, rawDil_fr, rawDil_err, rawT)

        
        
        #compile results for that test.
        # Aq, Org, or Dil pump.
        pumpTest = ''
        if pump == 1:
            pumpTest = 'Aq'
        elif pump == 2:
            pumpTest = 'Org'
        elif pump == 3:
            pumpTest = 'Dil'
        
        resultsArr = np.hstack((filename, pumpTest, resArr))
        # resultsArr = np.hstack((filename, pumpTest, t_fr_detect, t_err0, fr_draw, t_drawEnd, t_cl, err_end, errCount2, dt_err0, dt_err0_draw, dt_err0_drawV))
        resultsArr = np.reshape(resultsArr, (1,resultsArr.shape[0]))
        resultsArr2 = np.append(resultsArr2, resultsArr)        
            
        

        # if pump == 2:
        #     [err0_arr, err1_arr] = LFM_err(rawT, rawOrg_err, v2_cmd, rawOrg_fr, rawOrg_set_rpm)
        # elif pump == 1:
        #     [err0_arr, err1_arr] = LFM_err(rawT, rawAq_err, v1_cmd, rawAq_fr, rawAq_set_rpm)
        # elif pump == 3:
        #     [err0_arr, err1_arr] = LFM_err(rawT, rawDil_err, v3_cmd, rawDil_fr, rawDil_set_rpm)
        
      
        
        print (pumpTest + ' line in ' + filename+ ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        