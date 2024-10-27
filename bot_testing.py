# -*- coding: utf-8 -*-
"""
Created on Sat Jan 23 17:24:23 2021

@author: bob_m
"""
# import os
# os.chdir("C://Users//bob_m//Desktop//Persoonlijk//Trade bot//CODE")

#%%
#import websocket, json, pprint
import numpy as np
import pandas as pd
import copy
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator

BIGGEST_IND_PERIOD = 30
WINDOW = 14
SMOOTH_WINDOW = 3
BB_WINDOW = 20
BB_WINDOW_DEV = 2
RSI_OVERBOUGHT = 90
RSI_OVERSOLD = 10

def macd(df):
    macd_func = MACD(df['close'])
    df['macd'] = macd_func.macd()
    df['macd_signal'] = macd_func.macd_signal()
    df['macd_buy'] = np.where(df['macd']>df['macd_signal'], 1, np.where(df['macd']<df['macd_signal'], -1, 0))
    return df

def stoch(df):
    stoch_func = StochasticOscillator(df['high'], df['low'], df['close'], window=WINDOW, smooth_window=SMOOTH_WINDOW)
    df['stoch'] = stoch_func.stoch()
    df['stoch_buy'] = np.where(df['stoch']>RSI_OVERBOUGHT, -1, np.where(df['stoch']<RSI_OVERSOLD, 1, 0))
    return df

def RSI(df):
    df['rsi'] = RSIIndicator(df['close'], window=WINDOW).rsi()
    df['rsi_buy'] = np.where(df['rsi']>RSI_OVERBOUGHT, -1, np.where(df['rsi']<RSI_OVERSOLD, 1, 0))
    return df

def SMA(df):
    df['ema'] = EMAIndicator(df['close'], window=WINDOW).ema_indicator()
    df['ema_buy'] = np.where(df['close']>df['ema'], -1, np.where(df['close']<df['ema'], 1, 0))
    return df

def bollingerBands(df):
    indicator_bb = BollingerBands(close=df["close"], window=BB_WINDOW, window_dev=BB_WINDOW_DEV)
    # Calculate Bollinger Bands
    df['bb_upper']  = indicator_bb.bollinger_hband()
    df['bb_middle'] = indicator_bb.bollinger_mavg()
    df['bb_lower'] = indicator_bb.bollinger_lband()
    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

    df['bb_buy'] = np.where(df['bb_bbli']==1, 1, np.where(df['bb_bbhi']==1, -1, 0))
    return df

def buy_or_sell(df):
    df['sum_buy_signals'] = df['macd_buy'] + df['stoch_buy'] + df['rsi_buy'] + df['bb_buy']
    return df
#%% READ DATA
df_btc = pd.read_csv("btc_eur.csv")
df_btc['datetime'] = pd.to_datetime(df_btc['time'])
df_eth = pd.read_csv("eth_eur.csv")
df_eth['datetime'] = pd.to_datetime(df_eth['time'])
df_ada = pd.read_csv("ada_eur.csv")
df_ada['datetime'] = pd.to_datetime(df_ada['time'])
df_atom = pd.read_csv("atom_eur.csv")
df_atom['datetime'] = pd.to_datetime(df_atom['time'])
df_dot = pd.read_csv("dot_eur.csv")
df_dot['datetime'] = pd.to_datetime(df_dot['time'])
df_sol = pd.read_csv("sol_eur.csv")
df_sol['datetime'] = pd.to_datetime(df_sol['time'])
df_link = pd.read_csv("link_eur.csv")
df_link['datetime'] = pd.to_datetime(df_link['time'])
df_matic = pd.read_csv("matic_eur.csv")
df_matic['datetime'] = pd.to_datetime(df_matic['time'])

def calculate_ta_analysis(df):
    df = macd(df)
    df = bollingerBands(df)
    df = SMA(df)
    df = stoch(df)
    df = RSI(df)
    df = buy_or_sell(df)
    return df
