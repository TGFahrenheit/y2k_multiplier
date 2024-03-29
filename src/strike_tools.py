import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fpdf import FPDF
import os

def output_df_to_pdf(pdf, df):
    # A cell is a rectangular area, possibly framed, which contains some text
    # Set the width and height of cell
    table_cell_width = 25
    table_cell_height = 6
    # Select a font as Arial, bold, 8
    pdf.set_font('Arial', 'B', 8)
    
    # Loop over to print column names
    cols = df.columns
    for col in cols:
        pdf.cell(table_cell_width, table_cell_height, col, align='C', border=1)
    # Line break
    pdf.ln(table_cell_height)
    # Select a font as Arial, regular, 10
    pdf.set_font('Arial', '', 10)
    # Loop over to print each data in the table
    for row in df.itertuples():
        for col in cols:
            value = str(getattr(row, col))
            pdf.cell(table_cell_width, table_cell_height, value, align='C', border=1)
        pdf.ln(table_cell_height)

def calculate_stable_strike(df_in,show_details,write_pdf,ticker):
    df = df_in.copy()
    df['price'] = df['low'].apply(lambda x: 1 if x > 1 else x)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df2 = df.resample('W').min().reset_index().dropna()

    processed_df = df2.copy()
    percentile_weekly = 100/(10)  # 10% chance of touching or going below for weekly
    
    #print(processed_df)
    if show_details == 1:
        print(f"Theoretical probability to hit weekly =  {percentile_weekly/100:.1%}")

    strike_price_weekly = np.percentile(processed_df['price'], percentile_weekly)

    if show_details == 1:
        print(f"Weekly Strike Price (10% chance of touching or going below): {strike_price_weekly}")

    # Calculate probabilities (for verification)
    total_weeks = len(processed_df)
    depeg_weeks_weekly = sum(processed_df['price'] <= strike_price_weekly)
    
    if show_details == 1:
        print(f"Total number of weeks : {total_weeks}")
        print(f"Number of depeg for weekly strike price : {depeg_weeks_weekly}")

    probability_of_depeg_weekly = depeg_weeks_weekly / total_weeks
    df2['is_depeg'] = df2['price'].apply(lambda x: 0 if x > strike_price_weekly else 1)
    records = df2[df2['is_depeg'] == 1]

    if show_details == 1:
        print(f"Probability of touching or going below for weekly based on historical data: {probability_of_depeg_weekly:.4%}")
    
        print('Date for weeks which depeg has occured in the last 365 days')
        print(records['timestamp'])
    
        ax = df.plot(y='low')
        ax.axhline(y = strike_price_weekly, color='r',alpha = 0.5, linestyle='--')
        
        for i in range(total_weeks):
            ax.axvline(x = df2['timestamp'].iloc[i],alpha = 0.2,linestyle = '--')
            
    if write_pdf == 1:
        ax = df.plot(y='low')
        ax.axhline(y = strike_price_weekly, color='r',alpha = 0.5, linestyle='--')
        
        for i in range(total_weeks):
            ax.axvline(x = df2['timestamp'].iloc[i],alpha = 0.2,linestyle = '--')
        
        save_file_path = f'output/stable/{ticker}/{ticker}_daily.png'
        
        # Check if the directory exists, if not create it
        if not os.path.exists(os.path.dirname(save_file_path)):
            os.makedirs(os.path.dirname(save_file_path))    
        
        plt.savefig(save_file_path)
        plt.close()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','',10)
        
        pdf.multi_cell(w=0, h=5,txt=f"Asset name: {ticker}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Theoretical probability to hit weekly =  {percentile_weekly/100:.1%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Weekly Strike Price (10% chance of touching or going below): {strike_price_weekly:.6}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Total number of weeks : {total_weeks}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Number of depeg for weekly strike price : {depeg_weeks_weekly}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt='Date for weeks which depeg has occured in the last 365 days')
        pdf.ln(5)
        print1 = records.drop(columns=['open', 'close','high','low']) 
        print1 = print1.round({'price': 5})
        output_df_to_pdf(pdf, print1.astype(str))
        pdf.ln(5)
        pdf.image(save_file_path,w = 150)
        
        pdf.output(f'output/stable/{ticker}/{ticker}_summary.pdf')
        print('Done')

    return strike_price_weekly,probability_of_depeg_weekly,total_weeks

def probability_stable_strike(df_in,strike_price,show_details,write_pdf,ticker):
    df = df_in.copy()
    df['price'] = df['low'].apply(lambda x: 1 if x > 1 else x)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df2 = df.resample('W').min().reset_index().dropna()

    processed_df = df2.copy()

    # Calculate probabilities (for verification)
    total_weeks = len(processed_df)
    depeg_weeks_weekly = sum(processed_df['price'] <= strike_price)
    
    if show_details == 1:
        print(f"Total number of weeks : {total_weeks}")
        print(f"Number of depeg for weekly strike price : {depeg_weeks_weekly}")

    probability_of_depeg_weekly = depeg_weeks_weekly / total_weeks
    df2['is_depeg'] = df2['price'].apply(lambda x: 0 if x > strike_price else 1)
    records = df2[df2['is_depeg'] == 1]
        
    if show_details == 1:
        print(f"Probability of touching or going below for weekly based on historical data: {probability_of_depeg_weekly:.4%}")
    
        print('Date for weeks which depeg has occured in historical data')
        
        print(records['timestamp'])
    
        ax = df.plot(y='low')
        ax.axhline(y = strike_price, color='r',alpha = 0.5, linestyle='--')
        
        for i in range(total_weeks):
            ax.axvline(x = df2['timestamp'].iloc[i],alpha = 0.2,linestyle = '--')
            
    if write_pdf == 1:
        ax = df.plot(y='low')
        ax.axhline(y = strike_price, color='r',alpha = 0.5, linestyle='--')
        
        for i in range(total_weeks):
            ax.axvline(x = df2['timestamp'].iloc[i],alpha = 0.2,linestyle = '--')
        
        save_file_path = f'output/stable/{ticker}/{ticker}_daily.png'
        
        # Check if the directory exists, if not create it
        if not os.path.exists(os.path.dirname(save_file_path)):
            os.makedirs(os.path.dirname(save_file_path))    
        
        plt.savefig(save_file_path)
        plt.close()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','',10)
        
        pdf.multi_cell(w=0, h=5,txt=f"Asset name: {ticker}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Probability of touching or going below for weekly based on historical data: {probability_of_depeg_weekly:.4%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Weekly Strike Price (10% chance of touching or going below): {strike_price:.4}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Total number of weeks : {total_weeks}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Number of depeg for weekly strike price : {depeg_weeks_weekly}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt='Date for weeks which depeg has occured in the last 365 days')
        pdf.ln(5)
        print1 = records.drop(columns=['open', 'close','high','low'])
        print1 = print1.round({'price': 5})
        output_df_to_pdf(pdf, print1.astype(str))
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt='Price in last year')
        pdf.ln(5)
        pdf.image(save_file_path,w = 150)
        
        pdf.output(f'output/stable/{ticker}/{ticker}_summary.pdf')
        print('Done')
        
    return probability_of_depeg_weekly
        
def calculate_turbo_strikes(price_history_in,desired_prob,day,show,write_pdf,ticker):
    week_day = f'W-{day}'
    
    price_history = price_history_in.copy()
    price_history['timestamp'] = pd.to_datetime(price_history['timestamp'])
    price_history.set_index('timestamp', inplace=True)

    df1 = price_history.resample(week_day).first().reset_index().dropna()
    df2 = price_history.resample(week_day).max().reset_index().dropna()
    df3 = price_history.resample(week_day).min().reset_index().dropna()
    
    #print(df1[0:5])

    df1['ratio_u'] = df2['high']/df1['open']
    df1['ratio_d'] = df3['low']/df1['open']

    df1['inc_m'] = np.abs(df1['ratio_u'].rolling(window=4).max()-1)
    df1['dec_m'] = np.abs(df1['ratio_d'].rolling(window=4).min()-1)
    df1['ch_m'] = df1[['dec_m','inc_m']].max(axis=1)
    df1['last_week_ch_m'] = df1['ch_m'].shift(1)
    df1 = df1.dropna()

    initial_u_r = 2
    initial_d_r = 2

    up_count = 100
    down_count = 100

    week_num = len(df1.index)
    
    while ((up_count/week_num > desired_prob) or (down_count/week_num > desired_prob)):
        df1['inc_lim'] = (1 + initial_u_r/100)**(1+10*df1['last_week_ch_m'])
        df1['dec_lim'] = (1 - initial_d_r/100)**(1+10*df1['last_week_ch_m'])
        
        df1['up_depeg'] = 0
        df1['d_depeg'] = 0
        
        df1['up_depeg'] = np.where(df1['ratio_u'] > df1['inc_lim'],1,0)
        df1['d_depeg'] = np.where(df1['ratio_d'] < df1['dec_lim'],1,0)   

        up_count = df1['up_depeg'].sum()
        down_count = df1['d_depeg'].sum()

        if up_count/week_num > desired_prob:
            initial_u_r = initial_u_r + 0.1

        if down_count/week_num > desired_prob:
            initial_d_r = initial_d_r + 0.1

    
    result1_df = df1[df1['up_depeg'] == 1]
    up_depeg_dates = result1_df['timestamp']

    result2_df = df1[df1['d_depeg'] == 1]
    d_depeg_dates = result2_df['timestamp']

    if show == 1:
        print(initial_u_r)
        print(initial_d_r)
        print('Up depeg dates')
        print(up_depeg_dates)
        print('Down depeg dates')
        print(d_depeg_dates)
        
        fig, ax = plt.subplots(figsize=(10,6))

        ax.plot(df1['timestamp'],df1['ratio_u'], label='Increase')
        ax.plot(df1['timestamp'],df1['ratio_d'], label='Decrease')
        ax.step(df1['timestamp'],df1['inc_lim'], label='Increase limit')
        ax.step(df1['timestamp'],df1['dec_lim'], label='Decrease limit')
        ax.legend()

        ax2 = ax.twinx()
        ax2.plot(price_history['open'],color='red')
        plt.show()
        
    change_amount = df1['ch_m'].iloc[-1]
    
    inc_lim = (1 + initial_u_r/100)**(1+10*change_amount)
    dec_lim = (1 - initial_d_r/100)**(1+10*change_amount)
    
    if write_pdf == 1:
        fig, ax = plt.subplots(figsize=(10,6))

        ax.plot(df1['timestamp'],df1['ratio_u'], label='Increase')
        ax.plot(df1['timestamp'],df1['ratio_d'], label='Decrease')
        ax.step(df1['timestamp'],df1['inc_lim'], label='Increase limit')
        ax.step(df1['timestamp'],df1['dec_lim'], label='Decrease limit')
        ax.legend()

        #ax2 = ax.twinx()
        #ax2.plot(price_history['open'],color='red')
        
        save_file_path1 = f'output/turbo/{ticker}/{ticker}_daily.png'
        
        # Check if the directory exists, if not create it
        if not os.path.exists(os.path.dirname(save_file_path1)):
            os.makedirs(os.path.dirname(save_file_path1))    
        
        plt.savefig(save_file_path1)
        plt.close()
        
        fig, ax = plt.subplots(figsize=(10,6))
        ax.plot(price_history['open'], label='Price')
        ax.legend()
        save_file_path2 = f'output/turbo/{ticker}/{ticker}_price.png'
        
        plt.savefig(save_file_path2)
        plt.close()
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','',10)
        
        pdf.multi_cell(w=0, h=5,txt=f"Touch up strike: {(inc_lim-1):.3%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Probability of touching up based on historical data: {up_count/week_num:.1%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Touch down strike: {(dec_lim-1):.3%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Probability of touching down based on historical data: {down_count/week_num:.1%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Total number of weeks : {week_num}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt='Date for weeks which touch up depeg has occured in the last 365 days')
        pdf.ln(5)
        print_1 = result1_df.drop(columns=['open', 'close','high','low','inc_m','dec_m','ch_m','last_week_ch_m'])
        output_df_to_pdf(pdf, print_1.round(4).astype(str))
        
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt='Date for weeks which touch down depeg has occured in the last 365 days')
        pdf.ln(5)
        print_2 = result2_df.drop(columns=['open', 'close','high','low','inc_m','dec_m','ch_m','last_week_ch_m'])
        output_df_to_pdf(pdf, print_2.round(4).astype(str))
        pdf.ln(5)
        pdf.add_page()
        pdf.multi_cell(w=0, h=5,txt='Price in last year')
        pdf.ln(5)
        pdf.image(save_file_path2,w = 150)
        pdf.ln(5)
        pdf.image(save_file_path1,w = 150)
        
        pdf.output(f'output/turbo/{ticker}/{ticker}_summary.pdf')
        print('Done')
        
        
    return (inc_lim-1)*100,(dec_lim-1)*100,up_count/week_num*100,down_count/week_num*100,week_num

def calculate_cvi_strike(df_in,show, write_pdf):   
    df = df_in.copy()
    df['price'] = df['open']/(1E11) 
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)

    df1 = df.resample('W').first().reset_index().dropna()
    df2 = df.resample('W').max().reset_index().dropna()
    
    df1['ratio'] = df2['price']/df1['price']
    
    increase = np.percentile(df1['ratio'],93)

    if show == 1:
        fig, ax = plt.subplots(figsize=(10,6))

        ax.plot(df1['timestamp'],df1['ratio'])
        plt.axhline(y = increase,alpha = 0.2,linestyle = '--')
        plt.show()
        
    if write_pdf == 1:
        fig, ax = plt.subplots(figsize=(10,6))

        ax.plot(df1['timestamp'],df1['ratio'])
        plt.axhline(y = increase,alpha = 0.2,linestyle = '--')
        
        save_file_path1 = f'output/volatility/cvi/cvi_daily.png'
        
        # Check if the directory exists, if not create it
        if not os.path.exists(os.path.dirname(save_file_path1)):
            os.makedirs(os.path.dirname(save_file_path1))    
        
        plt.savefig(save_file_path1)
        plt.close()
        
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','',10)
        
        pdf.multi_cell(w=0, h=5,txt=f"CVI touch up strike: {(increase-1):.3%}")
        pdf.ln(5)
        pdf.image(save_file_path1,w = 150)
        
        pdf.output(f'output/volatility/cvi/cvi_summary.pdf')
        print('Done')

    return increase

