#!/usr/bin/env python
# coding: utf-8

# In[1]:

import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import statistics 
from src.strike_tools import calculate_stable_strike, probability_stable_strike, calculate_turbo_strikes, calculate_cvi_strike, calculate_volatility_strike

warnings.simplefilter(action='ignore', category=FutureWarning)


# In[2]:


stable_tickers = ["cusd", "crvusd" ,"dai", "fdusd", "frax", "lusd","mai" ,"pyusd", "steth", "tusd", "usdc", "usdd", "usdt","usde", "wbtc"] 
stable_strikes = [["cusd",0.976],["crvusd",0.990],["dai",0.997],["fdusd",0.996],["frax",0.995],["lusd",0.990],["mai",0.750],["pyusd",0.990],["steth",0.981],["tusd",0.974],["usdc",0.992],["usdd",0.977],["usde",0.995],["usdt",0.991],["wbtc",0.997]]

asset_name_list = []
alt_strike_list = []
alt_probability_list = []
multiplier_list = []
week_num = []

for ticker in stable_tickers:
    print(ticker)
    csv_file_path = f'data/{ticker}/{ticker}_daily.csv'
    price_history = pd.read_csv(csv_file_path)

    for d in stable_strikes:
        if d[0] == ticker:
            test_price = d[1]

    ideal_strike,exp_probability,total_week = calculate_stable_strike(price_history.tail(365),0,0,ticker)
    alt_probability = probability_stable_strike(price_history.tail(365),test_price,0,0,ticker) #alt_strike
    
    asset_name_list.append(ticker)    
    alt_strike_list.append(test_price)
    alt_probability_list.append(100*alt_probability)
    multiplier_list.append(1/(alt_probability+0.0001))
    week_num.append(total_week)


output_df = pd.DataFrame({'Asset': asset_name_list,
                          'Strike':alt_strike_list,
                          'Probability':alt_probability_list,
                          'Multiplier':multiplier_list,
                          'Weeks' : week_num
                         })

print(output_df)