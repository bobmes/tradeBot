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
import math
from ta.volatility import BollingerBands
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.trend import MACD, EMAIndicator

BIGGEST_IND_PERIOD = 30
RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30

def macd(df):
    macd_func = MACD(df['close'])
    df['macd'] = macd_func.macd()
    df['macd_signal'] = macd_func.macd_signal()
    return df

def stoch(df):
    stoch_func = StochasticOscillator(df['high'], df['low'], df['close'])
    df['stoch'] = stoch_func.stoch()
    df['stoch_signal'] = stoch_func.stoch_signal()
    return df

def RSI(df):
    df['rsi'] = RSIIndicator(df['close']).rsi()
    df['rsi_signal'] = np.where(df['rsi']>RSI_OVERBOUGHT, -1, np.where(df['rsi']<RSI_OVERSOLD, 1, 0))
    return df

def SMA(df):
    df['ema'] = EMAIndicator(df['close']).ema_indicator()
    df['ema_signal'] = np.where(df['close']>df['ema'], -1, np.where(df['close']<df['ema'], 1, 0))
    return df

def bollingerBands(df):
    indicator_bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    # Calculate Bollinger Bands
    df['bb_upper']  = indicator_bb.bollinger_hband()
    df['bb_middle'] = indicator_bb.bollinger_mavg()
    df['bb_lower'] = indicator_bb.bollinger_lband()
    # Add Bollinger Band high indicator
    df['bb_bbhi'] = indicator_bb.bollinger_hband_indicator()

    # Add Bollinger Band low indicator
    df['bb_bbli'] = indicator_bb.bollinger_lband_indicator()

    return df
#%% READ DATA
df = pd.read_csv("BTCUSD-5m1676214088.743315.csv")
df = macd(df)
df = bollingerBands(df)
df = SMA(df)
df = stoch(df)
df = RSI(df)
print(df[['macd', 'macd_signal']].tail())

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

def SMA(df,faPeriod=14,slPeriod=30, siPeriod=0):
    df['ema'] = EMAIndicator(df['Close']).ema_indicator()
    return df

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
