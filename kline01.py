# -*- coding:utf-8 -*-
import tushare as ts  # 获取股票数据用
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker  # 用于日期刻度定制
# import mpl_finance as mpf
# 注释了上面一行的旧版，新版是mplfinance，少了一个下划线，运行没警告，新版绘制蜡烛图性能应该更高，但是限得比较死，
# 不好加子图，后面我们把关键代码拿出来自己绘制
import mplfinance as mpf
from mplfinance import original_flavor as ompf  # 用新版库里面的旧版实现(跟mpl_finance一模一样)
from matplotlib import colors as mcolors  # 用于颜色转换成渲染时顶点需要的颜色格式
from matplotlib.collections import LineCollection, PolyCollection  # 用于绘制直线集合和多边形集合
# import tools  # 计算MACD和KDJ(没有使用talib，有缺陷)

from CSVReader import CSVReader

# csv
import csv
import datetime
#
draw_macd = False
draw_kdj = False

# 在k线基础上计算MACD，并将结果存储在df上面(dif,dea,bar)
def calc_macd(df, fastperiod=12, slowperiod=26, signalperiod=9):
    ewma12 = df['close'].ewm(span=fastperiod, adjust=False).mean()
    ewma26 = df['close'].ewm(span=slowperiod, adjust=False).mean()
    df['dif'] = ewma12 - ewma26
    df['dea'] = df['dif'].ewm(span=signalperiod, adjust=False).mean()
    df['bar'] = (df['dif'] - df['dea']) * 2
    # df['macd'] = 0
    # series = df['dif']>0
    # df.loc[series[series == True].index, 'macd'] = 1
    return df


# 在k线基础上计算KDF，并将结果存储在df上面(k,d,j)
def calc_kdj(df):
    low_list = df['low'].rolling(9, min_periods=9).min()
    low_list.fillna(value=df['low'].expanding().min(), inplace=True)
    high_list = df['high'].rolling(9, min_periods=9).max()
    high_list.fillna(value=df['high'].expanding().max(), inplace=True)
    rsv = (df['close'] - low_list) / (high_list - low_list) * 100
    df['k'] = pd.DataFrame(rsv).ewm(com=2).mean()
    df['d'] = df['k'].ewm(com=2).mean()
    df['j'] = 3 * df['k'] - 2 * df['d']

    # df['kdj'] = 0
    # series = df['k']>df['d']
    # df.loc[series[series == True].index, 'kdj'] = 1
    # # df.loc[series[(series == True) & (series.shift() == False)].index, 'kdjcross'] = 1
    # # df.loc[series[(series == False) & (series.shift() == True)].index, 'kdjcross'] = -1

def read_daily_data(filePath):
    dt = np.dtype([
        ('date', 'u4'),
        ('open', 'u4'),
        ('high', 'u4'),
        ('low', 'u4'),
        ('close', 'u4'),
        ('amount', 'f'),
        ('volume', 'u4'),
        ('reserve','u4')])
    data = np.fromfile(filePath, dtype=dt)
    #df = pd.DataFrame(data)
    # Or if you want to explicitly set the column names
    df = pd.DataFrame(data, columns=data.dtype.names)
    df.eval('''
        dt=date
    ''',inplace=True)
    # df.eval('''
    #     year=floor(date/10000)
    #     month=floor((date%10000)/100)
    #     day=floor(date%10000%100)
    #     open=open/100
    #     high=high/100
    #     low=low/100
    #     close=close/100
    # ''',inplace=True)
    return df

tradeData = CSVReader.read_trade_log(300083)
print(tradeData)
print("--------------------")

# 获取数据
dailyPath = r'C:\\Program Files\\HuaTai\\vipdoc\\sz\\lday\\sz300083.day'
df = read_daily_data(dailyPath)
# df = ts.get_k_data('603986', '2019-01-01')  # 获取日K线数据
# df.drop('code', axis=1, inplace=True)  # 剔除多余的列
if draw_macd: calc_macd(df)  # 计算MACD值，数据存于DataFrame中
if draw_kdj: calc_kdj(df)  # 计算KDJ值，数据存于DataFrame中
df = df[-50:]  # 取最近的N天测试，列顺序为 date,open,close,high,low,volume,dif,dea,bar,k,d,j
# print(df)
# print("--------------------")

# 日期转换成整数序列
date_tickers = df.date.values
df.date = range(0, len(df))  # 日期改变成序号
matix = df.values  # 转换成绘制蜡烛图需要的数据格式(date, open, close, high, low, volume)
xdates = matix[:, 0]  # X轴数据(这里用的天数索引)

# print(df['dt'])

