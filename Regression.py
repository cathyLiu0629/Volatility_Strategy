import datetime

import pandas as pd
import sys
import os
from get_stock import *
import numpy as np
from sklearn.linear_model import LinearRegression

DATA_PATH = os.path.join(os.path.dirname(sys.argv[0]),'data')

def get_SMB():
    PctChg = pd.read_csv(os.path.join(DATA_PATH,'Pct_Chg.csv'),index_col=0,header=0).T
    MktCap = pd.read_csv(os.path.join(DATA_PATH,'MktCap.csv'),index_col=0,header=1).iloc[1:,1:]
    print(len(PctChg.columns))
    print(len(MktCap.columns))
    SMB_list=[]
    for i in range(len(MktCap.columns)):
        day_MktCap =MktCap.iloc[:,i].copy()
        day_PctChange = PctChg.iloc[:,i].copy()
        day_MktCap.sort_values(ascending=True,inplace=True)
        day_MktCap.dropna(inplace=True)
        #计算SMB
        min_cap_stock = day_MktCap[:int(len(day_MktCap)/3)]
        min_cap_weight = min_cap_stock/sum(min_cap_stock)
        max_cap_stock = day_MktCap[-int(len(day_MktCap)/3):]
        max_cap_weight = max_cap_stock/sum(max_cap_stock)

        min_stocks = min_cap_weight.index.tolist()
        max_stocks = max_cap_weight.index.tolist()

        min_return_df = day_PctChange.loc[min_stocks]
        max_return_df = day_PctChange.loc[max_stocks]
        min_return_df.fillna(0,inplace=True)
        max_return_df.fillna(0,inplace=True)
        #print(max_return_df)

        min_return=0
        max_return=0
        for j in range(len(min_return_df)):
            #print(min_return_df[j] * min_cap_weight[j])
            min_return += min_return_df[j]*min_cap_weight[j]

            max_return += max_return_df[j]*max_cap_weight[j]
        SMB_t = min_return - max_return
        #print(SMB_t)
        SMB_list.append(SMB_t)

    #print(SMB_list)
    SMB_df = pd.DataFrame([SMB_list],columns=MktCap.columns).T
    print(SMB_df)
    return SMB_df

def get_HML():
    PctChg = pd.read_csv(os.path.join(DATA_PATH, 'Pct_Chg.csv'), index_col=0, header=0).T
    MktCap = pd.read_csv(os.path.join(DATA_PATH, 'MktCap.csv'), index_col=0, header=1).iloc[1:,1:]
    PB = pd.read_csv(os.path.join(DATA_PATH, 'PB.csv'), index_col=0, header=1).iloc[1:,1:]
    HML_list=[]
    for i in range(len(PctChg.columns)):
        day_PctChg = PctChg.iloc[:,i].copy()
        day_MktCap =  MktCap.iloc[:,i].copy()
        day_PB = PB.iloc[:,i].copy()

        day_MktCap.dropna(inplace=True)
        day_PB.dropna(inplace=True)
        day_PB.sort_values(ascending=True, inplace=True)
        min_PB_stock = day_MktCap[:int(len(day_MktCap) / 3)].index.tolist()
        max_PB_stock = day_MktCap[-int(len(day_MktCap) / 3):].index.tolist()
        min_return = 0
        max_return =0
        day_PctChg.fillna(0,inplace=True)
        for stock in min_PB_stock:
            weight = day_MktCap[stock]/sum(day_MktCap)
            min_return+=weight*day_PctChg[stock]
        for stock in max_PB_stock:
            weight  = day_MktCap[stock]/sum(day_MktCap)
            max_return+=weight*day_PctChg[stock]
        HML_t = min_return- max_return

        HML_list.append(HML_t)
    HML_df = pd.DataFrame([HML_list], columns=MktCap.columns).T
    print(HML_df)

    return HML_df

def get_MKT():
    MktClose = pd.read_csv(os.path.join(DATA_PATH, 'MktClose.csv'), index_col=0, header=0).T
    MktClose['Pct_Chg']=MktClose['close']/MktClose['close'].shift(1)-1
    #print(MktClose)
    MktClose.dropna(how='any',axis=0,inplace=True)
    MktClose = MktClose[['Pct_Chg']]
    return MktClose

def get_return():
    Return = pd.read_csv(os.path.join(DATA_PATH, 'Close.csv'), index_col=0, header=1).iloc[1:, :].T
    original_columns = Return.columns
    for column in original_columns:
        Return[column+'_temp'] =Return[column]/Return[column].shift(1)-1
        Return.drop([column],axis=1,inplace=True)
        Return.rename({column+'_temp':column},axis=1,inplace  = True)
    Return.dropna(axis=0,how='all',inplace=True)
    print(len(Return))
    Return.to_csv(os.path.join(DATA_PATH, 'Pct_Chg.csv'))
    print(Return.head())
    return Return.T



class FF_Regression:
    def __init__(self,factor_list,return_data):
        #feed 进如的是每个月data! 30天 对于每只股票 y是30*1的数据，有n个 factor，factor是30*n的数据
        self.factor_list =  factor_list
        self.return_data =  return_data

    def regression_residual(self):
        self.return_data.dropna(axis=0, inplace=True)
        #对每只股票做循环
        month_factor_df={}
        for i in range(len(self.return_data)):
            stock = return_data.index.tolist()[i]
            y_data = self.return_data.iloc[i,:].T
            x_data = pd.concat(self.factor_list,axis=1)
            x_data.columns=['SMB','MKT','HML']
            #print(x_data)
            #print(y_data)
            linreg = LinearRegression()
            model = linreg.fit(x_data, y_data)
            y_pre = model.predict(x_data)
            residual = y_data - y_pre
            #print(residual)
            iv = np.std(residual)
            month_factor_df[stock]=iv
        print(month_factor_df)
        month_factor_df = pd.DataFrame(month_factor_df,index=['iv']).T
        #month_factor_df.to_csv(os.path.join(DATA_PATH,'iv.csv'))
        return month_factor_df




def get_next_month(datet):
    next_date = datet + datetime.timedelta(days=28)
    while next_date.month==datet.month:
        next_date+=datetime.timedelta(days=1)
    return next_date





if __name__=='__main__':
    start_d= datetime.datetime.strptime('20070101','%Y%m%d')
    return_data = pd.read_csv(os.path.join(DATA_PATH, 'Pct_Chg.csv'), index_col=0, header=0).T
    SMB_data =get_SMB()
    MKT_data =get_MKT()
    HML_data  = get_HML()

    factor_df = pd.DataFrame(index=return_data.index)
    for i in range(174):
        start_month = start_d.month

        current_month_1 = [m for m in return_data.columns if datetime.datetime.strptime(str(m),'%Y%m%d').month == start_month]
        current_month = [str(m) for m in return_data.columns if
                         datetime.datetime.strptime(str(m), '%Y%m%d').month == start_month]
        #print(current_month)
        return_data = return_data[current_month_1]
        #print(return_data)
        #print(return_data)
        factor_list = []
        factor_list.append(SMB_data.loc[current_month,:])
        factor_list.append(MKT_data.loc[current_month,:])
        factor_list.append(HML_data.loc[current_month,:])
        #print(factor_list)


        regression = FF_Regression(factor_list,return_data)
        monthly_factor = regression.regression_residual()
        factor_df = pd.concat([factor_df,monthly_factor],axis=1)
        print(factor_df)

        start_d = get_next_month(start_d)
    factor_df.to_csv(os.path.join(DATA_PATH, 'factor.csv'))




