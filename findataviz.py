#Pandas PLTR Financial Plots
# IMPORTING PACKAGES

import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from math import floor
from termcolor import colored as cl

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (12,7)

# EXTRACTING STOCK DATA

def get_historical_data(symbol, start_date):
    api_key = 'YOUR API KEY'
    api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)
    return df

tcs = get_historical_data('PLTR', '2020-01-01')

tcs

tcs1=tcs.reset_index()
tcs1.tail()

print(tcs1.columns.tolist())

#Closing Price PLot
tcs['close'].plot()
plt.show()
#Volume Plot
tcs['volume'].plot()
plt.show()

# Isolate the adjusted closing prices 
adj_close_px = tcs['close']

# Short moving window rolling mean
tcs['20'] = adj_close_px.rolling(window=20).mean()

# Long moving window rolling mean
tcs['50'] = adj_close_px.rolling(window=50).mean()

# Plot the adjusted closing price, the short and long windows of rolling means
tcs[['close', '20', '50']].plot()

plt.show()

tcs['daily_change_pct'] = tcs['close'].pct_change()*100
tcs['returns'] = tcs['daily_change_pct'] / tcs['close']  

tcs['daily_change_pct'].fillna(0)
tcs['daily_change_pct'].hist(bins = 50, figsize = (10,5)) 
plt.xlabel('Daily Change Percentage')
plt.ylabel('Frequency')
plt.show()
#print the statistics on daily change percentage
tcs.daily_change_pct.describe()

tcs_vol = tcs['volume'].rolling(7).std()*np.sqrt(7)
tcs_vol.plot(figsize = (10, 6))
plt.show()

def daily_trend(x):
    if x > -0.5 and x <= 0.5:
        return 'No change'
    elif x > 0.5 and x <= 2:
        return 'Upto 2% Increase'
    elif x > -2 and x <= -0.5:
        return 'Upto 2% Decrease'
    elif x > 2 and x <= 5:
        return '2-5% Increase'
    elif x > -5 and x <= -2:
        return '2-5% Decrease'
    elif x > 5 and x <= 10:
        return '5-10% Increase'
    elif x > -10 and x <= -5:
        return '5-10% Decrease'
    elif x > 10:
        return '>10% Increase'
    elif x <= -10:
        return '>10% Decrease'

tcs['Trend']= np.zeros(tcs['daily_change_pct'].count()+1)
tcs['Trend']= tcs['daily_change_pct'].apply(lambda x:daily_trend(x))
tcs['Trend'].replace('None','No change')
#tcs.head()

tcs_pie_data = tcs.groupby('Trend')
pie_label = tcs_pie_data['Trend'].unique()
plt.pie(tcs_pie_data['Trend'].count(), labels = pie_label, 
        autopct = '%1.1f%%', radius = 2 )
plt.show()
ax=tcs_pie_data['Trend'].count().sort_values(ascending=False).plot.bar(rot=90)
plt.show()

#scipy PDF of PLTR Daily Returns

import matplotlib.pyplot as plt
from scipy.stats import norm
mu = tcs['LogReturn'].mean()
sigma = tcs['LogReturn'].std(ddof=1)

density = pd.DataFrame()
density['x'] = np.arange(tcs['LogReturn'].min()-0.01, tcs['LogReturn'].max()+0.01, 0.001)
density['pdf'] = norm.pdf(density['x'], mu, sigma)

tcs['LogReturn'].hist(bins=50, figsize=(15, 8))
plt.plot(density['x'], density['pdf'], color='red')
plt.show()

#mplfinance PLTR Candlesticks & Indicators

import mplfinance as mpf

mpf.plot(tcs, type='candle', mav = (20, 50, 90, 180, 365), volume = True)

from finta import TA

fin_tcs = tcs.copy()
print(fin_tcs.tail())
ohlc=fin_tcs
#will return Pandas Series object with "SMA" values
print(TA.SMA(ohlc, 42))
#will return Pandas Series object with "Awesome oscillator" values
TA.AO(ohlc)
#expects ["volume"] column as input
print(TA.OBV(ohlc))
#will return Series with Bollinger Bands columns [BB_UPPER, BB_LOWER]
print(TA.BBANDS(ohlc))
#will return Series with calculated BBANDS values but will use KAMA instead of MA for calculation, other types of Moving Averages are allowed as well.
#print(TA.BBANDS(ohlc, MA=TA.KAMA(ohlc, 20)))

# calc bol band
bbands = TA.BBANDS(fin_tcs, 30)

# cherry pick what to show on the chart
bands_plot = pd.concat([bbands.BB_UPPER, bbands.BB_LOWER], axis=1)

apd = mpf.make_addplot(bands_plot.tail(300))

mpf.plot(fin_tcs.tail(300), type='candle', style='charles',
        title='PLTR BBANDS(30)',
        ylabel='Price (USD)',
        ylabel_lower='Volume',
        volume=True,
        figscale=1.5,
        addplot=apd
        )

apd = mpf.make_addplot(bands_plot.head(300))

mpf.plot(fin_tcs.head(300), type='candle', style='charles',
        title='PLTR BBANDS(30)',
        ylabel='Price (USD)',
        ylabel_lower='Volume',
        volume=True,
        figscale=1.5,
        addplot=apd
        )

#Plotly PLTR Candlesticks & Indicators

#OHLC Plot using Plotly
import plotly.graph_objects as go

fig = go.Figure(data=go.Ohlc(x=tcs1['datetime'],
        open=tcs1['open'],
        high=tcs1['high'],
        low=tcs1['low'],
        close=tcs1['close']))
fig.show()

tcs['SMA5'] = tcs.close.rolling(5).mean()
tcs['SMA20'] = tcs.close.rolling(20).mean()
tcs['SMA50'] = tcs.close.rolling(50).mean()
tcs['SMA200'] = tcs.close.rolling(200).mean()
tcs['SMA500'] = tcs.close.rolling(500).mean()

fig = go.Figure(data=[go.Ohlc(x=tcs1['datetime'],
                              open=tcs['open'],
                              high=tcs['high'],
                              low=tcs['low'],
                              close=tcs['close'], name = "OHLC"),
                      go.Scatter(x=tcs1.datetime, y=tcs.SMA5, line=dict(color='orange', width=1), name="SMA5"),
                      go.Scatter(x=tcs1.datetime, y=tcs.SMA20, line=dict(color='green', width=1), name="SMA20"),
                      go.Scatter(x=tcs1.datetime, y=tcs.SMA50, line=dict(color='blue', width=1), name="SMA50"),
                      go.Scatter(x=tcs1.datetime, y=tcs.SMA200, line=dict(color='violet', width=1), name="SMA200"),
                      go.Scatter(x=tcs1.datetime, y=tcs.SMA500, line=dict(color='purple', width=1), name="SMA500")])
fig.show()

tcs['EMA5'] = tcs.close.ewm(span=5, adjust=False).mean()
tcs['EMA20'] = tcs.close.ewm(span=20, adjust=False).mean()
tcs['EMA50'] = tcs.close.ewm(span=50, adjust=False).mean()
tcs['EMA200'] = tcs.close.ewm(span=200, adjust=False).mean()
tcs['EMA500'] = tcs.close.ewm(span=500, adjust=False).mean()

fig = go.Figure(data=[go.Ohlc(x=tcs1['datetime'],
                              open=tcs['open'],
                              high=tcs['high'],
                              low=tcs['low'],
                              close=tcs['close'], name = "OHLC"),
                      go.Scatter(x=tcs1.datetime, y=tcs.EMA5, line=dict(color='orange', width=1), name="EMA5"),
                      go.Scatter(x=tcs1.datetime, y=tcs.EMA20, line=dict(color='green', width=1), name="EMA20"),
                      go.Scatter(x=tcs1.datetime, y=tcs.EMA50, line=dict(color='blue', width=1), name="EMA50"),
                      go.Scatter(x=tcs1.datetime, y=tcs.EMA200, line=dict(color='violet', width=1), name="EMA200"),
                      go.Scatter(x=tcs1.datetime, y=tcs.EMA500, line=dict(color='purple', width=1), name="EMA500")])
fig.show()

from plotly.subplots import make_subplots
import plotly.graph_objects as go