# 设置外观效果
plt.rc('font', family='Microsoft YaHei')  # 用中文字体，防止中文显示不出来
plt.rc('figure', fc='k')  # 绘图对象背景图
plt.rc('text', c='#800000')  # 文本颜色
plt.rc('axes', axisbelow=True, xmargin=0, fc='k', ec='#800000', lw=1.5, labelcolor='#800000',
       unicode_minus=False)  # 坐标轴属性(置底，左边无空隙，背景色，边框色，线宽，文本颜色，中文负号修正)
plt.rc('xtick', c='#d43221')  # x轴刻度文字颜色
plt.rc('ytick', c='#d43221')  # y轴刻度文字颜色
plt.rc('grid', c='#800000', alpha=0.9, ls=':', lw=0.8)  # 网格属性(颜色，透明值，线条样式，线宽)
plt.rc('lines', lw=0.8)  # 全局线宽

# 创建绘图对象和4个坐标轴
fig = plt.figure(figsize=(16, 8))
left, width = 0.05, 0.9
ax1 = fig.add_axes([left, 0.6, width, 0.35])  # left, bottom, width, height
ax2 = fig.add_axes([left, 0.45, width, 0.15], sharex=ax1)  # 共享ax1轴
if draw_macd: ax3 = fig.add_axes([left, 0.25, width, 0.2], sharex=ax1)  # 共享ax1轴
if draw_kdj: ax4 = fig.add_axes([left, 0.05, width, 0.2], sharex=ax1)  # 共享ax1轴
plt.setp(ax1.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示
plt.setp(ax2.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示
if draw_macd: plt.setp(ax3.get_xticklabels(), visible=False)  # 使x轴刻度文本不可见，因为共享，不需要显示


# 绘制蜡烛图
def format_date(x, pos=None):
    # 日期格式化函数，根据天数索引取出日期值
    return '' if x < 0 or x > len(date_tickers) - 1 else date_tickers[int(x)]

# 设置自定义x轴格式化日期函数
ax1.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
# 横向最多排15个左右的日期，最少5个，防止日期太拥挤
ax1.xaxis.set_major_locator(ticker.MultipleLocator(max(int(len(df) / 15), 5)))
# lx:y轴刻度不对
ax1.yaxis.label.set_color("w")
ax1.tick_params(axis='y', colors='w')
ax1.yaxis.set_major_locator(ticker.MaxNLocator(prune='upper'))
# ompf.candlestick_ochl(ax1, matix, width=0.5, colorup='#ff3232', colordown='#54fcfc')
## 下面这一段代码，替换了上面注释的这个函数，因为上面的这个函数达不到同花顺的效果
# 取出ochl值
opens, closes, highs, lows = matix[:, 1], matix[:, 4], matix[:, 2], matix[:, 3]
# 计算每个日期之间的距离
avg_dist_between_points = (xdates[-1] - xdates[0]) / float(len(xdates))
# 用于K线实体(矩形)的偏移坐标计算
delta = avg_dist_between_points / 4.0
# 生成K线实体(矩形)的4个顶点坐标
barVerts = [((date - delta, open), (date - delta, close), (date + delta, close), (date + delta, open)) for
            date, open, close in zip(xdates, opens, closes)]
# 生成下影线顶点列表
rangeSegLow = [((date, low), (date, min(open, close))) for date, low, open, close in zip(xdates, lows, opens, closes)]
# 生成上影线顶点列表
rangeSegHigh = [((date, high), (date, max(open, close))) for date, high, open, close in zip(xdates, highs, opens, closes)]
# 上下影线顶点列表
rangeSegments = rangeSegLow + rangeSegHigh
cmap = {True: mcolors.to_rgba('#000000', 1.0),
        False: mcolors.to_rgba('#000000', 1.0)}  # K线实体(矩形)中间的背景色(True是上涨颜色，False是下跌颜色)
# K线实体(矩形)中间的背景色列表
inner_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]
cmap = {True: mcolors.to_rgba('#ff3232', 1.0),
        False: mcolors.to_rgba('#54fcfc', 1.0)}  # K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)
# K线实体(矩形)边框线颜色(上下影线和后面的成交量颜色也共用)列表
updown_colors = [cmap[opn < cls] for opn, cls in zip(opens, closes)]
# 生成上下影线的顶点数据(颜色，线宽，反锯齿，反锯齿关闭好像没效果)
ax1.add_collection(LineCollection(rangeSegments, colors=updown_colors, linewidths=0.5, antialiaseds=False))
# 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)
ax1.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=False, linewidths=0.5))

