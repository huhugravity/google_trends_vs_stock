'''
Created on Jun 24, 2015
explore the correlation btw search interests (from google trend) and stock market prices (from yahoo finance)
use yahoo_finance library to retrieve historical data from yahoo finance (https://pypi.python.org/pypi/yahoo-finance/1.1.4)
netflix on google trends: https://www.google.com/trends/explore#q=netflix&geo=US&cmpt=q&tz=Etc%2FGMT%2B7
@author: Hu
'''
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from yahoo_finance import Share
from os.path import exists
import numpy as np
from datetime import datetime, date
from pyGTrends import pyGTrends
import time
from random import randint
import re

def read_sp500_symbol():
    _filename = 'data/sp500_symbol.csv'
    pass
    
def normalization(_data, method='zscore'):
    _normarlized_data = []
    _data = np.array(_data)
    if method=='maxmin':
        _normarlized_data = (_data - np.min(_data) + 0.0)/(np.max(_data) - np.min(_data))
    else:
        _normarlized_data = (_data - np.mean(_data) + 0.0)/np.std(_data)
    return _normarlized_data

def format_raw_google_trends_report(_raw_data):
    _raw_data = _raw_data.split('\n')
    num_blank_rows = 0
    add_data_flag = False
    i = 0
    _formate_data = []
    while(i<len(_raw_data)):
        row = _raw_data[i]
        if row == '':
            num_blank_rows = num_blank_rows + 1
            if num_blank_rows > 1:
                break
            add_data_flag = True
            i = i + 3
            continue
        if add_data_flag:
            _formate_data.append(re.split(' - |,', row))
        i = i + 1
    if _formate_data == []:
        raise Exception('No Data Returned!')
        print _raw_data
    return _formate_data

if __name__ == '__main__':
    company_short_name = 'cisco' #apple,netflix,irobot,coca
    company_name_info = {'netflix':{'symbol':'NFLX','search_string':'/m/017rf_'}, 
                         'apple':{'symbol':'AAPL','search_string':'/m/0k8z'}, #027lnzs (iphone), 0k8z(apple)
                         'cisco':{'symbol':'CSCO','search_string':'/m/0dmtp'},
                         'irobot':{'symbol':'IRBT','search_string':'/m/03ymt0'},
                         'coca':{'symbol':'KO','search_string':'/m/03phgz'},
                         }
    stock_symbol = company_name_info[company_short_name]['symbol']
    print company_short_name, stock_symbol
    
    # read or request stock data
    stockdata_filename = 'data/' + company_short_name + '_stock_prices.csv'
    if not exists(stockdata_filename):
        print 'retrieving stock data from yahoo finance...'
        share = Share(stock_symbol)
        daily_stock = share.get_historical('2004-01-01', str(date.today()))
        stock_df = pd.DataFrame(daily_stock) ##Date,Open,High,Low,Close,Volume,Adj_Close
        stock_df.to_csv(stockdata_filename, sep=',', index=False)
        stock_df['Date'] = pd.to_datetime(stock_df['Date'])
        fieldnames_float = ['Open','High','Low','Close','Volume','Adj_Close']
        for fieldname in fieldnames_float:
            stock_df[fieldname] = stock_df[fieldname].astype(float)
        
    else:
        stock_df = pd.read_csv(stockdata_filename, header = 0,
                           parse_dates=['Date'], infer_datetime_format=True)
    stock_df.index = stock_df['Date']
    
    # read or request trends data
    google_trends_filename = 'data/us_' + company_short_name + '_google_trends.csv'
    if not exists(google_trends_filename):
        print 'request data from google trends...'
        google_username = '@gmail.com'
        google_password = ''
        connector = pyGTrends(google_username, google_password) #connect to Google
        #make request
        connector.request_report(company_name_info[company_short_name]['search_string'], geo='US', use_topic=False)
        raw_data = connector.get_data()
        format_data = format_raw_google_trends_report(raw_data)
        us_interests_df = pd.DataFrame(format_data, columns=['week_start','week_end','us_interest'])
        us_interests_df.to_csv(google_trends_filename, sep=',', index=False)
        us_interests_df['week_start'] = pd.to_datetime(us_interests_df['week_start'])
        us_interests_df['week_end'] = pd.to_datetime(us_interests_df['week_end'])
        us_interests_df['us_interest'] = us_interests_df['us_interest'].astype(float)
        #wait a random amount of time between requests to avoid bot detection
#         time.sleep(randint(5,10))
    else:
        us_interests_df = pd.read_csv(google_trends_filename, header = 0,
                           parse_dates=['week_start','week_end'], infer_datetime_format=True)
    #print stock_df.info(), us_interests_df.info()
    
    # read sp500 stock prices
    sp500_stockdata_filename = 'data/sp500_stock_prices.csv'
    sp500_stock_df = pd.read_csv(sp500_stockdata_filename, header = 0,
                           parse_dates=['Date'], infer_datetime_format=True)
    sp500_stock_df.index = sp500_stock_df['Date']
    
    stock_df = stock_df.merge(sp500_stock_df[['Date','Adj_Close']], how='left', on=['Date'], suffixes=('', '_sp500'))
    
    # plot data
    normalization_method = 'zscore'
    plt.figure(figsize=(16,6))
    # plot us_interest
    dates = mdates.date2num(us_interests_df['week_start'])
    us_interests_normalized = normalization(us_interests_df['us_interest'], normalization_method)
    plt.plot_date(dates, us_interests_normalized, ls='-', marker='', markeredgewidth=0.0,
                      markeredgecolor=None, color='r', label='us_interest')
    
    # plot stock prices
    dates = mdates.date2num(stock_df['Date'])
    Adj_Close_normalized = normalization(stock_df['Adj_Close'], normalization_method)
    plt.plot_date(dates, Adj_Close_normalized, ls='-', marker='', markeredgewidth=0.0,
                      markeredgecolor=None, color='g', label='stock_Adj_Close')

    # plot stock prices against sp500_prices
    Adj_Close_over_sp500_normalized = normalization(stock_df['Adj_Close']/stock_df['Adj_Close_sp500'], 
                                         normalization_method)
    plt.plot_date(dates, Adj_Close_over_sp500_normalized, ls='-', marker='', markeredgewidth=0.0,
                      markeredgecolor=None, color='b', label='stock_Adj_Close_OVER_sp500')

    plt.legend(loc=0)
    plt.title(company_short_name)
    plt.show()
    
