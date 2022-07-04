# -*- coding: utf-8 -*-
"""
Created on Mon Oct  4 20:49:43 2021

@author: Jlee
"""

import pandas as pd
import numpy as np
import os
import time

pathName = 'C:/Users/jlee/Danaher/PLL PNI Engineering - Documents/00.0 Users/Janice/Valve Testing/'
fileName = 'DY water long run.csv'

tic = time.time()

for filename in os.listdir(pathName):
    if filename == fileName:
        # Initialize variables.
        
        # Import Prototype Pico Scope log file.
        df = pd.read_csv(pathName+filename)
        df_np = df.to_numpy()
        rawData_section = df_np[0:100,:]
        raw_section = df[0:100,:]
        
        print(time.time()-tic)
        
        
        
        
        