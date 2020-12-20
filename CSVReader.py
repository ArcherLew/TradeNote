# csv
import csv
import datetime
import numpy as np
import pandas as pd

tradeDir = r'F:\\_Trading\\_Log\\'

class CSVReader:
    def read_trade_log(code):
        path = tradeDir + str(code) + '.csv'
        print(path)

        tmp_lst = []
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                tmp_lst.append(row)

        dt = np.dtype([
            ('date', 'u4'),
            ('code', 'u4'),
            ('amount', 'u4'),
            ('price', 'u4')])
        df = pd.DataFrame(tmp_lst[1:], columns=dt.names) # 也可以这么干 columns=tmp_lst[0]
        df['date'] = df['date'].map(int) # 这里将str转int，不然下面eval里的除法'/'会报错
        df['code'] = df['code'].map(int)
        df['amount'] = df['amount'].map(int)
        df['price'] = df['price'].map(float)
        # df.eval('''
        #         year = floor(date/10000)
        #         month = floor((date%10000)/100)
        #         day = floor(date%10000%100)
        #     ''', inplace=True)
        # df.index=pd.to_datetime(df.loc[:,['year','month','day']])
        df.index = df['date']
        # print(df.index)
        # print("------------")
        return df


# read_trade_log(300083)