def calculate_volatility_strike(df_in, window_size, show, write_pdf, ticker):
    
    df = df_in.copy()
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    rolling_realized_volatility = df['log_return'].rolling(window=window_size).std(ddof=0) * np.sqrt(365)
    
    # Calculate Bollinger Bands for the realized volatility
    rolling_mean = rolling_realized_volatility.rolling(window=7).mean()
    rolling_std = rolling_realized_volatility.rolling(window=30).std()
    upper_band = rolling_mean + (rolling_std * 2)
    lower_band = rolling_mean - (rolling_std * 2)
    
    increase_up = upper_band[364]/rolling_mean[364]
    increase_d = lower_band[364]/rolling_mean[364]
    
    #print(upper_band[364])
    #print(lower_band[364])
    #print(rolling_mean[364])
    #print(rolling_realized_volatility[364])
    
    if show == 1:
        # Create a figure and axis for better control over the plot
        fig, ax = plt.subplots(figsize=(10,6))

        # Plot the rolling realized volatility and its Bollinger Bands
        ax.plot(rolling_realized_volatility[window_size-1:], label='Realized Volatility')
        ax.plot(upper_band, label='Upper Bollinger Band', linestyle='--')
        ax.plot(lower_band, label='Lower Bollinger Band', linestyle='--')
        ax.set_title('Historical Realized Volatility with Bollinger Bands')
        ax.set_xlabel('Date')
        ax.set_ylabel('Realized Volatility')
        ax.legend()
        ax.grid(visible=1)

        # Improve formatting of dates on x-axis
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        plt.show()
        
    if write_pdf == 1:
        fig, ax = plt.subplots(figsize=(10,6))

        ax.plot(rolling_realized_volatility[window_size-1:], label='Realized Volatility')
        ax.plot(upper_band, label='Upper Bollinger Band', linestyle='--')
        ax.plot(lower_band, label='Lower Bollinger Band', linestyle='--')
        ax.set_title('Historical Realized Volatility with Bollinger Bands')
        ax.set_xlabel('Date')
        ax.set_ylabel('Realized Volatility')
        ax.legend()
        ax.grid(visible=1)

        # Improve formatting of dates on x-axis
        ax.fmt_xdata = mdates.DateFormatter('%Y-%m-%d')
        fig.autofmt_xdate()
        
        save_file_path1 = f'output/volatility/{ticker}/{ticker}_daily.png'
        
        # Check if the directory exists, if not create it
        if not os.path.exists(os.path.dirname(save_file_path1)):
            os.makedirs(os.path.dirname(save_file_path1))    
        
        plt.savefig(save_file_path1)
        plt.close()
        
        
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('arial','',10)
        
        pdf.multi_cell(w=0, h=5,txt=f"Touch up strike: {(increase_up-1):.3%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Touch down strike: {(increase_d-1):.3%}")
        pdf.ln(5)
        pdf.multi_cell(w=0, h=5,txt=f"Last volatility value:{rolling_realized_volatility[364]:.3}")
        pdf.ln(5)
        pdf.image(save_file_path1,w = 150)
        
        pdf.output(f'output/volatility/{ticker}/{ticker}_summary.pdf')
        print('Done')
    
    return increase_up, increase_d, rolling_realized_volatility[364]

        
    