df_btc = calculate_ta_analysis(df_btc)
df_eth = calculate_ta_analysis(df_eth)
df_ada = calculate_ta_analysis(df_ada)
df_atom = calculate_ta_analysis(df_atom)
df_dot = calculate_ta_analysis(df_dot)
df_sol = calculate_ta_analysis(df_sol)
df_link = calculate_ta_analysis(df_link)
df_matic = calculate_ta_analysis(df_matic)

#%%
def simulate_trade_bot(df, money, name_coin, perc_transaction_fee=0.001, transaction_logging=False):
    money_start = copy.deepcopy(money)
    num_coins = 0
    zero_sell_one_buy = 1
    transaction_fees = 0
    transactions = 0

    df['date_only'] = pd.to_datetime(df['time'])
    date_only = df['date_only'].dt.date
    num_days = len(date_only.unique())

    for i in range(len(df)):
        if (df.loc[i, 'sum_buy_signals'] == 3) and (zero_sell_one_buy == 1):
            zero_sell_one_buy = 0
            num_coins = ((money * (1-perc_transaction_fee)) / df.loc[i+1, 'open'])
            transaction_fees += money * perc_transaction_fee
            revenue = money - transaction_fees
            money = 0
            transactions += 1
            
            if transaction_logging:
                print(f"Buying on: {df.loc[i+1, 'time']} | for: {df.loc[i+1, 'open']} | transaction fees: {transaction_fees}")
                print(f"Total worth: {((money * 0.999) / df.loc[i+1, 'open'])}")

        if (df.loc[i, 'sum_buy_signals'] == -3) and (zero_sell_one_buy == 0):
            zero_sell_one_buy = 1
            money = (num_coins * df.loc[i+1, 'open']) * (1-perc_transaction_fee)
            transaction_fees += money * perc_transaction_fee
            num_coins = 0
            transactions += 1
            revenue = money - revenue - transaction_fees

            if transaction_logging:
                print(f"Selling on: {df.loc[i+1, 'time']} | for: {df.loc[i+1, 'open']} | transaction fees: {transaction_fees}")
                print(f"Total worth: {money} | revenue on buy sell: {revenue}")

    print(f"Coin: {name_coin}")
    print(f"Koers start: {df.loc[0, 'open']}, Koers end: {df.loc[len(df)-1, 'close']}")
    if money > 0:
        print(f"Money: {money}")
    if num_coins > 0:
        print(f"Number of coins: {num_coins}")
        print(f"The coins worth: {num_coins*df.loc[len(df)-1, 'close']}")
        money = num_coins*df.loc[len(df)-1, 'close']
    print(f"Transaction fees: {transaction_fees}")
    print(f"Transactions: {transactions}")

    profit = money - money_start
    perc_profit = profit / money_start
    profit_per_day = perc_profit / num_days
    profit_per_year = profit_per_day * 365
    print(f"Profit: {profit}, % Profit: {perc_profit}, % Profit per Day: {profit_per_day}, % Profit per Year: {profit_per_year}")

 
