import pandas as pd
import matplotlib.pyplot as plt
import os
from Regression import *
import scipy.stats as st

class Factor_Analysis(object):
    def __init__(self,factor_df):
        self.factor = factor_df
    @staticmethod
    def get_forward_20_return():
        Return = pd.read_csv(os.path.join(DATA_PATH, 'Close.csv'), index_col=0, header=1).iloc[1:, :].T
        original_columns = Return.columns
        Return_new = Return.shift(-20) / Return - 1
        '''for column in original_columns:
            Return[column + '_temp'] = Return[column].shift(-20) / Return[column] - 1
            Return.drop([column], axis=1, inplace=True)
            Return.rename({column + '_temp': column}, axis=1, inplace=True)'''
        Return_new.dropna(axis=0, how='all', inplace=True)
        print(Return.head())
        return Return_new

    def cal_IC(self):
        # 计算了每一个月的**因子**和**之后20日收益**的秩相关系数
        self.factor.index = pd.to_datetime(self.factor.index)
        forward_20d_return_data = Factor_Analysis.get_forward_20_return()
        ic_data = pd.DataFrame(index=forward_20d_return_data.index, columns=['IC', 'pValue'])

        # 计算相关系数
        for dt in ic_data.index:
            tmp_factor = self.factor.ix[dt]
            tmp_ret = forward_20d_return_data.ix[dt]
            cor = pd.DataFrame(tmp_factor)
            ret = pd.DataFrame(tmp_ret)
            cor.columns = ['corr']
            ret.columns = ['ret']
            cor['ret'] = ret['ret']
            cor = cor[~np.isnan(cor['corr'])][~np.isnan(cor['ret'])]
            if len(cor) < 5:
                continue

            ic, p_value = st.spearmanr(cor['corr'], cor['ret'])  # 计算秩相关系数 RankIC
            ic_data['IC'][dt] = ic
            ic_data['pValue'][dt] = p_value

        # 每一天的**因子**和**之前20日收益**的秩相关系数作图

        fig = plt.figure(figsize=(16, 6))
        ax1 = fig.add_subplot(111)

        lns1 = ax1.plot(ic_data[ic_data > 0].index, ic_data[ic_data > 0].IC, '.r', label='IC(plus)')
        lns2 = ax1.plot(ic_data[ic_data < 0].index, ic_data[ic_data < 0].IC, '.b', label='IC(minus)')

        lns = lns1 + lns2
        labs = [l.get_label() for l in lns]
        ax1.legend(lns, labs, bbox_to_anchor=[0.6, 0.1], loc='', ncol=2, mode="", borderaxespad=0., fontsize=12)
        ax1.set_ylabel('相关系数',  fontsize=16)
        ax1.set_xlabel('日期', fontsize=16)
        ax1.set_title("特质动量因子与之后一个月收益月度IC", fontsize=16)
        ax1.grid()
    def cal_excess_return(self):
        n_quantile = 10
        # 统计十分位数
        cols_mean = [i + 1 for i in range(n_quantile)]
        cols = cols_mean

        excess_returns_means = pd.DataFrame(index=self.factor.index, columns=cols)

        # 计算因子分组的超额收益平均值
        for dt in excess_returns_means.index:
            qt_mean_results = []

            # ILLIQ去掉nan
            tmp_factor = self.factor.ix[dt].dropna()
            forward_20d_return_data = Factor_Analysis.get_forward_20_return()
            tmp_return = forward_20d_return_data.ix[dt].dropna()
            tmp_return = tmp_return[tmp_return < 0.6]
            tmp_return_mean = tmp_return.mean()

            pct_quantiles = 1.0 / n_quantile
            for i in range(n_quantile):
                down = tmp_factor.quantile(pct_quantiles * i)
                up = tmp_factor.quantile(pct_quantiles * (i + 1))
                i_quantile_index = tmp_factor[(tmp_factor <= up) & (tmp_factor >= down)].index
                mean_tmp = tmp_return[i_quantile_index].mean() - tmp_return_mean
                qt_mean_results.append(mean_tmp)

            excess_returns_means.ix[dt] = qt_mean_results

        excess_returns_means.dropna(inplace=True)

        # 因子分组的超额收益作图
        fig = plt.figure(figsize=(12, 6))
        ax1 = fig.add_subplot(111)

        excess_returns_means_dist = excess_returns_means.mean()
        excess_dist_plus = excess_returns_means_dist[excess_returns_means_dist > 0]
        excess_dist_minus = excess_returns_means_dist[excess_returns_means_dist < 0]
        lns2 = ax1.bar(excess_dist_plus.index, excess_dist_plus.values, align='center', color='r', width=0.35)
        lns3 = ax1.bar(excess_dist_minus.index, excess_dist_minus.values, align='center', color='g', width=0.35)

        ax1.set_xlim(left=0.5, right=len(excess_returns_means_dist) + 0.5)
        # ax1.set_ylim(-0.008, 0.008)
        ax1.set_ylabel(u'超额收益',  fontsize=16)
        ax1.set_xlabel(u'十分位分组',  fontsize=16)
        ax1.set_xticks(excess_returns_means_dist.index)
        ax1.set_xticklabels([int(x) for x in ax1.get_xticks()],  fontsize=14)
        ax1.set_yticklabels([str(x * 100) + '0%' for x in ax1.get_yticks()],  fontsize=14)
        ax1.set_title(u"因子超额收益",  fontsize=16)
        ax1.grid()

