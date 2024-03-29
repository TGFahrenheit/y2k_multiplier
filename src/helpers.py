import json
import pandas as pd

# Fetching the list of source based on the tickers input
def fetchSourceInfo(tickers: list):
    f = open(f"config/sources.json")
    sources = json.load(f)
    sourceList = []
    
    # Iterate over each ticker in the input list
    for ticker in tickers:
        ticker = ticker.lower()
        # Check if the ticker is in the sources dictionary
        if ticker in sources:
            # Append the source information to sourceList
            sourceList.append(sources[ticker])
        else:
            print(f"No source found for ticker: {ticker}")

    if(len(sourceList) == 0): 
        raise Exception("No sources found for the given tickers")
    if(len(sourceList) != len(tickers)): 
        raise Exception("Some tickers do not have sources")

    return sourceList

# Generic function called after all mining processes
def finalizeMine(TICKER):
    check_for_duplicates(TICKER)
    csv_format_daily(TICKER)

# Checking the mined data for duplicates
def check_for_duplicates(TICKER):
    ticker = TICKER.lower()
    file_path = f'data/{ticker}/{ticker}.csv'
    df = pd.read_csv(file_path, index_col=0)

    # Check for duplicates
    duplicate_rows = df[df.duplicated(['roundId'])]
    if not duplicate_rows.empty:
        print(f"Warning: Found {duplicate_rows.shape[0]} duplicate roundId values!")
        print(duplicate_rows)

        # Drop duplicates
        df = df.drop_duplicates(subset='roundId', keep='first')
        df.to_csv(file_path)
        print(f"Duplicates removed. Updated dataset saved for {ticker.upper()}.")
    else:
        return

# Formatting the mined data
def csv_format_daily(TICKER):
    ticker = TICKER.lower()

    # Load the data and group by date using 'updatedAt'
    df = pd.read_csv(f'data/{ticker}/{ticker}.csv', index_col=0)
    df['timestamp'] = pd.to_datetime(df['updatedAt'], unit='s')
    if ticker == "steth":
        df['price'] = df['price'].astype(float)/(1E10)
    df['price'] = df['price'].astype(float)/(1E8)
    #df.rename(columns={'updatedAt': 'timestamp'}, inplace=True)
    df.set_index('timestamp', inplace=True)
    daily_groups = df.resample('D')
    
    # Calculate OHLCV for each day and rename columns
    ohlcv = daily_groups.agg({
        'price': ['first', 'last', 'max', 'min'],
    })
    ohlcv.columns = ['open', 'close', 'high', 'low']
    
    # Save the result to a new CSV file
    ohlcv.to_csv(f'data/{ticker}/{ticker}_daily.csv')