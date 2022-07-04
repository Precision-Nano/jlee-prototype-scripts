# -*- coding: utf-8 -*-
"""
Created on Fri Feb 25 09:36:10 2022

Description: Process picolog data from valve bench setup with SMC valves and VI's latest valve housing. See ENG-000578.
Final results in "results_all" array. Adjust row 129 inputs for either valve 1 (small ID) or valve 2 (large ID), and onT.
Last updated: March 1, 2022

@author: Jlee
"""


import numpy as np
import os 
import time
import pandas as pd



pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/02.0 Projects/Enfield/3.0 Testing/ENG-000578 - Pneumatic Valve Tests/Tests'
testStart = '27'
testEnd = testStart
# testEnd = '24'
test = testStart
config = 'B'

nameStr = 'T'+test+'_'

# Test specific parameters.
wsAvgT = 3 # unit seconds. Mass is averaged over +/- wsAvg T (i.e., 3 seconds).
loAvgT = 0.5 #unit seconds. For fast duty cycles of 1s.
onT = 1 # unit seconds. approximate.
FM_thresh = 3 #unit ml/min.
FM_acc = 0.05 #acceptable accuracy. 5% PR.
p_thresh = 1 #unit psi.


# Initialize variables.
resultsArr2 = np.array([])

tic = time.time()
# Loop through all files in directory, searching for filename meeting below criteria.
os.chdir(pathName)
for filename in os.listdir(pathName):
    if nameStr in filename and 'psiA.csv' in filename and int(test) <= int(testEnd):
        testNum = int(test)
        
        # Initialize variables.
        resultsArr = np.array([])
        cyc_count = 0
        opcl = -99
        dutycyc = 0
        opArr1 = np.array([])
        clArr1 = np.array([])
        avgN = 0
        wsAvgN = 0
        

        
        # Load csv file (from PicoLogger).
        df = pd.read_csv(filename)
        dt = 0.001 # 1ms timestep.
        dfRaw = pd.DataFrame(df).to_numpy()
        rawFM = dfRaw[:,1]
        rawP1 = dfRaw[:,2]
        rawP2 = dfRaw[:,3]
        rawV1C = dfRaw[:,4]
        rawV2C = dfRaw[:,5]
        rawV1S1 = dfRaw[:,6]
        rawV1S2 = dfRaw[:,7]
        rawV2S1 = dfRaw[:,8]
        rawV2S2 = dfRaw[:,9]
        rawFME = dfRaw[:,10]
        rawFMZ = dfRaw[:,11]
        rawP_tank = dfRaw[:,12]
        rawP_air = dfRaw[:,13]
             
        if config == 'B' or config == 'C':
            wsAvgN = round(loAvgT/dt)
            
        else:
            wsAvgN = round(wsAvgT/dt)
        
        # Calcualations for each cycle on valve on/off.
        def valve_times(rawVC, rawVS1, rawVS2, onT,dt,):
            # Initialize variables.
            vcn = np.array([])
            vs1n = np.array([])
            vs2n = np.array([])
            offset = 0
            cyc_count = 0
            # chk_end = 0
            for i in range (1,rawVC.shape[0]):         
                # Calculations if an on/off cycle has started.
                i1 = i+offset
                if i1<rawVC.shape[0]:
                    if rawVC[i1] == 0 and rawVC[i1] != rawVC[i1-1]:
                        cyc_count += 1
                        vcn = np.append(vcn,i1)
                        v1state = rawVC[i1]
                                                        
                        for j in range(i1,i1+round((onT+10)/dt),1): #usually onT+3, but change additional time as needed for duty cycle.***
                            # Find starting conditions.
                            if rawVS1[j] != rawVS1[j-1]:
                                vs1n = np.append(vs1n,j)
                            if rawVS2[j] != rawVS2[j-1]:
                                vs2n = np.append(vs2n,j)
                            # Find end conditions.
                            if rawVC[j] != rawVC[j-1] and rawVC[j] != v1state and j != i1:
                                vcn = np.append(vcn,j)
                                for k in range(j,j+round(1/dt),1):
                                    if rawVS1[k] != rawVS1[k-1]:
                                        vs1n = np.append(vs1n,k)
                                        # chk_end += 1
                                        # if chk_end == 2:
                                        #     chk_end = 0
                                        #     break
                                    if rawVS2[k] != rawVS2[k-1]:
                                        vs2n = np.append(vs2n,k)
                                        # chk_end += 1
                                        # if chk_end == 2:
                                        #     chk_end = 0
                                        #     break
                                offset += (k-j)
                                break
                else:
                    break
            
           # delete extra indices.
            size = vs2n.shape[0]
            size1 = vs1n.shape[0]
            # m1 = 1
            # m2 = 1
            for m in range(1,size-1):
                if vs2n[m]-vs2n[m-1] <= 1:
                    vs2n = np.delete(vs2n,m-1)
                    size = size - 1
                    # m2 = m+1
            for m in range(1,size1-1):
                if vs1n[m]-vs1n[m-1] <= 1:
                    vs1n = np.delete(vs1n,m-1)
                    size1 = size1 - 1
                    # m1 = m+1
            vs1n = np.unique(vs1n)
            vs2n = np.unique(vs2n)
            
         
            res_valves_n = np.vstack((vcn, vs1n, vs2n))
            res_valves_n1 = np.transpose(res_valves_n)
            res_valves_n1 = res_valves_n1.astype(int)
            return res_valves_n1, cyc_count
            
            # return vcn, vs1n, vs2n
        
        # Adjust for valve type 1 (small ID) or valve type 2 (large ID).
        [res_valveArr, cyc_count] = valve_times(rawV2C, rawV2S1, rawV2S2, onT, dt)
        # [vcn, vs1n, vs2n] = valve_times(rawV1C, rawV1S1, rawV1S2, onT, dt)
        
        
    
        # def valve_results(res_valveArr, rawP1, rawP2, rawP_air, rawFM, FM_thresh, )
        # calculate valve action time and latencies.
        for i in range(0,res_valveArr.shape[0]):
            if i % 2 == 0:
                opcl = 1
                dutycyc += 1
                t_cmd = res_valveArr[i,0]*dt
                t_s1 = res_valveArr[i,1]*dt
                t_s2 = res_valveArr[i,2]*dt
                t_response = t_s1-t_cmd
                t_vact = t_s2-t_s1
                t_state = res_valveArr[i+1,0]*dt-t_cmd
                t_tot = t_response+t_vact
                
                # pressure results.
                nP1i = 0
                nP2i = 0
                ssP1 = 0
                ssP2 = 0
                nP1ss = 0
                nP2ss = 0
                tP1i = 0
                tP2i = 0
                tP1ss = 0
                tP2ss = 0
                p1_spike = 0
                p2_spike = 0
                dp1_spike = 0
                dp2_spike = 0
                nP_equil = -99
                tP_equil = -99
                tP1_res = 0
                tP2_res = 0
                p1_ini = np.mean(rawP1[res_valveArr[i,0]-wsAvgN:res_valveArr[i,0]])
                p2_ini = np.mean(rawP2[res_valveArr[i,0]-wsAvgN:res_valveArr[i,0]])
                
                # Find start of pressure change.
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawP1[j]-p1_ini) > p_thresh:
                        nP1i = j
                        tP1i = nP1i*dt
                    if abs(rawP2[j]-p2_ini) > p_thresh:
                        nP2i = j
                        tP2i = nP2i*dt
                    if nP1i and nP2i != 0:
                        break
                # pressure response time.
                tP1_res = tP1i - t_cmd
                tP2_res = tP2i - t_cmd

                
                # Find time at pressure equilibrium (from valve being fully opened).
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawP1[j]-rawP2[j]) < 0.5:
                        nP_equil = j
                        tP_equil = nP_equil*dt
                        break
                ssP1 = np.mean(rawP1[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                ssP2 = np.mean(rawP2[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                # Find SS time.
                for j in range(nP_equil,nP_equil+round(1/dt)):
                    if abs(rawP1[j]-ssP1) <= 0.3:
                        for k in range(j,j+round(3/dt)):
                            if abs(rawP1[k]-ssP1) > 0.3:
                                break
                        nP1ss = j
                        tP1ss = nP1ss*dt
                for j in range(nP_equil,nP_equil+round(1/dt)):
                    if abs(rawP2[j]-ssP2) <= 0.3:
                        for k in range(j,j+round(3/dt)):
                            if abs(rawP2[k]-ssP2) > 0.3:
                                break
                        nP2ss = j
                        tP2ss = nP2ss*dt
                p1_spike = np.max(rawP1[nP1i:nP1ss])
                p2_spike = np.max(rawP2[nP2i:nP2ss])
                dp1_spike = p1_spike - ssP1
                dp2_spike = p2_spike - ssP2
                        
                # Air pressure calcs.
                aP_avg = 0
                aP_dip = 0
                aP_dp = 0
                
                n_mid = round((res_valveArr[i,0]+res_valveArr[i+1,0])/2)
                aP_avg = np.mean(rawP_air[n_mid-wsAvgN:n_mid+wsAvgN])
                aP_dip = np.min(rawP_air[res_valveArr[i,0]:nP1ss])
                aP_dp = aP_dip-aP_avg
                
                # Flow rate calcs.
                dtFM_ss = 0
                tFM_ss = 0
                tFM_ch = 0
                nFM_ss = 0
                nFM_ch = 0
                tFM_res = 0
                fm_ss = np.mean(rawFM[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if rawFM[j] > FM_thresh:
                        nFM_ch = j
                        tFM_ch = nFM_ch*dt
                        break
                for j in range(nFM_ch,res_valveArr[i+1,0]):
                    ng = 0
                    if abs((rawFM[j]-fm_ss)/fm_ss) <= FM_acc:
                        checkFM = rawFM[j:j+wsAvgN]
                        if all(k > fm_ss*(1-FM_acc) and k < fm_ss*(1+FM_acc) for k in checkFM):
                            nFM_ss = j
                            tFM_ss = nFM_ss*dt
                            break
                dtFM_ss = tFM_ss - tFM_ch
                tFM_res = tFM_ch - t_cmd
                #additional flow rate calcs.
                # fm_std = np.std(rawFM[nP1ss:res_valveArr[i+1,0]])
                # fm_min = np.min(rawFM[nP1ss:res_valveArr[i+1,0]])
                # fm_max = np.max(rawFM[nP1ss:res_valveArr[i+1,0]])
                    
                
                
                # opArr = np.vstack((testNum, dutycyc, t_cmd, t_s1, t_s2, t_response, t_vact, t_tot, t_state, opcl,tP1i, tP2i, tP_equil, tP1ss, tP2ss, tP1_res, tP2_res, p1_spike, p2_spike, dp1_spike, dp2_spike, ssP1, ssP2, aP_avg, aP_dip, aP_dp, fm_ss, tFM_ch, tFM_ss, tFM_res, dtFM_ss, fm_std, fm_min, fm_max))
                opArr = np.vstack((testNum, dutycyc, t_cmd, t_s1, t_s2, t_response, t_vact, t_tot, t_state, opcl,tP1i, tP2i, tP_equil, tP1ss, tP2ss, tP1_res, tP2_res, p1_spike, p2_spike, dp1_spike, dp2_spike, ssP1, ssP2, aP_avg, aP_dip, aP_dp, fm_ss, tFM_ch, tFM_ss, tFM_res, dtFM_ss))
                
                opArr1 = np.append(opArr1, opArr)
            elif i % 2 != 0:
                opcl = 0
                t_cmd = res_valveArr[i,0]*dt
                t_s1 = res_valveArr[i,1]*dt
                t_s2 = res_valveArr[i,2]*dt
                t_response = t_s2-t_cmd
                t_vact = t_s1-t_s2
                t_state = t_cmd - res_valveArr[i-1,0]*dt
                t_tot = t_response+t_vact
                
                # pressure results.
                nP1i = 0
                nP2i = 0
                ssP1 = 0
                ssP2 = 0
                nP1ss = 0
                nP2ss = 0
                tP1i = 0
                tP2i = 0
                tP1ss = 0
                tP2ss = 0
                p1_spike = 0
                p2_spike = 0
                dp1_spike = 0
                dp2_spike = 0
                nP_equil = -99
                tP_equil = -99
                tP1_res = 0
                tP2_res = 0
                p1_ini = np.mean(rawP1[res_valveArr[i,0]-wsAvgN:res_valveArr[i,0]])
                p2_ini = np.mean(rawP2[res_valveArr[i,0]-wsAvgN:res_valveArr[i,0]])
                
                # Find start of pressure change.
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawP1[j]-p1_ini) > p_thresh:
                        nP1i = j
                        tP1i = nP1i*dt
                    if abs(rawP2[j]-p2_ini) > p_thresh:
                        nP2i = j
                        tP2i = nP2i*dt
                    if nP1i and nP2i != 0:
                        break
                # Find ss pressure.
                if i < res_valveArr.shape[0]-1:
                    ssP1 = np.mean(rawP1[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                    ssP2 = np.mean(rawP2[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                    n_mid = round((res_valveArr[i,0]+res_valveArr[i+1,0])/2)
                    fm_ss = np.mean(rawFM[res_valveArr[i+1,0]-wsAvgN:res_valveArr[i+1,0]])
                    nFM_end = res_valveArr[i+1,0]

                else:
                    ssP1 = np.mean(rawP1[res_valveArr[i,0]+round(1/dt):res_valveArr[i,0]+round(1/dt)+wsAvgN])
                    ssP2 = np.mean(rawP2[res_valveArr[i,0]+round(1/dt):res_valveArr[i,0]+round(1/dt)+wsAvgN])
                    n_mid = res_valveArr[i,0]+wsAvgN
                    fm_ss = np.mean(rawFM[res_valveArr[i,0]+round(1/dt):res_valveArr[i,0]+round(1/dt)+wsAvgN])
                    nFM_end = rawFM.shape[0]
                
                # Find SS time.
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawP1[j]-ssP1) <= 0.3:
                        for k in range(j,j+wsAvgN): 
                            if abs(rawP1[k]-ssP1) > 0.3:
                                break
                        nP1ss = j
                        tP1ss = nP1ss*dt
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawP2[j]-ssP2) <= 0.3:
                        for k in range(j,j+round(3/dt)): # usually 3/dt, sometimes shorter for test run.
                            if abs(rawP2[k]-ssP2) > 0.3:
                                break
                        nP2ss = j
                        tP2ss = nP2ss*dt
                # p1_spike = np.max(rawP1[res_valveArr[i,0]:nP1ss])
                # p2_spike = np.max(rawP2[res_valveArr[i,0]:nP2ss])
                # dp1_spike = p1_spike - ssP1
                # dp2_spike = p2_spike - ssP2
                

                
                # pressure response time.
                tP1_res = tP1i - t_cmd
                tP2_res = tP2i - t_cmd
                
                # Air pressure calcs.
                aP_avg = 0
                aP_dip = 0
                aP_dp = 0
                
               
                aP_avg = np.mean(rawP_air[n_mid-wsAvgN:n_mid+wsAvgN])
                aP_dip = np.min(rawP_air[res_valveArr[i,0]:nP1ss])
                aP_dp = aP_dip-aP_avg
                
                # Flow rate calcs.
                dtFM_ss = 0
                tFM_ss = -99
                tFM_ch = 0
                nFM_ss = 0
                nFM_ch = 0
                fm_ini = 0
                tFM_res = 0
                dtFM_ss = -99

                fm_ini = np.mean(rawFM[res_valveArr[i,0]-wsAvgN:res_valveArr[i,0]])
                for j in range(res_valveArr[i,0],res_valveArr[i,0]+round(1/dt)):
                    if abs(rawFM[j]-fm_ini) > FM_thresh:
                        nFM_ch = j
                        tFM_ch = nFM_ch*dt
                        break
                for j in range(nFM_ch,nFM_end):
                    ng = 0
                    if abs((rawFM[j]-fm_ss)/fm_ss) <= FM_acc:
                        checkFM = rawFM[j:j+wsAvgN]
                        if all(k > fm_ss*(1-FM_acc) and k < fm_ss*(1+FM_acc) for k in checkFM):
                            nFM_ss = j
                            tFM_ss = nFM_ss*dt
                            break
                tFM_res = tFM_ch - t_cmd
                fm_std = -99
                fm_min = -99
                fm_max = -99
                
                
                
                # clArr = np.vstack((testNum, dutycyc, t_cmd, t_s1, t_s2, t_response, t_vact, t_tot, t_state, opcl,tP1i, tP2i, tP_equil, tP1ss, tP2ss, tP1_res, tP2_res, p1_spike, p2_spike, dp1_spike, dp2_spike, ssP1, ssP2, aP_avg, aP_dip, aP_dp, fm_ss, tFM_ch, tFM_ss, tFM_res, dtFM_ss, fm_std, fm_min, fm_max))
                clArr = np.vstack((testNum, dutycyc, t_cmd, t_s1, t_s2, t_response, t_vact, t_tot, t_state, opcl,tP1i, tP2i, tP_equil, tP1ss, tP2ss, tP1_res, tP2_res, p1_spike, p2_spike, dp1_spike, dp2_spike, ssP1, ssP2, aP_avg, aP_dip, aP_dp, fm_ss, tFM_ch, tFM_ss, tFM_res, dtFM_ss))                
                clArr1 = np.append(clArr1, clArr)
                
                
        opArr2 = np.reshape(opArr1,(dutycyc, int(opArr1.shape[0]/dutycyc)))
        clArr2 = np.reshape(clArr1,(dutycyc, int(clArr1.shape[0]/dutycyc)))
        results_all = np.vstack((opArr2,clArr2))
                
                                

          
        
        # resultsArr = np.hstack((testNum, tarFR, wat, eth, t1_LFM, t1_BFM, t1_SFM, tEnd2, ssLFM, ssBFM, ssSFM, min_LFM, min_BFM, min_SFM, max_LFM, max_BFM, max_SFM, LCfr, temp1, temp2, temp3))
        # # resultsArr = np.transpose(resultsArr)
        # resultsArr = np.reshape(resultsArr, (1,resultsArr.shape[0]))
        # resultsArr2 = np.append(resultsArr2, resultsArr)
        
        # print ('test '+test+ ' done.')
        # print(filename)
        
        # testNum +=1 
        # test = str(testNum)
        # nameStr = 'T_'+test+'_'
        
        
        
    

# resultsArr2 = np.reshape(resultsArr2, (round(resultsArr2.shape[0]/resultsArr.shape[1]), resultsArr.shape[1]))
       
        
        
                
                            
                            
    