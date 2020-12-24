# csv
import csv
import datetime
import math
import numpy as np
import pandas as pd

tradeDir = r'F:\\_Trading\\_Log\\'

class CSVReader:
    HTColumnNames = { 'date':'发生日期', 'code':'证券代码', 'bsmark':'买卖标志', 'amount':'成交数量', 'price':'成交价格'}
    GXColumnNames = { 'date':'成交日期', 'code':'证券代码', 'bsmark':'买卖标志', 'amount':'成交数量', 'price':'成交价格'}
    ColumnNames = { 'ht':HTColumnNames, 'gx':GXColumnNames }

    # code:dataframe
    tradeData = {}
    def get_trade_data(self, alldf, code):
        df = alldf.loc[(alldf['code'] == code)]
        df.index = df['date']
        print("------------")
        print(df)
        return df

    def load_trade_log(self, qs):
        path = tradeDir + 'GX-200625-201218' + '.csv'
        print(path)

        tmp_lst = []
        with open(path, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                tmp_lst.append(row)

        colMaps = self.ColumnNames[qs]
        print(colMaps)

        rawdf = pd.DataFrame(tmp_lst[1:], columns=tmp_lst[0])

        dt = np.dtype([
            ('date', 'u4'),
            ('code', 'u4'),
            ('amount', 'u4'),
            ('price', 'u4'),
            ('bs', 'u4'),
            ('bsmark', 'u4')])

        df = pd.DataFrame(columns=dt.names) # 也可以这么干 columns=tmp_lst[0]
        df['date'] = rawdf[colMaps['date']].map(int) # 这里将str转int，不然下面eval里的除法'/'会报错
        df['code'] = rawdf[colMaps['code']].map(int)
        df['amount'] = rawdf[colMaps['amount']].map(int)
        df['price'] = rawdf[colMaps['price']].map(float)
        df['bsmark'] = rawdf[colMaps['bsmark']].map(str)
        df["bs"] = np.where(df.bsmark == '证券买入', 1, -1)

        # df.eval('''
        #         year = floor(date/10000)
        #         month = floor((date%10000)/100)
        #         day = floor(date%10000%100)
        #     ''', inplace=True)
        # df.index=pd.to_datetime(df.loc[:,['year','month','day']])

        # 用不了会报错：NotImplementedError: 'IfExp' nodes are not implemented
        # df.eval('bs=1 if bs==\'证券买入\' else -1', inplace=True)

        df.index = df['date']


        # for index, row in df.iterrows():
        #     bs = 1 if row['bs'] =='证券买入' else -1
        #     row['amount'] = math.fabs(row['amount']) * bs
            # df.iloc[index] = row # 这样改会报错 IndexError: single positional indexer is out-of-bounds
            # df.loc[index,'amount'] = math.fabs(row['amount']) * bs # 这样改值错乱

        print(df)
        # print("------------")
        return df

reader = CSVReader()
alldf = reader.load_trade_log("gx")
df = reader.get_trade_data(alldf, 300088)