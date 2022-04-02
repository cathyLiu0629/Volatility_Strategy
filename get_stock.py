import pandas as pd
import datetime
from config_operate import *
my_config = MyConfig()
token = my_config.get_tushre_token()
import tushare as ts
pro = ts.pro_api(token)
from dateutil.parser import parse



class FilterStocks():
    '''
    获取某日的成分股股票
    1.过滤ST
    2.过滤上市不足N个月
    3.过滤当月交易不超过N日的股票
    '''
    def __init__(self,index,date,N=90,active_day=15):
        '''
        :param index: 'A'全市场
        :param date: 日期
        :param N: 上市日期不足N日
        :param active_day: 过滤交易不足N日的股票
        '''
        self.__index = index
        self.__date = parse(date).date().strftime('%Y%m%d')
        self.__N = N
        self.__active_day = active_day
    @property
    def get_stocks(self):
        if self.__index == 'A':
            stock_list = pro.query('stock_basic', exchange='', list_status='L', fields='ts_code')['ts_code'].tolist()
        else:
            stock_list = list(pro.index_weight(self.__index,start_date = self.__date,end_date=self.__date)['con_code'])
        stock_list = self.delete_stop(stock_list,self.__date)
        stock_list = self.delete_pause(stock_list,self.__date)
        return stock_list
    @staticmethod
    def get_trade_days(start,end):
        cal_df = pro.trade_cal(exchange='', start_date=start, end_date=end)
        cal_list = cal_df.loc[cal_df['is_open']==1,'cal_date'].tolist()
        return cal_list

    @staticmethod
    def delete_stop(stock_list,begin_date,n=90):
        #剔除上市时间不足3个月的股票
        company_list_sh= pro.stock_company( fields='ts_code,setup_date',exchange='SSE')
        company_list_sz = pro.stock_company(fields='ts_code,setup_date', exchange='SZSE')
        company_list = pd.concat([company_list_sh,company_list_sz])
        going_stock_list = company_list.loc[company_list['setup_date'] < ((datetime.datetime.strptime(begin_date,'%Y%m%d') - datetime.timedelta(days=n))).strftime('%Y%m%d')]['ts_code'].tolist()
        stocks  = set(stock_list) & set(going_stock_list)
        return list(stocks)
    @staticmethod
    def delete_pause(stock_list,date,n=30):
        begin_date = (datetime.datetime.strptime(date,'%Y%m%d') - datetime.timedelta(days=n)).strftime('%Y%m%d')
        cal_list = FilterStocks.get_trade_days(begin_date,date)
        suspend_stock=[]
        for trade_day in cal_list:
            df = pro.suspend_d(suspend_type='S', trade_date=trade_day)
            for stock in df.ts_code:
                if stock in stock_list:
                    suspend_stock.append(stock)
        stock_set = set(stock_list)
        suspend_stock = set(suspend_stock)
        return list(stock_set-suspend_stock)


if __name__=='__main__':
    s1 = FilterStocks('A','2022-01-05',20,30)
    s1 = s1.get_stocks