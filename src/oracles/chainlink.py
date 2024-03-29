import pandas as pd
from tqdm import tqdm
import json
from src.helpers import finalizeMine
import os

def mineChainlink(source, web3):
    # Getting the name of the source
    ticker = source["name"].lower()

    # Define the file path
    file_path = f'data/{ticker}/{ticker}.csv'

    # Check if the directory exists, if not create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    # Check if the file exists, if not create an empty one with headers
    if not os.path.isfile(file_path):
        df = pd.DataFrame(columns=['','roundId','price','startedAt','updatedAt','datasource','roundId2'])  # Assuming 'roundId' is a column you need
        df.to_csv(file_path, index=False)
    else:
        # If the file exists, read it
        df = pd.read_csv(file_path, index_col=0)
    
    # Constructing ABI
    sourceType = source["sourceType"]
    abis = open(f"config/abis.json")
    abis = json.load(abis)
    abi = abis[sourceType]

    # Fetching the current round and last mined round
    contract = web3.eth.contract(address=source["address"], abi=abi)
    latestData = contract.functions.latestRoundData().call()
    currentRoundId = int(latestData[0])
    if not df.empty:
        lastRoundId = df['roundId'][df.index[-1]]
        ids = currentRoundId - int(lastRoundId)
    else:
        # TODO: Change back to 0
        lastRoundId = currentRoundId - 400
        if ticker == "cvi":
            print('in')
            lastRoundId = 18446744073709583854
        elif ticker == "steth":
            lastRoundId = 18446744073709551617
        elif ticker == "crvusd":
            lastRoundId = 18446744073709551616
        ids = currentRoundId - int(lastRoundId)
    
    # Fetching the historical data
    startFrom = currentRoundId - ids
    data = []
    for i in tqdm(range(ids)):
        startFrom += 1
        historicalData = contract.functions.getRoundData(startFrom).call()
        data.append(historicalData)
    new_df = pd.DataFrame(data, columns = ['roundId', 'price', 'startedAt', 'updatedAt', 'roundId2'])
    df = pd.read_csv(f'data/{ticker}/{ticker}.csv', index_col=0)
    
    # Dropping N/A values from DF
    df = df.dropna(axis=1, how='all')
    new_df = new_df.dropna(axis=1, how='all')

    # Formatting the data
    master_df = pd.concat([df, new_df])
    master_df['datasource'] = source["chain"]
    master_df = master_df.reset_index(drop=True)
    master_df.to_csv(f'data/{ticker}/{ticker}.csv')
    
    # Check for duplicates
    finalizeMine(ticker)