# lx:绘制买卖点
for index, row in df.iterrows():
    # if tradeData.loc[[row.dt]]:
    # print(row['dt'])
    dt = row['dt']

    # 不加这个判断， logs = tradeData.loc[[dt],['amount', 'price']] 会报错如下：
    # #KeyError: "None of [Float64Index([20201012.0], dtype='float64', name='date')] are in the [index]"
    if dt in tradeData.index.values:
        print("---", dt, "---")
        date = row['date']
        logs = tradeData.loc[[dt],['amount', 'price']]
        # print(logs)
        for _, log in logs.iterrows():
            print(log)
            _color = 'r' if log.amount > 0 else '#00ff00'
            _marker = '>' if log.amount > 0 else '<'
            x = date-0.25 if log.amount > 0 else date+0.25
            y = log.price * 100
            ax1.scatter(x, y, marker=_marker, color=_color)


# 绘制均线
mav_colors = ['#ffffff', '#d4ff07', '#ff80ff', '#00e600', '#02e2f4', '#ffffb9', '#2a6848']  # 均线循环颜色
mav_period = [5, 10, 20, 60]  # 定义要绘制的均线周期，可增减
n = len(df)
for i in range(len(mav_period)):
    if n >= mav_period[i]:
        mav_vals = df['close'].rolling(mav_period[i]).mean().values
        ax1.plot(xdates, mav_vals, c=mav_colors[i % len(mav_colors)]) # , label='MA' + str(mav_period[i]) #均线说明框，加在 plot 参数列表末尾
ax1.set_title('K线图')  # 标题
ax1.grid(True)  # 画网格
# ax1.legend(loc='upper right')  # 图例放置于右上角
ax1.xaxis_date()  # 好像要不要效果一样？

# 绘制成交量和成交量均线（5日，10日）
# ax2.bar(xdates, matix[:, 5], width= 0.5, color=updown_colors) # 绘制成交量柱状图
barVerts = [((date - delta, 0), (date - delta, vol), (date + delta, vol), (date + delta, 0)) for date, vol in
            zip(xdates, matix[:, 5])]  # 生成K线实体(矩形)的4个顶点坐标
ax2.add_collection(PolyCollection(barVerts, facecolors=inner_colors, edgecolors=updown_colors, antialiaseds=False, linewidths=0.5))  # 生成多边形(矩形)顶点数据(背景填充色，边框色，反锯齿，线宽)
if n >= 5:  # 5日均线，作法类似前面的均线
    vol5 = df['volume'].rolling(5).mean().values
    ax2.plot(xdates, vol5, c='y', label='VOL5')
if n >= 10:  # 10日均线，作法类似前面的均线
    vol10 = df['volume'].rolling(10).mean().values
    ax2.plot(xdates, vol10, c='w', label='VOL10')
ax2.yaxis.set_ticks_position('right')  # y轴显示在右边
ax2.legend(loc='upper right')  # 图例放置于右上角
ax2.grid(True)  # 画网格
# ax2.set_ylabel('成交量') # y轴名称

# 绘制MACD
if draw_macd:
    difs, deas, bars = matix[:, 6], matix[:, 7], matix[:, 8]  # 取出MACD值
    ax3.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
    ax3.plot(xdates, difs, c='w', label='DIFF')  # 绘制DIFF线
    ax3.plot(xdates, deas, c='y', label='DEA')  # 绘制DEA线
    # ax3.bar(xdates, df['bar'], width= 0.05, color=bar_colors) # 绘制成交量柱状图(发现用bar绘制，线的粗细不一致，故使用下面的直线列表)
    cmap = {True: mcolors.to_rgba('r', 1.0), False: mcolors.to_rgba('g', 1.0)}  # MACD线颜色，大于0为红色，小于0为绿色
    bar_colors = [cmap[bar > 0] for bar in bars]  # MACD线颜色列表
    vlines = [((date, 0), (date, bars[date])) for date in range(len(bars))]  # 生成MACD线顶点列表
    ax3.add_collection(
        LineCollection(vlines, colors=bar_colors, linewidths=0.5, antialiaseds=False))  # 生成MACD线的顶点数据(颜色，线宽，反锯齿)
    ax3.legend(loc='upper right')  # 图例放置于右上角
    ax3.grid(True)  # 画网格

# 绘制KDJ
if draw_kdj:
    K, D, J = matix[:, 9], matix[:, 10], matix[:, 11]  # 取出KDJ值
    ax4.axhline(0, ls='-', c='g', lw=0.5)  # 水平线
    ax4.yaxis.set_ticks_position('right')  # y轴显示在右边
    ax4.plot(xdates, K, c='y', label='K')  # 绘制K线
    ax4.plot(xdates, D, c='c', label='D')  # 绘制D线
    ax4.plot(xdates, J, c='m', label='J')  # 绘制J线
    ax4.legend(loc='upper right')  # 图例放置于右上角
    ax4.grid(True)  # 画网格

# set useblit = True on gtkagg for enhanced performance
from matplotlib.widgets import Cursor  # 处理鼠标

cursor = Cursor(ax1, useblit=True, color='w', linewidth=0.5, linestyle='--')

plt.show()