simulate_trade_bot(df_btc, 200, "BTC", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_eth, 200, "ETH", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_ada, 200, "ADA", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_atom, 200, "ATOM", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_dot, 200, "DOT", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_sol, 200, "SOL", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_link, 200, "LINK", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_matic, 200, "MATIC", perc_transaction_fee=0.001, transaction_logging=False)
#%%
df_btc = df_btc.loc[df_btc['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_eth = df_eth.loc[df_eth['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_ada = df_ada.loc[df_ada['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_atom = df_atom.loc[df_atom['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_dot = df_dot.loc[df_dot['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_sol = df_sol.loc[df_sol['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_link = df_link.loc[df_link['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)
df_matic = df_matic.loc[df_matic['datetime'] >= pd.to_datetime('2022-08-01'),:].reset_index(drop=True)

simulate_trade_bot(df_btc, 200, "BTC", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_eth, 200, "ETH", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_ada, 200, "ADA", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_atom, 200, "ATOM", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_dot, 200, "DOT", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_sol, 200, "SOL", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_link, 200, "LINK", perc_transaction_fee=0.001, transaction_logging=False)
simulate_trade_bot(df_matic, 200, "MATIC", perc_transaction_fee=0.001, transaction_logging=False)
#%%

# #%%
# course = []
# for i in range(len(df)):
#     close = df.loc[i, 'Close']
#     if not math.isnan(close):
#         old_close = close
    
#     if math.isnan(close):
#         course.append(old_close)
#     else:
#         course.append(old_close)
        
#     if len(course) > 60:
#         del course[0]
    
#     np_course = np.array(course)
#     if len(course) >= BIGGEST_IND_PERIOD:
# # =============================================================================
# #         # Bollinger bands
# #         upperband, middleband, lowerband = talib.BBANDS(np_course, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
# #         print(lowerband)
# # =============================================================================
        
#         # MACD
#         macd, macdsignal, macdhist = ta.MACD(np_course, fastperiod=12, slowperiod=26, signalperiod=9)
#         print(macdhist)
# # =============================================================================
# #         # RSI
# #         rsi = talib.RSI(np_course, RSI_PERIOD)
# #         last_rsi = rsi[-1]
# #         
# #         # Stochastic
# #         #slowk, slowd = talib.STOCH(high, low, np_course, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
# # 
# #         # Exponential moving average
# #         real = talib.EMA(np_course, timeperiod=30)
# # =============================================================================
        
        
    
#     if i == 2000:
#         break
    
#%%
# def Stoch(close,  high, low):
#     slowk, slowd = ta.STOCH(high, low, close)
#     stochSell = ((slowk < slowd) & (slowk.shift(1) > slowd.shift(1))) & (slowd > 80)
#     stochBuy = ((slowk > slowd) & (slowk.shift(1) < slowd.shift(1))) & (slowd < 20)
#     return stochSell,stochBuy, slowk,slowd
# def macd(df):
#     macd_func = MACD(df['close'])
#     df['macd'] = macd_func.macd()
#     df['macd_signal'] = macd_func.macd_signal()
#     return df

# def stoch():
#     stoch_func = StochasticOscillator(df['high'], df['low'], df['close'])
#     df['stoch'] = stoch_func.stoch()
#     df['stoch_signal'] = stoch_func.stoch_signal()
#     return df

# def RSI(df,timePeriod=14):
#     df['rsi'] = RSIIndicator(df['close']).rsi()
#     df['rsi_signal'] = np.where(df['rsi']>RSI_OVERBOUGHT, -1, np.where(df['rsi']<RSI_OVERSOLD, 1, 0))
#     return df

# def SMA(close,sPeriod,lPeriod):
#     shortSMA = ta.SMA(close,sPeriod)
#     longSMA = ta.SMA(close,lPeriod)
#     smaSell = ((shortSMA <= longSMA) & (shortSMA.shift(1) >= longSMA.shift(1)))
#     smaBuy = ((shortSMA >= longSMA) & (shortSMA.shift(1) <= longSMA.shift(1)))
#     return smaSell,smaBuy,shortSMA,longSMA

# def SMA(df,faPeriod=14,slPeriod=30, siPeriod=0):
#     df['ema'] = EMAIndicator(df['Close']).ema_indicator()
#     return df

# def bollingerBands(df, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0):
#     # Calculate Bollinger Bands
#     df['bb_upper'], df['bb_middle'], df['bb_lower'] = BollingerBands(df['Close']).bollinger_bands()
#     return df
# #%%
# # Bollinger bands
# upperband, middleband, lowerband = BBANDS(close, timeperiod=5, nbdevup=2, nbdevdn=2, matype=0)
    
# # MACD
# macd, macdsignal, macdhist = MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)

# # RSI
# real = RSI(close, timeperiod=14)

# # Stochastic
# slowk, slowd = STOCH(high, low, close, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)

# # Exponential moving average
# real = EMA(close, timeperiod=30)
