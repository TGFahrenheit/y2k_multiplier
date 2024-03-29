import json
from src.oracles.chainlink import mineChainlink
from src.oracles.pyth import minePyth
from src.helpers import fetchSourceInfo

# Rpc configuration for mineData function
from web3 import Web3
from dotenv import load_dotenv
import os
load_dotenv()

# Mining configuration
mineAllSources = False
ticker = ["usdc", "1inch"]
mineSources = fetchSourceInfo(ticker)

# Routing the mining to the correct source
def mineData(sources):    
    # Iterating over the sources to mine data
    for source in sources:
        # Configuring the rpc for each chain
        rpcEnv = f"{source['chain']}_RPC"
        rpc = os.getenv(rpcEnv)
        web3 = Web3(Web3.HTTPProvider(rpc))

        # Mining the data
        print(f"Mining {source['name']} ({source['chain']}) via {source['sourceType']} on {source['address']}...")
        if(source["sourceType"] == "Chainlink"): mineChainlink(source, web3)
        elif(source["sourceType"] == "Pyth"): minePyth(source)
        else: print(f"Oracle type {source['sourceType']} not supported")


# Main function to mine all or specific source
def main(mineAllSources, mineSources):
    # Mining all data sources if mineAllSources is true
    if(mineAllSources): 
        f = open(f"config/sources.json")
        sourceData = json.load(f)
        sources = fetchSourceInfo(list(sourceData.keys()))
        print(f"Mining data: {list(sourceData.keys())}")
        mineData(sources)
        # TODO: Format the data to incl. High/Low/Close/Open for each day

    # Mining the specified sources if mineAllSources is false
    else : 
        if(len(mineSources) == 0): raise Exception("No sources found for the given tickers")
        print(f"Mining data for the following: {ticker}")
        mineData(mineSources)
        # TODO: Format the data to incl. Date/High/Low/Close/Open for each day

# Mining process
main(mineAllSources, mineSources)