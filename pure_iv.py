import os.path

from Regression import *



def regression_self():
    iv_data = pd.read_csv(os.path.join(DATA_PATH,'iv.csv'))
    month_factor_df = pd.DataFrame()
    for m in range(len(iv_data)-6):
        m_data = iv_data.iloc[:,m:m+6]
        month = iv_data.columns[m+6]
        # 对每只股票做循环

        y_data = m_data.iloc[:,5].T
        x_data = m_data.iloc[:,:5].T

        linreg = LinearRegression()
        model = linreg.fit(x_data, y_data)
        y_pre = model.predict(x_data)
        residual = y_data - y_pre
        residual.columns = [month]
        print(month_factor_df)
        month_factor_df = pd.concat([month_factor_df,residual], axis=1)
        # month_factor_df.to_csv(os.path.join(DATA_PATH,'iv.csv'))
    return month_factor_df