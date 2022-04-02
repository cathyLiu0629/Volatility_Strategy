import pandas as pd
import sys
import os
from get_stock import *
import numpy as np

DATA_PATH = os.path.join(os.path.dirname(sys.argv[0]),'data')

def get_independent_variables():
    Mkt_Ret = pd.read_csv(os.path.join(DATA_PATH,'MktClose.csv'))

def get_SMB():
    PctChg = pd.read_csv(os.path.join(DATA_PATH,'Pct_Chg.csv'),index_col=0,header=1).iloc[1:,:]
    MktCap = pd.read_csv(os.path.join(DATA_PATH,'MktCap.csv'),index_col=0,header=1).iloc[1:,:]
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

        min_return=0
        max_return=0
        for j in range(len(min_return_df)):
            min_return +=  min_return_df[j]*min_cap_weight[j]
            max_return += max_return_df[j]*max_cap_weight[j]
        SMB_t = min_return - max_return
        SMB_list.append(SMB_t)
    print(len(SMB_list))
    SMB_df = pd.DataFrame([SMB_list],columns=MktCap.columns).T
    return SMB_df

def get_HML():
    PctChg = pd.read_csv(os.path.join(DATA_PATH, 'Pct_Chg.csv'), index_col=0, header=1).iloc[1:, :]
    MktCap = pd.read_csv(os.path.join(DATA_PATH, 'MktCap.csv'), index_col=0, header=1).iloc[1:, :]
    PB = pd.read_csv(os.path.join(DATA_PATH, 'PB.csv'), index_col=0, header=1).iloc[1:, :]
    HML_list=[]
    for i in range(len(PctChg.columns)):
        day_PctChg = PctChg.iloc[:,i]
        day_MktCap =  MktCap.iloc[:,i]
        day_PB = PB.iloc[:,i]

        day_MktCap.dropna(inplace=True)
        day_PB.dropna(inplace=True)
        day_PB.sort_values(ascending=True, inplace=True)
        min_PB_stock = day_MktCap[:int(len(day_MktCap) / 3)].index.tolist()
        max_PB_stock = day_MktCap[-int(len(day_MktCap) / 3):].index.tolist()
        min_return = 0
        max_return =0
        for stock in min_PB_stock:
            weight = day_MktCap[stock]/sum(day_MktCap)
            min_return+=weight*day_PctChg[stock]
        for stock in max_PB_stock:
            weight  = day_MktCap[stock]/sum(day_MktCap)
            max_return+=weight*day_PctChg[stock]
        HML_t = min_return- max_return
        HML_list.append(HML_t)
    SMB_df = pd.DataFrame([HML_list], columns=MktCap.columns).T
    return SMB_df

def get_MKT():
    MktClose = pd.read_csv(os.path.join(DATA_PATH, 'MktClose.csv'), index_col=0, header=0).T
    MktClose['Pct_Chg']=MktClose['close']/MktClose['close'].shift(1)-1
    print(MktClose)
    MktClose.fillna(0,inplace=True)
    MktClose = MktClose[['Pct_Chg']]
    return MktClose

if __name__=='__main__':
    get_MKT()