# calculate MACD values
tcs.ta.macd(close='close', fast=12, slow=26, append=True)
# Force lowercase (optional)
tcs.columns = [x.lower() for x in tcs.columns]
# Construct a 2 x 1 Plotly figure
fig = make_subplots(rows=2, cols=1)
# price Line
fig.append_trace(
    go.Scatter(
        x=tcs.index,
        y=tcs['open'],
        line=dict(color='lawngreen', width=1),
        name='open',
        # showlegend=False,
        legendgroup='1',
    ), row=1, col=1
)
# Candlestick chart for pricing
fig.append_trace(
    go.Candlestick(
        x=tcs.index,
        open=tcs['open'],
        high=tcs['high'],
        low=tcs['low'],
        close=tcs['close'],
        increasing_line_color='lawngreen',
        decreasing_line_color='black',
        showlegend=False
    ), row=1, col=1
)
# Fast Signal (%k)
fig.append_trace(
    go.Scatter(
        x=tcs.index,
        y=tcs['macd_h'],
        line=dict(color='lawngreen', width=2),
        name='macd',
        # showlegend=False,
        legendgroup='2',
    ), row=2, col=1
)

# Slow signal (%d)
fig.append_trace(
    go.Scatter(
        x=tcs.index,
        y=tcs['macd_s'],
        line=dict(color='mediumblue', width=2),
        # showlegend=False,
        legendgroup='2',
        name='signal'
    ), row=2, col=1
)



# Colorize the histogram values
colors = np.where(tcs['macd_h'] < 0, '#000', 'lawngreen')
# Plot the histogram
fig.append_trace(
    go.Bar(
        x=tcs.index,
        y=tcs['macd_h'],
        name='histogram',
        marker_color=colors,
    ), row=2, col=1
)

# Make it pretty
layout = go.Layout(
    plot_bgcolor='linen',
    # Font Families
    font_family='Monospace',
    font_color='mediumblue',
    font_size=20,
    xaxis=dict(
        rangeslider=dict(
            visible=False
        )
    )
)
# Update options and show plot
fig.update_layout(layout)
fig.update_layout(height=800,width=1000,dragmode='lasso')
fig.show()

import os
import numpy as np
import pandas as pd
import plotly.express as py
import plotly.graph_objects as go
from plotly.subplots import make_subplots

df=tcs.copy()
dfs=df.reset_index()

def bolinger(data):
    data['MA20'] = data.close.rolling(window=20).mean()
    data['std'] = data.close.rolling(window=20).std()
    data['upper_20'] = data.MA20 + 2 * data['std']
    data['lower_20'] = data.MA20 - 2 * data['std']
    data.drop('std',axis=1,inplace=True)
    data.dropna(inplace=True)
    return data

dfs = bolinger(dfs)
dfs.ffill(inplace=True)
dfs.reset_index(drop=True,inplace=True)

fig = make_subplots(specs=[[{'secondary_y':True}]])
fig.add_trace(
    go.Scatter(x=dfs.datetime,y=dfs.close,name='close')
)
fig.add_trace(
    go.Scatter(x=dfs.datetime,y=dfs.upper_20,name='Upper 20')
)
fig.add_trace(
    go.Scatter(x=dfs.datetime,y=dfs.lower_20,name='Lower 20')
)
fig.update_layout(title='Bollinger Bands',
                  xaxis_title='Date',
                  yaxis_title='Price'
                 )
fig.show()

#PLTR KST Trading Strategy in Matplotlib

import pandas as pd
import numpy as np
import requests
import matplotlib.pyplot as plt
from math import floor
from termcolor import colored as cl

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (12,7)

# EXTRACTING STOCK DATA

def get_historical_data(symbol, start_date):
    api_key = 'a07d718849d64be78e8a7d5669e4e3af'
    api_url = f'https://api.twelvedata.com/time_series?symbol={symbol}&interval=1day&outputsize=5000&apikey={api_key}'
    raw_df = requests.get(api_url).json()
    df = pd.DataFrame(raw_df['values']).iloc[::-1].set_index('datetime').astype(float)
    df = df[df.index >= start_date]
    df.index = pd.to_datetime(df.index)
    return df

aapl = get_historical_data('PLTR', '2020-01-01')
 
aapl


# ROC CALCULATION

def get_roc(close, n):
    difference = close.diff(n)
    nprev_values = close.shift(n)
    roc = (difference / nprev_values) * 100
    return roc
  
  # KST CALCULATION

def get_kst(close, sma1, sma2, sma3, sma4, roc1, roc2, roc3, roc4, signal):
    rcma1 = get_roc(close, roc1).rolling(sma1).mean()
    rcma2 = get_roc(close, roc2).rolling(sma2).mean()
    rcma3 = get_roc(close, roc3).rolling(sma3).mean()
    rcma4 = get_roc(close, roc4).rolling(sma4).mean()
    kst = (rcma1 * 1) + (rcma2 * 2) + (rcma3 * 3) + (rcma4 * 4)
    signal = kst.rolling(signal).mean()
    return kst, signal

aapl['kst'], aapl['signal_line'] = get_kst(aapl['close'], 10, 10, 10, 15, 10, 15, 20, 30, 9)
aapl = aapl[aapl.index >= '2020-01-01']
aapl.tail()

# KST INDICATOR PLOT

