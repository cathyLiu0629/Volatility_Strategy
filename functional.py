import pandas as pd
import datetime
from config_operate import *
from get_stock import *
from tqdm import tqdm
from get_stock import FilterStocks
import numpy as np




def query_PB(begin_date,end_date):
    #先获取可以直接获取的因子值
    trade_days = FilterStocks.get_trade_days(begin_date,end_date)
    df_all=[]
    for day in trade_days:
        df = pro.daily_basic(trade_date=day, fields='ts_code,pb')
        df['date']=day

        df_all.append(df)
    df_all=pd.concat(df_all)

    df = pd.pivot_table(df_all,index=['ts_code'],values=["pb"],
               columns=["date"])
    df.to_csv('PB.csv')
    #factors为指定股票池，指定日期的因子df
    print(df)
    return df
def query_mkt_cap(begin_date,end_date):
    #先获取可以直接获取的因子值
    trade_days = FilterStocks.get_trade_days(begin_date,end_date)
    df_all=[]
    for day in trade_days:
        df = pro.daily_basic(trade_date=day, fields='ts_code,circ_mv')
        df['date']=day

        df_all.append(df)
    df_all=pd.concat(df_all)

    df = pd.pivot_table(df_all,index=['ts_code'],values=["circ_mv"],
               columns=["date"])
    df.to_csv('MktCap.csv')
    #factors为指定股票池，指定日期的因子df
    print(df)
    return df
def query_close_price(begin_date,end_date):
    #先获取可以直接获取的因子值
    trade_days = FilterStocks.get_trade_days(begin_date,end_date)
    df_all=[]
    for day in trade_days:
        df = pro.daily_basic(trade_date=day, fields='ts_code,close')
        df['date']=day

        df_all.append(df)
    df_all=pd.concat(df_all)

    df = pd.pivot_table(df_all,index=['ts_code'],values=["close"],
               columns=["date"])
    df.to_csv('Close.csv')
    #factors为指定股票池，指定日期的因子df
    print(df)
    return df
def query_mkt_close_price(begin_date,end_date):
    #先获取可以直接获取的因子值
    trade_days = FilterStocks.get_trade_days(begin_date,end_date)
    df_all=[]
    for day in trade_days:
        df = pro.index_daily(ts_code='000002.SH', start_date=day, end_date=day)[['trade_date','close']]
        df.columns=['date','close']
        df_all.append(df)
    df_all=pd.concat(df_all)

    df = pd.pivot_table(df_all,index=['date'],values=["close"]).T
    df.to_csv('MktClose.csv')
    #factors为指定股票池，指定日期的因子df
    print(df)
    return df
def query_pct_change(begin_date,end_date):
    #先获取可以直接获取的因子值
    trade_days = FilterStocks.get_trade_days(begin_date,end_date)
    df_all=[]
    for day in trade_days:
        print(day)
        stock_list = FilterStocks('A',day).get_stocks
        df = pro.index_daily(ts_code=','.join(stock_list), start_date=day, end_date=day)[['ts_code','trade_date','pct_chg']]
        df.columns=['ts_code','date','pct_chg']
        df['pct_chg'] = df['pct_chg'].astype('float64')
        df_all.append(df)
    df_all=pd.concat(df_all)
    df_all.to_csv('Pct_Chg.csv')
    df = pd.pivot_table(df_all,index=['ts_code'],values=["pct_chg"],columns=["date"])
    df.to_csv('Pct_Chg.csv')
    #factors为指定股票池，指定日期的因子df
    print(df)
    return df



#factors = get_factor(query_PB,'000300.XSHG',start_date,end_date)
if __name__=='__main__':
    start_date = '20070101'
    end_date = '20210701'
    query_pct_change(start_date,end_date)
