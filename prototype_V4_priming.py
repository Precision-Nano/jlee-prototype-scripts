# -*- coding: utf-8 -*-
"""

Description: Prototype fluid path schematic updated to calibrate with Promass flow meter, no switching. Script analyzes priming tests (PLC folder dated May 16, 22) (ENG-000730).
Compiled results in "resultsArr2".
Last updated: May 18, 22.
@author: Jlee
"""

import numpy as np
import os 
import time
import pandas as pd
# pd.set_option('display.float_format',lambda x: '%.9f' % x)


# User entries
# pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000730 - Priming Sequence - Centrifugal Pumps/PLC files/PP draw primed - 2022.05.18'
pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000730 - Priming Sequence - Centrifugal Pumps/PLC files/Priming - 2022.05.16'

testStart = '9' # PLC test number

# pump = 3 # 1=aq, 2=org, 3=dil pump.


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
        rawAirp = dfRaw[:,26].astype(np.float)
        v1_cmd = dfRaw[:,27].astype(np.float)
        v2_cmd = dfRaw[:,28].astype(np.float)
        v3_cmd = dfRaw[:,29].astype(np.float)
      

        
        dt = np.mean(np.diff(rawT))/1000 # unit seconds.
        
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
        
        
        
      
        
        print (filename + ' analysis complete.')
        
        testNum +=1 
        test = str(testNum)
        nameStr = 'T'+test+'_'
        
        
# resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
        
                            
                            
                            
                    
                    
        
        
        
        
        
        