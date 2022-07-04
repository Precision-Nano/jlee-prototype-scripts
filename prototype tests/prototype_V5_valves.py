# -*- coding: utf-8 -*-
"""

Description: Prototype fluid path schematic updated to calibrate with Promass flow meter, no switching. Script analyzes dry valve switches, tested in groups or all at once (ENG-000805).
Compiled results in "resOp_all" and "resCl_all".
Last updated: May 24, 22.
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000805 Install Fluid Path Workflow/PLC Data'
testStart = '3' # PLC test number



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
resOp_all = np.array([])
resCl_all= np.array([])

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if nameStr in filename and 'PLC_FastLog_V5_' and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.

        
        
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
        
        # Calculate latency between valve command (to open or close) and sense response.
        def valveTiming(V_cmd, rawT, V_open, V_close, valveNum):
            tArr_cmdOp = np.array([])
            tArr_sOp = np.array([])
            tArr_cmdCl = np.array([])
            tArr_sCl = np.array([])
            dtArr_cl = np.array([])
            dtArr_op = np.array([])
            t_resOp = np.array([])
            valveNumArr = np.array([])
            valveNumArr2 = np.array([])
            dutycArr = np.array([])
            airPArr_dipOp = np.array([])
            airPArr_dipCl = np.array([])
            # define function for each valve.
       
            for i in range(1,rawT.shape[0]):
                if V_cmd[i] == 1 and V_cmd[i] != V_cmd[i-1]:
                    tArr_cmdOp = np.append(tArr_cmdOp, rawT[i])
                    valveNumArr = np.append(valveNumArr, valveNum)
                    airPArr_dipOp = np.append(airPArr_dipOp, np.min(rawAirp[i:i+round(2/dt)]))
                    for j in range(i,i+round(5/dt)):
                        if V_open[j] == 1 and V_open[j] != V_open[j-1]:
                            tArr_sOp = np.append(tArr_sOp, rawT[j])
                            break
                    if tArr_cmdOp.shape[0]>tArr_sOp.shape[0]:
                        tArr_sOp = np.append(tArr_sOp, -99)
                if V_cmd[i] == 0 and V_cmd[i] != V_cmd[i-1]:
                    tArr_cmdCl = np.append(tArr_cmdCl, rawT[i])
                    valveNumArr2 = np.append(valveNumArr2, valveNum)
                    airPArr_dipCl = np.append(airPArr_dipCl, np.min(rawAirp[i:i+round(2/dt)]))
                    for j in range(i,i+round(5/dt)):
                        if V_close[j] == 1 and V_close[j] != V_close[j-1]:
                            tArr_sCl = np.append(tArr_sCl, rawT[j])
                            break
                    if tArr_cmdCl.shape[0] > tArr_sCl.shape[0]:
                        tArr_sCl = np.append(tArr_sCl, -99)
            for k in range(0, tArr_sOp.shape[0]):
                if tArr_sOp[k] != -99:
                    dtArr_op = np.append(dtArr_op, tArr_sOp[k]-tArr_cmdOp[k])
                else:
                    dtArr_op = np.append(dtArr_op, -99)
            for k in range(0,tArr_sCl.shape[0]):
                if tArr_sCl[k] != -99:
                    dtArr_cl = np.append(dtArr_cl, tArr_sCl[k]-tArr_cmdCl[k])
                else:
                    dtArr_cl = np.append(dtArr_cl, -99)
            if tArr_cmdOp.shape[0] >= tArr_cmdCl.shape[0]:
                for m in range(0,tArr_cmdCl.shape[0]):
                    dutycArr = np.append(dutycArr,tArr_cmdCl[m] - tArr_cmdOp[m])
            else:
                for m in range(0,tArr_cmdOp.shape[0]):
                    dutycArr = np.append(dutycArr,tArr_cmdCl[m] - tArr_cmdOp[m])
                    
            
            t_resOp = np.vstack((valveNumArr, tArr_cmdOp, tArr_sOp, dtArr_op, airPArr_dipOp)) # add dutycArr here if one group test.
            t_resCl = np.vstack((valveNumArr2, tArr_cmdCl, tArr_sCl, dtArr_cl, airPArr_dipCl)) # add dutycArr here if 2 group test.
            return t_resOp, t_resCl, dutycArr
        

        [resOp_v1, resCl_v1, dutycArr1] = valveTiming(V1_cmd, rawT, V1_open, V1_close, 1)
        [resOp_v2, resCl_v2, dutycArr2] = valveTiming(V2_cmd, rawT, V2_open, V2_close, 2)
        [resOp_v3, resCl_v3, dutycArr3] = valveTiming(V3_cmd, rawT, V3_open, V3_close, 3)
        [resOp_v4, resCl_v4, dutycArr4] = valveTiming(V4_cmd, rawT, V4_open, V4_close, 4)
        [resOp_v5, resCl_v5, dutycArr5] = valveTiming(V5_cmd, rawT, V5_open, V5_close, 5)
        # [resOp_v6, resCl_v6] = valveTiming(V6_cmd, rawT, V6_open, V6_close, 6)
        [resOp_v7, resCl_v7, dutycArr7] = valveTiming(V7_cmd, rawT, V7_open, V7_close, 7)
        # [resOp_v8, resCl_v8] = valveTiming(V8_cmd, rawT, V8_open, V8_close, 8)
        
        # compile all open cycles together. compile all close cycles together.
        fileN_arr = np.repeat(filename, resOp_all.shape[0])
        resOp_all = np.hstack((resOp_v1, resOp_v2, resOp_v3, resOp_v4, resOp_v5, resOp_v7))
        resCl_all = np.hstack((resCl_v1, resCl_v2, resCl_v3, resCl_v4, resCl_v5, resCl_v7))
        resDutycArr_all = np.hstack((dutycArr1, dutycArr4))
        # resArr = np.hstack(())
        
        print (filename + ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
# resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        