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


#tickers = [ "cusd", "dai", "fdusd", "frax", "lusd", "pyusd", "steth", "tusd", "usdc", "usdd", "usdt", "wbtc"]
stable_tickers = ["cusd", "crvusd" ,"dai", "fdusd", "frax", "lusd","mai" ,"pyusd", "steth", "tusd", "usdc", "usdd", "usdt","usde", "wbtc"] 
#stable_tickers = [ "usde"]

asset_name_list = []
ideal_strike_list = []
exp_probability_list = []
#current_strike_list = []
#current_probability_list = []
alt_strike_list = []
alt_probability_list = []
week_num = []
#multiplier_list = []

for ticker in stable_tickers:
    print(ticker)
    csv_file_path = f'data/{ticker}/{ticker}_daily.csv'
    price_history = pd.read_csv(csv_file_path)
    ideal_strike,exp_probability,total_week = calculate_stable_strike(price_history.tail(365),0,0,ticker)
    alt_strike = np.trunc(1000*ideal_strike)/1000
    alt_probability = probability_stable_strike(price_history.tail(365),alt_strike,0,1,ticker) #alt_strike
    
    asset_name_list.append(ticker)    
    ideal_strike_list.append(ideal_strike)
    exp_probability_list.append(100*exp_probability)
    alt_strike_list.append(alt_strike)
    alt_probability_list.append(100*alt_probability)
    week_num.append(total_week)
    


# In[3]:


output_df = pd.DataFrame({'Asset': asset_name_list,
                          'Ideal':ideal_strike_list,
                          'Ideal prob ':exp_probability_list,
                          'Alternative':alt_strike_list,
                          'Alt prob ':alt_probability_list,
                          
                         })

print(output_df)


# In[4]:


turbo_tickers = [ "arb", "btc", "eth","gmx", "pendle", "sol"]
#turbo_tickers = [ "arb"]
starting_day = 'SUN'

asset_name_list = []
touch_up_m_list = []
touch_d_m_list = []
p_up = []
p_down = []
week_total = []

for ticker in turbo_tickers:
    print(ticker)
    asset_name_list.append(ticker)
    csv_file_path = f'data/{ticker}/{ticker}_daily.csv'
    price_history = pd.read_csv(csv_file_path)
    a,b,c,d,e = calculate_turbo_strikes(price_history.tail(365),0.075, day=starting_day, show=0, write_pdf=1, ticker=ticker)
    
    touch_up_m_list.append(a)
    p_up.append(c)
    touch_d_m_list.append(b)
    p_down.append(d)
    week_total.append(e)


# In[5]:


output_df = pd.DataFrame({'Asset': asset_name_list,
                      'Up': touch_up_m_list,
                      'Prob up':p_up,
                      'Down': touch_d_m_list,
                      'Prob down':p_down,
                      'Total weeks':week_total
                     })

print(output_df)


# In[6]:


cvi_tickers = [ "cvi"]

for ticker in cvi_tickers:
    print(ticker)
    #asset_name_list.append(ticker)
    csv_file_path = f'data/{ticker}/{ticker}_daily.csv'
    price_history = pd.read_csv(csv_file_path)
    cvi_strike = calculate_cvi_strike(price_history.tail(365),show = 0,write_pdf = 1)
    print('CVI strike:')
    print(cvi_strike)


# In[7]:


volatility_tickers = [ "btc", "eth"]
#volatility_tickers = [ "btc"]

asset_name_list = []
touch_up_list = []
touch_d_list = []
value_list = []

for ticker in volatility_tickers:
    print(ticker)
    asset_name_list.append(ticker)
    csv_file_path = f'data/{ticker}/{ticker}_daily.csv'
    price_history = pd.read_csv(csv_file_path)
    up_limit, d_limit, current_val = calculate_volatility_strike(price_history.tail(365), window_size=30, show = 0,write_pdf = 1, ticker = ticker)
    touch_up_list.append(up_limit)
    touch_d_list.append(d_limit)
    value_list.append(current_val)
    


# In[8]:


output_df = pd.DataFrame({'Asset': asset_name_list,
                      'Up': touch_up_list,
                      'Down': touch_d_list,
                      'Current Val': value_list
                     })

print(output_df)


# In[ ]:




