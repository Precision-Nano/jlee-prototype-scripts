# -*- coding: utf-8 -*-
"""

Description: Calibration through Promass flow meter. ENG-000810. Final results in "resultsArr".
Last updated: Jun 6, 22.
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd
# pd.set_option('display.float_format',lambda x: '%.9f' % x)


# User entries
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000820 Calibration sequence workflow/Tests'

testStart = '10' # PLC test number
testType = 2 # 1 = one setpoint FR. 2 = Two setpoint FRs in test.



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
        
        # calculate SS flow rates for promass and LFM from last section of test.
        
        # optional parameters.
        offsetT = 1 # unit seconds, from end of run.
        # offsetN = -r
        
        # avgArr = np.array([5,10,15,20,25,30,35,40,45, 60])
        avgArrSam = np.array([2,4,6,8,10,12,14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,58,60])
        avgArr = avgArrSam + offsetT
        lfmArr_ss = np.array([])
        lfmArr_std = np.array([])
        cfmArr_ss = np.array([])
        cfmArr_std = np.array([])
        cfArr = np.array([])
        fr_targetArr = np.array([])
        offsetArr = np.array([])
        cf = -99
        fr_target = rawOrg_set_fr[round(rawT.shape[0]/2)] # adjust for pump***
        for i in range(0,avgArr.shape[0]):    
            lfmArr_ss = np.append(lfmArr_ss, np.mean(rawOrg_fr[-round(avgArr[i]/dt):-round(offsetT/dt)])) # adjust for pump***
            lfmArr_std = np.append(lfmArr_std, np.std(rawOrg_fr[-round(avgArr[i]/dt):-round(offsetT/dt)])) # adjust for pump***
            cfmArr_ss = np.append(cfmArr_ss, np.mean(rawCFM_fr[-round(avgArr[i]/dt):-round(offsetT/dt)]))
            cfmArr_std = np.append(cfmArr_std, np.std(rawCFM_fr[-round(avgArr[i]/dt):-round(offsetT/dt)])) 
            cf = fr_target/np.mean(rawCFM_fr[-round(avgArr[i]/dt):-round(offsetT/dt)])
            cfArr = np.append(cfArr, cf)
            fr_targetArr = np.append(fr_targetArr, fr_target)
            offsetArr = np.append(offsetArr, offsetT)
   
        #compile promass results.
        resultsArr = np.vstack((fr_targetArr, avgArrSam, lfmArr_ss, cfmArr_ss, lfmArr_std, cfmArr_std, cfArr, offsetArr))
        resultsArr = np.transpose(resultsArr)
        
        # integrate flow rates for volume. 
        T_min = rawT/1000/60
        t_endPrime = 5 #priming done 10s prior to end of test.
        n_endPrime = round(t_endPrime/dt)
        ind_endPrime = rawT.shape[0]-n_endPrime
        
        volAq = np.trapz(rawAq_fr,T_min)
        volOrg = np.trapz(rawOrg_fr,T_min)
        volDil = np.trapz(rawDil_fr,T_min)
        vol_test = volAq + volOrg + volDil
        volAq_prime = np.trapz(rawAq_fr[0:ind_endPrime],T_min[0:ind_endPrime])
        volOrg_prime = np.trapz(rawOrg_fr[0:ind_endPrime],T_min[0:ind_endPrime])
        volDil_prime = np.trapz(rawDil_fr[0:ind_endPrime],T_min[0:ind_endPrime])
        vol_prime = volAq_prime + volOrg_prime + volDil_prime
        
        
        #Section below analyzes the effect of changing the target fr and settle time v. CF. 
        sampleT = 10 # unit seconds. Time to calculate CF.
        sampleN = round(sampleT/dt)
        refreshT = 3 #unit seconds. Time to re-evaluate CF.
        refreshN = round(3/dt)
        
        #initialize variables.
        newTargetTArr = np.array([])
        avgCFM = -99
        cf = -99
        t_eval = 0
        avgCFM_arr = np.array([])
        avgLFM_arr = np.array([])
        cf_arr = np.array([])
        tArr_newtar = np.array([])
        fr_targetArr = np.array([])
        
        
        if testType == 2:
            fr_target1 = rawDil_set_fr[round(rawT.shape[0]/3)] # Adjust for pump**********
            fr_target2 = rawDil_set_fr[round(rawT.shape[0]*2/3)] # Adjust for pump**********
            for j in range(round(rawT.shape[0]/3),rawT.shape[0]):
                if rawDil_set_fr[j] == fr_target2: # Adjust for pump**********
                    for k in range(j,rawT.shape[0],refreshN):
                        avgCFM = np.mean(rawCFM_fr[k-sampleN:k])
                        avgCFM_arr = np.append(avgCFM_arr, avgCFM)
                        avgLFM_arr = np.append(avgLFM_arr, np.mean(rawDil_fr[k-sampleN:k])) # Adjust for pump**********
                        cf = fr_target2/avgCFM
                        cf_arr = np.append(cf_arr, cf)
                        tArr_newtar = np.append(tArr_newtar,t_eval)
                        fr_targetArr = np.append(fr_targetArr, fr_target2)
                        t_eval += refreshT
                        if t_eval == 90:
                            break
                    break
                
            #compile results.
            resultsArr_recal = np.vstack((fr_targetArr, tArr_newtar, avgCFM_arr, avgLFM_arr, cf_arr))
            resultsArr_recal = np.transpose(resultsArr_recal)
                        
                        
                        
                        
                    
        
        
      
        
        print (filename + ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
# resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        