ax1 = plt.subplot2grid((11,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((11,1), (6,0), rowspan = 5, colspan = 1)
ax1.plot(aapl['close'], linewidth = 2.5)
ax1.set_title('PLTR CLOSING PRICES')
ax2.plot(aapl['kst'], linewidth = 2, label = 'KST', color = 'orange')
ax2.plot(aapl['signal_line'], linewidth = 2, label = 'SIGNAL', color = 'mediumorchid')
ax2.legend()
ax2.set_title('PLTR KST')
plt.show()

# KST INDICATOR PLOT

ax1 = plt.subplot2grid((11,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((11,1), (6,0), rowspan = 5, colspan = 1)
ax1.plot(aapl['close'], linewidth = 2.5)
ax1.set_title('PLTR CLOSING PRICES')
ax2.plot(aapl['kst'], linewidth = 2, label = 'KST', color = 'orange')
ax2.plot(aapl['signal_line'], linewidth = 2, label = 'SIGNAL', color = 'mediumorchid')
ax2.legend()
ax2.set_title('PLTR KST')
plt.show()

# KST CROSSOVER TRADING STRATEGY

def implement_kst_strategy(prices, kst_line, signal_line):
    buy_price = []
    sell_price = []
    kst_signal = []
    signal = 0
    
    for i in range(len(kst_line)):
        
        if kst_line[i-1] < signal_line[i-1] and kst_line[i] > signal_line[i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                kst_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                kst_signal.append(0)
                
        elif kst_line[i-1] > signal_line[i-1] and kst_line[i] < signal_line[i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                kst_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                kst_signal.append(0)
                
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            kst_signal.append(0)
            
    return buy_price, sell_price, kst_signal

buy_price, sell_price, kst_signal = implement_kst_strategy(aapl['close'], aapl['kst'], aapl['signal_line'])

# TRADING SIGNALS PLOT

ax1 = plt.subplot2grid((11,1), (0,0), rowspan = 5, colspan = 1)
ax2 = plt.subplot2grid((11,1), (6,0), rowspan = 5, colspan = 1)
ax1.plot(aapl['close'], linewidth = 2, label = 'aapl')
ax1.plot(aapl.index, buy_price, marker = '^', markersize = 12, linewidth = 0, color = 'green', label = 'BUY SIGNAL')
ax1.plot(aapl.index, sell_price, marker = 'v', markersize = 12, linewidth = 0, color = 'r', label = 'SELL SIGNAL')
ax1.legend()
ax1.set_title('PLTR KST TRADING SIGNALS')
ax2.plot(aapl['kst'], linewidth = 2, label = 'KST', color = 'orange')
ax2.plot(aapl['signal_line'], linewidth = 2, label = 'SIGNAL', color = 'mediumorchid')
ax2.legend()
ax2.set_title('PLTR KST')
plt.show()

#BTC-USD Support/Resistance Trading in Matplotlib

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import pandas as pd
from datetime import datetime as dt
import yfinance as yf
import nsepy
from statistics import mean

benchmark_ = ["BTC-USD"]

start_date_ = "2024-01-01"
end_date_  = "2024-06-10"

df = yf.download(benchmark_, start=start_date_, end=end_date_)
df.tail()

def find_levels(data, window):
    high = data['High'].rolling(window=window).max()
    low = data['Low'].rolling(window=window).min()
    midpoint = (high + low) / 2
    diff = high - low
    resistance = midpoint + (diff / 2)
    support = midpoint - (diff / 2)
    return support, resistance

# Download historical stock prices

data = df.copy()

window = 30

# Calculate support and resistance levels
support, resistance = find_levels(data, window)

# Plot the stock price, support, and resistance lines
fig, ax = plt.subplots(figsize=(12, 6))
ax.plot(data.index, data['Close'], label='Stock Price')
ax.plot(data.index, support, label='Support', linestyle='--', color='green')
ax.plot(data.index, resistance, label='Resistance', linestyle='--', color='red')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.set_title(f'{symbol} Stock Price with Support and Resistance Levels')
ax.legend()

# Add annotations for last support and resistance levels
last_support = support.iloc[-1]
last_resistance = resistance.iloc[-1]
ax.annotate(f'Support: {last_support:.2f}', xy=(support.index[-1], last_support),
            xytext=(support.index[-1] - pd.DateOffset(days=30), last_support + 10),
            arrowprops=dict(facecolor='green', arrowstyle='->'))
ax.annotate(f'Resistance: {last_resistance:.2f}', xy=(resistance.index[-1], last_resistance),
            xytext=(resistance.index[-1] - pd.DateOffset(days=30), last_resistance - 10),
            arrowprops=dict(facecolor='red', arrowstyle='->'))
plt.grid()
plt.show()

stock_data = df.copy()

# Define the lookback period for calculating high and low prices
lookback_period = 15

# Calculate the high and low prices over the lookback period
high_prices = stock_data["High"].rolling(window=lookback_period).max()
low_prices = stock_data["Low"].rolling(window=lookback_period).min()

# Calculate the price difference and Fibonacci levels
price_diff = high_prices - low_prices
levels = np.array([0, 0.236, 0.382, 0.5, 0.618, 0.786, 1])
fib_levels = low_prices.values.reshape(-1, 1) + price_diff.values.reshape(-1, 1) * levels

# Get the last price for each Fibonacci level
last_prices = fib_levels[-1, :]

# Define a color palette for the Fibonacci levels
colors = ['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet']

# Plot the stock price with the Fibonacci retracement levels and last prices
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(stock_data.index, stock_data["Close"], label="Stock Price")

offsets = [-16, -14, -12, -10, 8, 10, 12] 

for i, level in enumerate(levels):
    if level == 0 or level == 1:
        linestyle = "--"
    else:
        linestyle = "-"
    ax.plot(stock_data.index, fib_levels[:, i], label=f"Fib {level:.3f}", linestyle=linestyle, color=colors[i])
    ax.annotate(f"{last_prices[i]:.2f}", 
                xy=(stock_data.index[-1], fib_levels[-1, i]), 
                xytext=(stock_data.index[-1] + pd.Timedelta(days=5), fib_levels[-1, i] + offsets[i]), 
                ha="left", va="center", fontsize=16, color=colors[i])

ax.set_xlabel("Date")
ax.set_ylabel("Price")
ax.set_title(f"{symbol} with Fibonacci Retracement Levels")
ax.legend(loc="lower right", fontsize=14)
plt.grid()
plt.show()

#Backtesting IBM Mean Reversion Strategy

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from backtesting import Backtest, Strategy
from backtesting.lib import crossover

df = yf.download('IBM', start='2015-01-01', end='2023-11-14')

class MeanReversion(Strategy):
    n1 = 30  # Period for the moving average
    
    def init(self):
        # Compute moving average
        self.offset = 0.01  # Buy/sell when price is 1% below/above the moving average
        prices = self.data['Close']
        self.ma = self.I(self.compute_rolling_mean, prices, self.n1)

    def compute_rolling_mean(self, prices, window):
        return [(sum(prices[max(0, i - window):i]) / min(i, window)) if i > 0 else np.nan for i in range(len(prices))]

    def next(self):
        size = 0.1
        # If price drops to more than offset% below n1-day moving average, buy
        if self.data['Close'] < self.ma[-1] * (1 - self.offset):
            if self.position.size < 0:  # Check for existing short position
                self.buy()  # Close short position
            self.buy(size=size)

        # If price rises to more than offset% above n1-day moving average, sell
        elif self.data['Close'] > self.ma[-1] * (1 + self.offset):
            if self.position.size > 0:  # Check for existing long position
                self.sell()  # Close long position
            self.sell(size=size)

bt = Backtest(df, MeanReversion, cash=100000, commission=.002)
stats = bt.run()
bt.plot()

#Hierarchical Clustering of Stocks

import numpy as np
import pandas as pd
import yfinance as yf
from fastdtw import fastdtw
import matplotlib.pyplot as plt
from scipy.spatial.distance import euclidean
from scipy.cluster.hierarchy import dendrogram, linkage

stocks = [
    'AAPL',  # Apple
    'JNJ',   # Johnson & Johnson
    'XOM',   # Exxon Mobil
    'HSBC',  # HSBC
    'BABA',  # Alibaba
    'TSLA',  # Tesla
    'KO',    # Coca-Cola
    'SAP',   # SAP
    'NVDA',  # NVIDIA
    'WMT'    # Walmart
]

start_date = '2023-01-01'
end_date = '2024-05-28'

closing_prices = pd.DataFrame()

for stock in stocks:
    ticker = yf.Ticker(stock)
    hist = ticker.history(start=start_date, end=end_date)
    closing_prices[stock] = hist['Close']

normalized_data = closing_prices / closing_prices.iloc[0]
normalized_data.dropna(axis=1, inplace=True)

normalized_data.plot()

def euclidean(x, y):
    return np.sqrt(np.sum((x - y) ** 2))

dtw_distances = np.zeros((len(normalized_data.columns), len(normalized_data.columns)))

for i, stock_i in enumerate(normalized_data.columns):
    for j, stock_j in enumerate(normalized_data.columns):
        if i < j:
            series_i = normalized_data[stock_i].values.flatten()
            series_j = normalized_data[stock_j].values.flatten()
            distance, path = fastdtw(series_i, series_j, dist=euclidean)
            dtw_distances[i, j] = distance
            dtw_distances[j, i] = distance

Z = linkage(dtw_distances, 'ward')

plt.figure(figsize=(10, 6))
dendrogram(Z, labels=normalized_data.columns, leaf_rotation=45., leaf_font_size=12.,
                    above_threshold_color='#1500fc', color_threshold=0.3 * max(Z[:, 2]),  
                    )
plt.title('Hierarchical Clustering of Stocks with DTW')
plt.xlabel('Stock')
plt.ylabel('Distance')
plt.tight_layout()
plt.show()

#NVDA Volatility & Options Trading in Plotly

mport pandas as pd
import numpy as np

# Yfinance to retrieve financial data 
import yfinance as yf

# Plotly for Data Visualization
import plotly.express as px
import plotly.graph_objs as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.io as pio
from IPython.display import display
from plotly.offline import init_notebook_mode
init_notebook_mode(connected=True)

df = yf.download('NVDA',start="2023-01-01")
df.info()
df.tail()

# Defining function 
def get_ticker(ticker):

    """
    This function takes in a ticker from Yahoo Finance as argument. 
    It then computed the returns based on the adjusted closing prices and uses it to compute the annualized volatility.
    The annualized volatility is used to create an indicator called volatility rank, in which we categorize the annualized volatility into values from 1 to 10.
    """

    # Downloading historical data
    df = yf.download(ticker,start="2023-01-01")

    # Computing returns
    df['Returns'] = df[('Close', ticker)].pct_change()

    # Computing annualized volatility
    df['Vol'] = df['Returns'].rolling(20).std() * np.sqrt(252)
    df.dropna(axis = 0, inplace = True) # Removing null values

    # Generating array of equally-spaced points representing the quantiles to be calculated (from 0% to 100%)
    quantiles = np.quantile(df['Vol'], np.linspace(0,1,11))

    # Using quantilies to categorize and label the annualized volatility values
    quantile_labels = pd.cut(df['Vol'], bins = quantiles, 
                             labels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    
    # Adding categorical labels to the dataframe
    df['Vol_Rank'] = quantile_labels

    # Plotting data
    fig = make_subplots(rows = 3, cols = 1, horizontal_spacing=0.2, row_heights=[.60, .20, .20], shared_xaxes=True)

    # First row --> Closing Price
    fig.add_trace(go.Scatter(
        x = df.index, y = df[('Close', ticker)], name = 'Closing Price'
    ), row = 1, col = 1)

    # Second row --> Annualized Volatility
    fig.add_trace(go.Scatter(
        x = df.index, y = df['Vol'], name = 'Annualized Volatility'
    ), row = 2, col = 1)

    # Third row --> Volatility rank
    fig.add_trace(go.Scatter(
        x = df.index, y = df['Vol_Rank'], name = 'Volatility Rank'
    ), row = 3, col = 1)

    # Defining subplots layout
    fig.update_layout(title = {'text': f'<b>{ticker} Closing Price & Volatility</b>'},
                      template = 'plotly_white',
                      height = 900, width = 950,
                      showlegend=False,
                      hovermode='x unified')
    
    # Defining layout of y-axes across subplots
    fig.update_yaxes(title_text = 'Closing Price ($)', row = 1)
    fig.update_yaxes(title_text = 'Annualized Volatility', row = 2)
    fig.update_yaxes(title_text = 'Volatility Rank', row = 3)

    fig.show() # Displaying plot

get_ticker('NVDA')

def get_strategy(ticker, strike_call, strike_put, premium_call, premium_put):

    """
    This function is used to visualize the payoffs of long and short straddle strategies of options trading.

    Params:
    ticker: Symbol of the underlying asset.
    strike_call: Strike price of the call option.
    strike_put: Strike price of the put option.
    premium_call: Premium of the call option.
    premium_put: Premium of the put option.
    """

    # Generating an array of possible prices the underlying asset might fall into
    stock_prices = np.linspace(0.79 * min(strike_put, strike_call), 1.19 * max(strike_put, strike_call), 100).round(2)

    # Computing payoffs
    # Payoffs for holding long call and put options 
    long_call_payoff = np.maximum(stock_prices - strike_call, 0) - premium_call
    long_put_payoff = np.maximum(strike_put - stock_prices, 0) - premium_put

    # Payoffs for holding short positions in call and put options
    short_call_payoff = -long_call_payoff
    short_put_payoff = -long_put_payoff

    # Combined payoffs for both long and short positions
    combined_long_payoff = long_call_payoff + long_put_payoff
    combined_short_payoff = short_call_payoff + short_put_payoff

    # Computing profit and loss for long straddle
    profit_long = np.maximum(combined_long_payoff, 0)
    loss_long = np.minimum(combined_long_payoff, 0)

    # Computing profit and loss for short straddle
    loss_short = np.minimum(combined_short_payoff, 0)
    profit_short = np.maximum(combined_short_payoff, 0)
    
    # Creating subplots
    fig = make_subplots(
        rows=2, cols=1,
        horizontal_spacing=0.2,
        row_heights=[0.5, 0.5],
        shared_xaxes=False,
        shared_yaxes=False
    )

    # Adding Long Straddle traces
    fig.add_trace(
        go.Scatter(x=stock_prices, y=long_call_payoff, mode='lines', line=dict(color='grey', dash='dash'), name='Long Call', hovertemplate='%{y:.2f}'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=stock_prices, y=long_put_payoff, mode='lines', line=dict(color='grey', dash='dash'),  name='Long Put', hovertemplate='%{y:.2f}'),
        row=1, col=1
    )

    # Adding Short Straddle traces
    fig.add_trace(
        go.Scatter(x=stock_prices, y=short_call_payoff, mode='lines', line=dict(color='grey', dash='dash'),  name='Short Call', hovertemplate='%{y:.2f}'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=stock_prices, y=short_put_payoff, mode='lines', line=dict(color='grey', dash='dash'), name='Short Put', hovertemplate='%{y:.2f}'),
        row=2, col=1
    )

    # Adding the payoff lines for Long Straddle
    fig.add_trace(
        go.Scatter(x=stock_prices, y=profit_long, mode='lines', line=dict(color='black', dash='solid'), name='Profit', hovertemplate='%{y:.2f}',
                    fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.5)'),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=stock_prices, y=loss_long, mode='lines', line=dict(color='black', dash='solid'), name='Loss', hovertemplate='%{y:.2f}',
                    fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.5)'),
        row=1, col=1
    )

    # Adding the payoff lines for Long Straddle
    fig.add_trace(
        go.Scatter(x=stock_prices, y=loss_short, mode='lines', line=dict(color='black', dash='solid'), name = 'Loss', hovertemplate='%{y:.2f}',
                   fill='tozeroy', fillcolor='rgba(255, 0, 0, 0.5)'),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=stock_prices, y=profit_short, mode='lines', line=dict(color='black', dash='solid'), name = 'Profit', hovertemplate='%{y:.2f}',
                   fill='tozeroy', fillcolor='rgba(0, 255, 0, 0.5)'),
        row=2, col=1
    )

    
    # Defining layout
    fig.update_layout(
        title={'text': f'<b>{ticker} Long & Short Straddle</b>'},
        template='plotly_white',
        height=1000, width=750,
        showlegend=False,
        hovermode='x unified')

    # Defining y-axes and x-axes tiles across rows
    fig.update_yaxes(title_text='Long Payoff ($)', row=1)
    fig.update_yaxes(title_text='Short Payoff ($)', row=2)
    fig.update_xaxes(title_text = 'Underlying Asset Price at Expiration', row=1)
    fig.update_xaxes(title_text = 'Underlying Asset Price at Expiration', row=2)

    fig.show() # Displaying plot

get_strategy('NVDA', 950, 950, 9.5, 9.5)

#Portfolio Optimization in Matplotlib

RISK_FREE_RATE = 0.05
MAX_PORTS = 10000
MAX_WEIGHT = 1.05


def port_generator(rets, cov_matrix):
    port_rets = []
    port_risks = []
    port_sharpes = []
    port_weights = []

    for _ in range(MAX_PORTS):
        # weights = np.random.random(len(rets))
        weights = np.random.uniform(-MAX_WEIGHT, MAX_WEIGHT, len(rets))
        weights /= np.sum(weights)  # Normalize weights to 1
        if any(weights > MAX_WEIGHT):
            continue
        port_weights.append(weights)

        port_ret = np.dot(weights, rets)
        port_rets.append(port_ret)

        port_risk = np.sqrt(weights.T @ cov_matrix @ weights)
        port_risks.append(port_risk)

        port_sharpe = (port_ret - RISK_FREE_RATE) / port_risk
        port_sharpes.append(port_sharpe)

    port_rets = np.array(port_rets)
    port_risks = np.array(port_risks)

    plt.scatter(
        port_risks * 100.0,
        port_rets * 100.0,
        c=port_sharpes,
        cmap="viridis",
        alpha=0.75,
    )

    plt.xlabel("Risk (%)")
    plt.ylabel("Expected Returns (%)")
    plt.colorbar(label="Sharpe Ratio")
    plt.grid()

    return port_risks, port_rets, port_sharpes


plt.figure(figsize=(16, 8))
plt.title("Random Portfolios")
port_generator(rets, cov_matrix)
plt.show()

tickers = [
    "AAPL",
    "TSLA",
    "MO",
    "AMZN",
    "META",
]
START_DATE = "2021-01-01"
END_DATE = "2023-12-15"

tickers_orig_df = load_ticker_prices_ts_df(tickers, START_DATE, END_DATE)
tickers_df = tickers_orig_df.dropna(axis=1).pct_change().dropna()  # first % is NaN

rets = ((1 + tickers_df).prod() ** (TRADING_DAYS_IN_YEAR / len(tickers_df))) - 1
cov_matrix = tickers_df.cov() * TRADING_DAYS_IN_YEAR

plt.figure(figsize=(16, 8))
plt.title("Random Portfolios")
port_risks, port_rets, port_sharpes = port_generator(rets, cov_matrix)
plt.show()

# Equally weighted portfolio 
equal_weights = np.ones(len(rets))

rets = ((1 + tickers_df).prod() ** (TRADING_DAYS_IN_YEAR / len(tickers_df))) - 1
cov_matrix = tickers_df.cov() * TRADING_DAYS_IN_YEAR

# Min variance weights
inv_cov_matrix = np.linalg.pinv(cov_matrix)
min_risk_vect = equal_weights @ inv_cov_matrix
expect_ret_vect = inv_cov_matrix @ rets

# Minimum variance portfolio
# Weights are normalized to sum to 1, and risk to std deviation.
mvp_weights = min_risk_vect / np.sum(min_risk_vect)
mvp_ret = mvp_weights @ rets
mvp_risk = np.sqrt(mvp_weights.T @ cov_matrix @ mvp_weights)

# Tangency portfolio
tan_weights = expect_ret_vect / np.sum(expect_ret_vect)
tan_ret = tan_weights @ rets
tan_risk = np.sqrt(tan_weights.T @ cov_matrix @ tan_weights)

summary_data = {
    "Asset": tickers,
    "MVP Weights": mvp_weights,
    "TAN Weights": tan_weights,
}

print(f"mvp_ret: {mvp_ret*100:0.02f}%, mvp_risk {mvp_risk*100:0.02f}%")
print(f"tan_ret: {tan_ret*100:0.02f}%, tan_risk {tan_risk*100:0.02f}%")

summary_df = pd.DataFrame(summary_data)
summary_df.T

MAX_RETS = 0.51
TEN_BASIS_POINTS = 0.0001 * 10

c = np.sum(equal_weights * min_risk_vect)  # Constant term
b = np.sum(rets * min_risk_vect)  # Linear term
a = np.sum(rets * expect_ret_vect)  # Quadratic term
utility_func = (a * c) + (-(b**2))  # U(X) to penalize risk

# The frontier curve & MCL, scaled by utility function
exp_rets = np.arange(0, MAX_RETS, TEN_BASIS_POINTS)
ports_risk_frontier = np.sqrt(
    ((c * (exp_rets**2)) - (2 * b * exp_rets) + a) / utility_func
)
mcl_vector = exp_rets * (1 / np.sqrt(a))

plt.figure(figsize=(12, 6))
plt.plot(
    ports_risk_frontier,
    exp_rets,
    linestyle="--",
    color="blue",
    label="Efficient Frontier",
    linewidth=4,
    alpha=0.6,
)
plt.plot(
    mcl_vector,
    exp_rets,
    label="MCL",
    linewidth=4,
    alpha=0.6,
    color="black",
)

plt.scatter(mvp_risk, mvp_ret, color="green", label="MVP")
plt.annotate(
    f"MVP\nRisk: {mvp_risk*100:.2f}%\nReturn: {mvp_ret*100:.2f}%",
    (mvp_risk, mvp_ret),
    textcoords="offset points",
    xytext=(-30, 10),
)
plt.scatter(tan_risk, tan_ret, color="red", label="TAN")
plt.annotate(
    f"Tangency\nRisk: {tan_risk*100:.2f}%\nReturn: {tan_ret*100:.2f}%",
    (tan_risk, tan_ret),
    textcoords="offset points",
    xytext=(10, 10),
)

plt.legend(loc="upper left", fontsize=16)
plt.xlabel("Risk %")
plt.ylabel("Returns %")
plt.tight_layout()
plt.show()

TARGET_RET = 0.2

pt_port = None
opt_risk = None
opt_ret = None

mvp_weights = (a - (b * TARGET_RET)) / utility_func
tan_weights = ((c * TARGET_RET) - b) / utility_func

opt_port_weights = (mvp_weights * min_risk_vect) + (tan_weights * expect_ret_vect)
opt_ret = np.sum(opt_port_weights * rets)
opt_risk = np.sqrt(((c * (opt_ret**2)) - (2 * b * opt_ret) + a) / utility_func)

plt.figure(figsize=(12, 6))
plt.plot(
    ports_risk_frontier,
    exp_rets,
    linestyle="--",
    color="blue",
    label="Frontier",
    linewidth=4,
    alpha=0.6,
)

plt.scatter(opt_risk, opt_ret, color="green", label="Min Variance",s=)
plt.annotate(
    f"Optimal \nRisk: {opt_risk*100:.2f}%\nReturn: {opt_ret*100:.2f}%",
    (opt_risk, opt_ret),
    textcoords="offset points",
    xytext=(-30, 10),
)

plt.legend(loc="upper left", fontsize=16)
plt.xlabel("Risk %")
plt.ylabel("Returns %")
plt.tight_layout()
plt.show()

# Add portfolios sharpe
opt_sharpe = (opt_ret - RISK_FREE_RATE) / opt_risk
mvp_sharpe = (mvp_ret - RISK_FREE_RATE) / mvp_risk
tan_sharpe = (tan_ret - RISK_FREE_RATE) / tan_risk

plt.figure(figsize=(16, 12))  # Increase figure size

plt.title("Investible Universe")

plt.scatter(
    port_risks * 100.0,
    port_rets * 100.0,
    c=port_sharpes,
    cmap="viridis",
    alpha=0.75,
    s=80,  # Adjust the size of the scatter points
)

plt.plot(
    ports_risk_frontier * 100,
    exp_rets * 100,
    linestyle="--",
    color="blue",
    label="Frontier",
    linewidth=4,
    alpha=0.6,
)

# Adjust the size of the optimal point
plt.scatter(
    opt_risk * 100,
    opt_ret * 100,
    color="green",
    marker="x",
    s=200,
    label="Optimal Expected Returns",
)
plt.annotate(
    f"Optimal Exp \nRisk: {opt_risk*100:.2f}%\nReturn: {opt_ret*100:.2f}%\nSharpe: {opt_sharpe:.2f}",
    (opt_risk * 100, opt_ret * 100),
    textcoords="offset points",
    xytext=(-90, 10),  # Adjust the annotation position
    fontsize=14,  # Adjust the font size
)

plt.plot(
    mcl_vector * 100,
    exp_rets * 100,
    label="MCL",
    linewidth=2,
    alpha=0.6,
    color="black",
)

# Adjust the size and position of the MVP point
plt.scatter(
    mvp_risk * 100,
    mvp_ret * 100,
    color="Black",
    label="MVP",
    marker="x",
    s=150,
)
plt.annotate(
    f"MVP\nRisk: {mvp_risk*100:.2f}%\nReturn: {mvp_ret*100:.2f}%\nSharpe: {mvp_sharpe:.2f}",
    (mvp_risk * 100, mvp_ret * 100),
    textcoords="offset points",
    xytext=(-30, 20),
    fontsize=14,
)

# Adjust the size and position of the Tangency point
plt.scatter(
    tan_risk * 100,
    tan_ret * 100,
    color="red",
    label="TAN",
    marker="x",
    s=200,
)
plt.annotate(
    f"Tangency\nRisk: {tan_risk*100:.2f}%\nReturn: {tan_ret*100:.2f}%\nSharpe: {tan_sharpe:.2f}",
    (tan_risk * 100, tan_ret * 100),
    textcoords="offset points",
    xytext=(-50, 20),
    fontsize=14,
)

plt.xlabel("Risk (%)")
plt.ylabel("Expected Returns (%)")
plt.colorbar(label="Sharpe Ratio")
plt.grid()

plt.tight_layout()
plt.show()

#Webscraping of Headlines & NLP Sentiment Analysis

import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests


tickers_list = ['XOM']

news = pd.DataFrame()

for ticker in tickers_list:
   url = f'https://finviz.com/quote.ashx?t={ticker}&p=d'
   ret = requests.get(
       url,
       headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'},
   )
   
   html = BeautifulSoup(ret.content, "html.parser")
   
   try:
     df = pd.read_html(
         str(html),
         attrs={'class': 'fullview-news-outer'}
     )[0]
   except:
     print(f"{ticker} No news found")
     continue
 
   df.columns = ['Date', 'Headline']

df.tail()

# Process date and time columns to make sure this is filled in every headline each row
dateNTime = df.Date.apply(lambda x: ','+x if len(x)<8 else x).str.split(r' |,', expand = True).replace("", None).ffill()

df = pd.merge(df, dateNTime, right_index=True, left_index=True).drop('Date', axis=1).rename(columns={0:'Date', 1:'Time'})

df = df[df["Headline"].str.contains("Loading.") == False].loc[:, ['Date', 'Time', 'Headline']]

df["Ticker"] = ticker
news = pd.concat([news, df], ignore_index = True)

nltk.download('vader_lexicon')
vader = SentimentIntensityAnalyzer()

scored_news = news.join(
  pd.DataFrame(news['Headline'].apply(vader.polarity_scores).tolist())
)

news.head()

news_score = scored_news.loc[:, ['Ticker', 'Date', 'compound']]


print(news_score)

plt.hist(news_score['compound'])
plt.title('Compound Sentiment Score for XOM')
plt.grid()

news_score = scored_news.loc[:, ['Ticker', 'Date', 'compound']].pivot_table(values='compound', index='Date', columns='Ticker', aggfunc='mean').ewm(15).mean()
news_score.plot(figsize=(14, 6),kind='line',linewidth=4,legend=True, fontsize=14)
plt.title("Sentiment Score for XOM",fontsize=14)
plt.grid()

news_score.pct_change().dropna().plot(figsize=(14, 6),linewidth=4,kind='line',legend=True, fontsize=14)
plt.title("Percentage Change of Sentiment Score for XOM",fontsize=14)
plt.grid()

#BTC-USD Renko Charts

import requests
import numpy as np
import matplotlib.pyplot as plt
from math import floor
from termcolor import colored as cl

plt.rcParams['figure.figsize'] = (12, 6)
plt.style.use('fivethirtyeight')

import pandas as pd
import yfinance as yf
import datetime
from datetime import date, timedelta
today = date.today()

d1 = today.strftime("%Y-%m-%d")
end_date = d1
d2 = date.today() - timedelta(days=730)
d2 = d2.strftime("%Y-%m-%d")
start_date = d2

data = yf.download('BTC-USD', 
                      start=start_date, 
                      end=end_date, 
                      progress=False)
data["Date"] = data.index
data = data[["Date", "Open", "High", "Low", "Close", "Adj Close", "Volume"]]
data.reset_index(drop=True, inplace=True)
data.tail()

plt.plot(data['Date'],data['Close'])
plt.xlabel('Date')
plt.ylabel('Close Price USD')
plt.title('BTC-USD Close Price')

# number of bars to display in the plot
import matplotlib 
import matplotlib.pyplot as plt 
num_bars = 200
df=data.copy()
# get the last num_bars
df = df.tail(num_bars)
renkos = zip(df['Open'],df['Close'])
 
# compute the price movement in the Renko
price_move = abs(df.iloc[1]['Open'] - df.iloc[1]['Close'])
 
# create the figure
fig = plt.figure(1)
fig.clf()
axes = fig.gca()
 
# plot the bars, blue for 'up', red for 'down'
index = 1
for open_price, close_price in renkos:
    if (open_price < close_price):
        renko = matplotlib.patches.Rectangle((index,open_price), 1, close_price-open_price, edgecolor='darkblue', facecolor='blue', alpha=0.5)
        axes.add_patch(renko)
    else:
        renko = matplotlib.patches.Rectangle((index,open_price), 1, close_price-open_price, edgecolor='darkred', facecolor='red', alpha=0.5)
        axes.add_patch(renko)
        index = index + 1
 
# adjust the axes
plt.xlim([0, num_bars])
plt.ylim([min(min(df['Open']),min(df['Close'])), max(max(df['Open']),max(df['Close']))])
fig.suptitle('Bars from ' + min(df['Date']).strftime("%d-%b-%Y %H:%M") + " to " + max(df['Date']).strftime("%d-%b-%Y %H:%M") \
        + '\nPrice movement = ' + str(price_move), fontsize=14)
plt.xlabel('Bar Number')
plt.xlim([0, 100])
plt.ylabel('Price')

plt.show()

import datetime as dt
import yfinance as yf
import pandas as pd
import mplfinance as fplt
start_date = dt.datetime.today()- dt.timedelta(730) # getting data of around 5 years.
end_date = dt.datetime.today()
ticker_name = "BTC-USD"
ohlcv = yf.download(ticker_name, start_date, end_date)

# Function to calculate average true range
def ATR(DF, n):
  df = DF.copy() # making copy of the original dataframe
  df['H-L'] = abs(df['High'] - df['Low']) 
  df['H-PC'] = abs(df['High'] - df['Adj Close'].shift(1))# high -previous close
  df['L-PC'] = abs(df['Low'] - df['Adj Close'].shift(1)) #low - previous close
  df['TR'] = df[['H-L','H-PC','L-PC']].max(axis =1, skipna = False) # True range
  df['ATR'] = df['TR'].rolling(n).mean() # average –true range
  df = df.drop(['H-L','H-PC','L-PC'], axis =1) # dropping the unneccesary columns
  df.dropna(inplace = True) # droping null items
  return df

bricks = round(ATR(ohlcv,50)["ATR"][-1],0)

fplt.plot(ohlcv,type='renko',renko_params=dict(brick_size=bricks, atr_length=14),
          style='yahoo',figsize =(18,7),
          title = "RENKO CHART WITH ATR {0}".format('BTC-USD'))

#EUR/USD FBProphet Forecasting

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)
import prophet as pr
import plotly.express as px
import requests
import numpy as np
import matplotlib.pyplot as plt
from math import floor
from termcolor import colored as cl

plt.rcParams['figure.figsize'] = (10, 6)
plt.style.use('fivethirtyeight')

import warnings
warnings.filterwarnings("ignore")

df = pd.read_csv('EURUSD_Daily_2006_2023.csv')

df.tail()

px.area(df, x='DATE', y='CLOSE')

px.box(df, y='CLOSE')

### Boxcox transformation
from statsmodels.base.transform import BoxCox

bc= BoxCox()
df["Close"], lmbda =bc.transform_boxcox(df["CLOSE"])

## Making data Prophet consistent
data= df[["DATE", "Close"]]
data.columns=["ds", "y"]

## Creating model parameters
model_param ={
    "daily_seasonality": False,
    "weekly_seasonality":False,
    "yearly_seasonality":True,
    "seasonality_mode": "multiplicative",
    "growth": "logistic"
}

from prophet import Prophet

model = Prophet(**model_param)
data['cap']= data["y"].max() + data["y"].std() * 0.05 
# Setting a cap or upper limit for the forecast as we are using logistics growth
# The cap will be maximum value of target variable plus 5% of std.

model.fit(data)

# Create future dataframe
future= model.make_future_dataframe(periods=365)
#future= model.make_future_dataframe(periods=60)
future['cap'] = data['cap'].max()

forecast= model.predict(future)

model.plot_components(forecast);

model.plot(forecast);

fig = plot_cross_validation_metric(df_cv, metric='rmse')

#Classification of Market Regimes Using STD
# Importing Libraries

# Data Handling
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Financial Data Analysis
import yfinance as yf

# Data Visualization
import plotly.express as px
import plotly.graph_objs as go
import plotly.subplots as sp
from plotly.subplots import make_subplots
import plotly.figure_factory as ff
import plotly.io as pio
from IPython.display import display
from plotly.offline import init_notebook_mode

# Statistics & Mathematics
import scipy.stats as stats
import statsmodels as sm
from scipy.stats import shapiro, skew
import math

# Hiding warnings 
import warnings
warnings.filterwarnings("ignore")

def load_and_preprocess(ticker):
    '''
    This function takes in a ticker symbol, which is used to 
    retrieve historical data from Yahoo Finance.
    The attributes 'Returns', and the Adjusted Low, High, and Open 
    are created.
    NaNs are filled with 0s
    '''
    
    df = yf.download(ticker)
    df['Returns'] = df[('Close',ticker)].pct_change(1)
    df['Low'] = df[('Low',ticker)] 
    df['High'] = df[('High',ticker)] 
    df['Open'] = df[('Open',ticker)] 
    df = df.fillna(0)
    return df

ticker = 'XOM'

df = load_and_preprocess(ticker) # Loading and Transforming Dataframe
df.tail()

        #log price
df['price'] = df['Close'].apply(np.log)

     #price difference
df['price_diff'] = df['price'].diff()   

        #std dev
df['std_dev'] = df['price_diff'].rolling(window=100).std()
        #use rolling mean to find 'zones' of volatility
df['std_dev_ma'] = df['std_dev'].rolling(3000).mean()
        #thresholds between levels
std_dev_ma_threshold_1 = df['std_dev_ma'].quantile(0.2)
std_dev_ma_threshold_2 = df['std_dev_ma'].quantile(0.4)
std_dev_ma_threshold_3 = df['std_dev_ma'].quantile(0.6)
std_dev_ma_threshold_4 = df['std_dev_ma'].quantile(0.8)
        # Initialize 'signal' column with zeros
df['levels'] = 0
        #assign levels based on average std dev  
df.loc[(df['std_dev_ma'] > std_dev_ma_threshold_1), 'levels'] = 1
df.loc[(df['std_dev_ma'] > std_dev_ma_threshold_2), 'levels'] = 2
df.loc[(df['std_dev_ma'] > std_dev_ma_threshold_3), 'levels'] = 3
df.loc[(df['std_dev_ma'] > std_dev_ma_threshold_4), 'levels'] = 4

def plot_levels(df):
        fig, ax = plt.subplots(figsize=(12, 6), dpi=80)
        colors = {
            0:'grey',
            1:'green',
            2: 'blue',
            3: 'red',
            4: 'black'
        }
        scatter = ax.scatter(
            np.reshape(df.index, -1),
            np.reshape(df['price'], -1),
            c=np.reshape(df['levels'].apply(lambda x: colors[x]), -1),
            s=10,
            linewidths=1            
        )
        # Create proxy artists for legend
        legend_labels = [f'Level {level}' for level in colors.keys()]
        legend_handles = [mpatches.Patch(color=colors[level], label=label) for level, label in enumerate(legend_labels)]

        # Create a legend
        ax.legend(handles=legend_handles, title='Levels')

        plt.title('XOM std levels')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.grid(True)
        plt.show()

#Market Regime Analysis

import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

class MarketRegimeAnalyzer:
    def __init__(self, start_date=None, end_date=None):
        """
        Initialize Market Regime Analyzer

        Args:
            start_date (str, optional): Start date for analysis. Defaults to 3 years ago.
            end_date (str, optional): End date for analysis. Defaults to today.
        """
        # Set default date range if not provided
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=3*365)).strftime('%Y-%m-%d')
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')

        self.start_date = start_date
        self.end_date = end_date

        # Tickers for analysis
        self.indices = {
            'SPX': '^GSPC',
            'VIX': '^VIX'
        }

        # Data storage
        self.data = {}

    def fetch_data(self):
        """
        Fetch historical data for specified indices

        Returns:
            MarketRegimeAnalyzer: Self with fetched data
        """
        for name, ticker in self.indices.items():
            try:
                # Download data using yfinance with explicit auto_adjust
                # Wrap single ticker in a list to avoid previous error
                df = yf.download([ticker], start=self.start_date, end=self.end_date, auto_adjust=True)

                # If DataFrame has multi-level columns, flatten them
                if isinstance(df.columns, pd.MultiIndex):
                    df.columns = [f'{col[0]}_{col[1]}' for col in df.columns]

                # Ensure numeric columns for calculations
                numeric_columns = ['Open', 'High', 'Low', 'Close']
                for suffix in ['', '_Open', '_High', '_Low', '_Close']:
                    for col in [f'{suffix}' for suffix in numeric_columns]:
                        if col in df.columns:
                            df[col] = pd.to_numeric(df[col], errors='coerce')

                # Add column with ticker name
                df['Ticker'] = name
                self.data[name] = df

            except Exception as e:
                print(f"Error fetching data for {name}: {e}")
                # Verbose error tracking
                import traceback
                traceback.print_exc()

        return self

    def calculate_yang_zhang_volatility(self, ohlc_data, window=21):
        """
        Calculate Yang-Zhang volatility

        Args:
            ohlc_data (pd.DataFrame): OHLC price data
            window (int, optional): Rolling window. Defaults to 21.

        Returns:
            pd.Series: Annualized volatility
        """
        # Identify correct column names
        open_col = [col for col in ohlc_data.columns if 'Open' in col][0]
        high_col = [col for col in ohlc_data.columns if 'High' in col][0]
        low_col = [col for col in ohlc_data.columns if 'Low' in col][0]
        close_col = [col for col in ohlc_data.columns if 'Close' in col][0]

        # Ensure data integrity
        ohlc_data = ohlc_data.dropna(subset=[open_col, high_col, low_col, close_col])

        # Parameters
        k = 0.34  # Standard Yang-Zhang parameter

        # Calculate overnight returns
        overnight_returns = np.log(ohlc_data[open_col] / ohlc_data[close_col].shift(1))
        overnight_vol_sq = overnight_returns.rolling(window=window).var()

        # Open-to-close volatility
        open_close_returns = np.log(ohlc_data[close_col] / ohlc_data[open_col])
        open_close_vol_sq = open_close_returns.rolling(window=window).var()

        # Rogers-Satchell volatility
        rs_terms = (np.log(ohlc_data[high_col] / ohlc_data[open_col]) *
                    np.log(ohlc_data[high_col] / ohlc_data[close_col]) +
                    np.log(ohlc_data[low_col] / ohlc_data[open_col]) *
                    np.log(ohlc_data[low_col] / ohlc_data[close_col]))

        rs_vol_sq = rs_terms.rolling(window=window).mean()

        # Yang-Zhang volatility
        yz_vol_sq = overnight_vol_sq + k * rs_vol_sq + (1 - k) * open_close_vol_sq
        yz_vol = np.sqrt(yz_vol_sq) * np.sqrt(252)  # Annualized

        return yz_vol

    def detect_market_regime(self):
        """
        Detect market regime based on volatility and VIX metrics

        Returns:
            pd.DataFrame: Market regime score and classification
        """
        if not self.data:
            self.fetch_data()

        # Verify data was fetched
        if not self.data or 'SPX' not in self.data or 'VIX' not in self.data:
            raise ValueError("Failed to fetch market data. Please check internet connection and ticker symbols.")

        # Prepare S&P 500 and VIX data
        # Find the correct close column
        spx_close_col = [col for col in self.data['SPX'].columns if 'Close' in col][0]
        vix_close_col = [col for col in self.data['VIX'].columns if 'Close' in col][0]

        sp500 = self.data['SPX']
        vix = self.data['VIX']

        # Calculate volatility
        sp500_volatility = self.calculate_yang_zhang_volatility(sp500)

        # Calculate volatility metrics with safeguards
        sp500_vol_median = sp500_volatility.rolling(window=252).median()

        # Calculate VIX ratio
        vix_median = vix[vix_close_col].rolling(window=21).median()
        vix_ratio = vix[vix_close_col] / vix_median

        # Regime components calculation with robust handling
        def safe_normalize(series):
            """Safely normalize a series to 0-1 range"""
            min_val = series.min()
            max_val = series.max()
            range_val = max_val - min_val

            # Avoid division by zero
            if range_val == 0:
                return pd.Series(0.5, index=series.index)

            return 1 - ((series - min_val) / range_val)

        # Calculate regime score components
        vol_score = safe_normalize(sp500_volatility)

        # VIX Ratio Score
        vix_ratio_score = safe_normalize(vix_ratio)

        # Additional components
        vol_median_score = (sp500_vol_median > sp500_volatility).astype(float)
        vix_ratio_threshold_score = (vix_ratio < 1).astype(float)

        # Combine components
        regime_score = (
            0.3 * vol_score +
            0.2 * vol_median_score +
            0.3 * vix_ratio_score +
            0.2 * vix_ratio_threshold_score
        ) * 100

        # Classify regime
        def classify_regime(score):
            if pd.isna(score):
                return 'Insufficient Data'
            elif score <= 20:
                return 'Extremely Bearish'
            elif score <= 40:
                return 'Bearish'
            elif score <= 60:
                return 'Neutral'
            elif score <= 80:
                return 'Bullish'
            else:
                return 'Extremely Bullish'

        # Create DataFrame with results
        regime_df = pd.DataFrame({
            'Score': regime_score,
            'Classification': regime_score.apply(classify_regime)
        }, index=sp500.index)

        return regime_df

    def visualize_regime(self, regime_df):
        """
        Visualize market regime analysis

        Args:
            regime_df (pd.DataFrame): Market regime DataFrame
        """
        plt.figure(figsize=(12, 6))

        # Color mapping for different regimes
        color_map = {
            'Extremely Bearish': '#B21818',
            'Bearish': '#EF5350',
            'Neutral': '#9C27B0',
            'Bullish': '#2196F3',
            'Extremely Bullish': '#1565C0',
            'Insufficient Data': '#9E9E9E'
        }

        # Clean out NaN values
        regime_df_clean = regime_df.dropna()

        # Plot regime score
        plt.plot(regime_df_clean.index, regime_df_clean['Score'],
                 linewidth=2,
                 color='gray',
                 alpha=0.7,
                 label='Regime Score')

        # Scatter plot with color-coded points
        for regime in color_map:
            mask = regime_df_clean['Classification'] == regime
            subset = regime_df_clean[mask]
            if not subset.empty:
                plt.scatter(subset.index,
                            subset['Score'],
                            c=color_map[regime],
                            label=regime,
                            alpha=0.7)

        plt.title('Market Regime Analysis', fontsize=15)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Regime Score', fontsize=12)
        plt.ylim(0, 100)
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def run_analysis(self):
        """
        Run complete market regime analysis

        Returns:
            pd.DataFrame: Market regime results
        """
        regime_df = self.detect_market_regime()
        self.visualize_regime(regime_df)
        return regime_df

if __name__ == "__main__":
    # Initialize and run analysis
    analyzer = MarketRegimeAnalyzer()
    results = analyzer.run_analysis()

    # Print most recent regime details
    print("\nMost Recent Market Regime:")
    most_recent = results.dropna().tail(1)
    print(most_recent)

    # Print summary statistics
    print("\nRegime Summary Statistics:")
    summary_stats = results.groupby('Classification').describe()
    print(summary_stats)

    # Additional insights
    print("\nRegime Distribution:")
    regime_distribution = results['Classification'].value_counts(normalize=True) * 100
    print(regime_distribution)

#SciKit-Learn Stock Cluster Analysis

import sys

import numpy as np
import pandas as pd

symbol_dict = {
    "TOT": "Total",
    "XOM": "Exxon",
    "CVX": "Chevron",
    "COP": "ConocoPhillips",
    "VLO": "Valero Energy",
    "MSFT": "Microsoft",
    "IBM": "IBM",
    "TWX": "Time Warner",
    "CMCSA": "Comcast",
    "CVC": "Cablevision",
    "YHOO": "Yahoo",
    "DELL": "Dell",
    "HPQ": "HP",
    "AMZN": "Amazon",
    "TM": "Toyota",
    "CAJ": "Canon",
    "SNE": "Sony",
    "F": "Ford",
    "HMC": "Honda",
    "NAV": "Navistar",
    "NOC": "Northrop Grumman",
    "BA": "Boeing",
    "KO": "Coca Cola",
    "MMM": "3M",
    "MCD": "McDonald's",
    "PEP": "Pepsi",
    "K": "Kellogg",
    "UN": "Unilever",
    "MAR": "Marriott",
    "PG": "Procter Gamble",
    "CL": "Colgate-Palmolive",
    "GE": "General Electrics",
    "WFC": "Wells Fargo",
    "JPM": "JPMorgan Chase",
    "AIG": "AIG",
    "AXP": "American express",
    "BAC": "Bank of America",
    "GS": "Goldman Sachs",
    "AAPL": "Apple",
    "SAP": "SAP",
    "CSCO": "Cisco",
    "TXN": "Texas Instruments",
    "XRX": "Xerox",
    "WMT": "Wal-Mart",
    "HD": "Home Depot",
    "GSK": "GlaxoSmithKline",
    "PFE": "Pfizer",
    "SNY": "Sanofi-Aventis",
    "NVS": "Novartis",
    "KMB": "Kimberly-Clark",
    "R": "Ryder",
    "GD": "General Dynamics",
    "RTN": "Raytheon",
    "CVS": "CVS",
    "CAT": "Caterpillar",
    "DD": "DuPont de Nemours",
}


symbols, names = np.array(sorted(symbol_dict.items())).T

quotes = []

for symbol in symbols:
    print("Fetching quote history for %r" % symbol, file=sys.stderr)
    url = (
        "https://raw.githubusercontent.com/scikit-learn/examples-data/"
        "master/financial-data/{}.csv"
    )
    quotes.append(pd.read_csv(url.format(symbol)))

close_prices = np.vstack([q["close"] for q in quotes])
open_prices = np.vstack([q["open"] for q in quotes])

# The daily variations of the quotes are what carry the most information
variation = close_prices - open_prices

from sklearn import covariance

alphas = np.logspace(-1.5, 1, num=10)
edge_model = covariance.GraphicalLassoCV(alphas=alphas)


X = variation.copy().T
X /= X.std(axis=0)
edge_model.fit(X)

from sklearn import cluster

_, labels = cluster.affinity_propagation(edge_model.covariance_, random_state=0)
n_labels = labels.max()

for i in range(n_labels + 1):
    print(f"Cluster {i + 1}: {', '.join(names[labels == i])}")

# Finding a low-dimension embedding for visualization: find the best position of
# the nodes (the stocks) on a 2D plane


from sklearn import manifold

node_position_model = manifold.LocallyLinearEmbedding(
    n_components=2, eigen_solver="dense", n_neighbors=6
)

embedding = node_position_model.fit_transform(X.T).T

import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

plt.figure(1, facecolor="w", figsize=(10, 8))
plt.clf()
ax = plt.axes([0.0, 0.0, 1.0, 1.0])
plt.axis("off")

# Plot the graph of partial correlations
partial_correlations = edge_model.precision_.copy()
d = 1 / np.sqrt(np.diag(partial_correlations))
partial_correlations *= d
partial_correlations *= d[:, np.newaxis]
non_zero = np.abs(np.triu(partial_correlations, k=1)) > 0.02

# Plot the nodes using the coordinates of our embedding
plt.scatter(
    embedding[0], embedding[1], s=100 * d**2, c=labels, cmap=plt.cm.nipy_spectral
)

# Plot the edges
start_idx, end_idx = np.where(non_zero)
# a sequence of (*line0*, *line1*, *line2*), where::
#            linen = (x0, y0), (x1, y1), ... (xm, ym)
segments = [
    [embedding[:, start], embedding[:, stop]] for start, stop in zip(start_idx, end_idx)
]
values = np.abs(partial_correlations[non_zero])
lc = LineCollection(
    segments, zorder=0, cmap=plt.cm.hot_r, norm=plt.Normalize(0, 0.7 * values.max())
)
lc.set_array(values)
lc.set_linewidths(15 * values)
ax.add_collection(lc)

# Add a label to each node. The challenge here is that we want to
# position the labels to avoid overlap with other labels
for index, (name, label, (x, y)) in enumerate(zip(names, labels, embedding.T)):
    dx = x - embedding[0]
    dx[index] = 1
    dy = y - embedding[1]
    dy[index] = 1
    this_dx = dx[np.argmin(np.abs(dy))]
    this_dy = dy[np.argmin(np.abs(dx))]
    if this_dx > 0:
        horizontalalignment = "left"
        x = x + 0.002
    else:
        horizontalalignment = "right"
        x = x - 0.002
    if this_dy > 0:
        verticalalignment = "bottom"
        y = y + 0.002
    else:
        verticalalignment = "top"
        y = y - 0.002
    plt.text(
        x,
        y,
        name,
        size=10,
        horizontalalignment=horizontalalignment,
        verticalalignment=verticalalignment,
        bbox=dict(
            facecolor="w",
            edgecolor=plt.cm.nipy_spectral(label / float(n_labels)),
            alpha=0.6,
        ),
    )

plt.xlim(
    embedding[0].min() - 0.15 * np.ptp(embedding[0]),
    embedding[0].max() + 0.10 * np.ptp(embedding[0]),
)
plt.ylim(
    embedding[1].min() - 0.03 * np.ptp(embedding[1]),
    embedding[1].max() + 0.03 * np.ptp(embedding[1]),
)

plt.show()

