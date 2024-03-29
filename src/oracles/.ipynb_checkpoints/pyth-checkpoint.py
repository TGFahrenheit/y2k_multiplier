import pandas as pd
from tqdm import tqdm
import json
from src.helpers import finalizeMine
import os
import time 
import requests

# Arbitrum pyth main feed: 0xff1a0f4744e8582DF1aE09D5611b887B6a12925C
def minePyth(source):
    # Getting the name of the source
    ticker = source["name"].lower()

    # Define the file path
    file_path = f'data/{ticker}/{ticker}_daily.csv'
    from_timestamp = 0

    # Check if the directory exists, if not create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # Check if the file exists, if not create an empty one with headers
    if not os.path.isfile(file_path):
        df = pd.DataFrame(columns=['open','high','low','close','timestamp'])
        df.to_csv(file_path, index=False)
    else:
        # If the file exists, read it
        os.remove(file_path)
        df = pd.DataFrame(columns=['open','high','low','close','timestamp'])
        df.to_csv(file_path, index=False)
        #df = pd.read_csv(file_path, index_col=0)
        #df['timestamp'] = pd.to_datetime(df['timestamp'])
        #last_timestamp = df['timestamp'].iloc[-1]
        #from_timestamp = int(last_timestamp.timestamp())

    # Fetch data
    to_timestamp = int(time.time())
    if(from_timestamp == 0):
        from_timestamp = to_timestamp - 60*60*24*365
    wholeTicker = f"{ticker}/USD"
    url = f"https://benchmarks.pyth.network/v1/shims/tradingview/history?symbol=Crypto.{wholeTicker}&resolution=D&from={from_timestamp}&to={to_timestamp}"

    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve data: {response.status_code}")
        return

    # Formatting the new data
    data = response.json()
    new_df = pd.DataFrame(data['t'], columns=['timestamp'])
    new_df['open'] = data['o']
    new_df['close'] = data['c']
    new_df['high'] = data['h']
    new_df['low'] = data['l']
    new_df['timestamp'] = pd.to_datetime(new_df['timestamp'], unit='s')

    # Dropping N/A values from DF
    df = df.dropna(axis=1, how='all')
    new_df = new_df.dropna(axis=1, how='all')

    # Formatting the data
    master_df = pd.concat([df, new_df])
    master_df = master_df.reset_index(drop=True)
    master_df.to_csv(f'data/{ticker}/{ticker}_daily.csv', index=False)