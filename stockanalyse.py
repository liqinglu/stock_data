# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from stockutil import datetime_offset_by_month
from datetime import datetime
import os

stockfile = "SH#600000.txt"
basen = os.path.splitext(stockfile)[0]
data = pd.read_table(stockfile,sep=',',names=['date','start','highest','lowest','ending','tq','tm'])
data['date'] = pd.to_datetime(data['date'])  # convert string to datetime series
#print data

# highest tm/tq historically
# lowest tm/tq historically
# highest 'highest'-'lowest'
# lowest 'highest'-'lowest'
# period when 'ending' < 'ending'*1.2 , 'ending' == stocklowest
# period when 'ending' > 'ending'*0.9 , 'ending' == stockhighest
# how many peaks during this period
# tendency in past three months
# tendency in past one year
# how many days up/down in a year
# see tm/tq curve when 'ending' price is peak

# up/down group by month(monthview)
dataTT = data.set_index('date')
monthendingprice = []

rng = pd.period_range(dataTT.index[0],dataTT.index[-1],freq='M')
for currdate in rng:
    monthendingprice.append(dataTT[str(currdate)].ix[0,'ending'])
    monthendingprice.append(dataTT[str(currdate)].ix[-1,'ending'])

monthview = DataFrame(np.array(monthendingprice).reshape(len(rng),2),index=rng,columns=['begin','end'])
monthview['ratio'] = (monthview['end'] - monthview['begin'])/monthview['begin']
monthview['ratio'].plot(kind='bar')
savefile = basen + '_' + 'monthview.png'
savefig(savefile)

#dateindex = []
#beginyear = dataTT.index[0].year
#endyear = dataTT.index[-1].year
#beginmonth = dataTT.index[0].month
#endmonth = dataTT.index[-1].month
#rollingdate = datetime(beginyear,beginmonth,1)
#while True:
#    currdate = "%4d-%02d"%(rollingdate.year,rollingdate.month)
#    dateindex.append(currdate)
#    monthendingprice.append(dataTT[currdate].ix[0,'ending'])
#    monthendingprice.append(dataTT[currdate].ix[-1,'ending'])
#    if rollingdate.year == endyear and rollingdate.month == endmonth:
#        break
#    rollingdate = datetime_offset_by_month(rollingdate,1)
#monthview = DataFrame(np.array(monthendingprice).reshape(len(dateindex),2),index=np.array(dateindex),columns=['begin','end'])
#monthview['ratio'] = (monthview['end'] - monthview['begin'])/monthview['begin']
#monthview['ratio'].plot(kind='bar')
#savefile = basen + '_' + 'monthview.png'
#savefig(savefile)

# 年zhangdie(yearview)
dataTT = data.set_index('date')
dayendingprice = []
beginyear = dataTT.index[0].year
endyear = dataTT.index[-1].year
yearindex = np.arange(beginyear,endyear+1)
for year in yearindex:
    dayendingprice.append(dataTT[str(year)].ix[0,'ending'])
    dayendingprice.append(dataTT[str(year)].ix[-1,'ending'])

yearview = DataFrame(np.array(dayendingprice).reshape(len(yearindex),len(dayendingprice)/len(yearindex)),index=yearindex,columns=['begin','end'])
yearview['ratio'] = (yearview['end'] - yearview['begin'])/yearview['begin']
yearview['ratio'].plot(kind='bar')
savefile = basen + '_' + 'yearview.png'
savefig(savefile)

# 历史最高价
#stockhighest = data['ending'].max()

# 历史最低价
#stocklowest = data['ending'].min()

# 收盘价的曲线
dataTT = data.set_index('date')
dataTT['ending'].plot()
savefile = basen + '_' + 'histprice.png'
savefig(savefile)

# 收盘价和成交额的曲线
dataTT = data.set_index('date')
dataTT[['ending','tm']].plot(subplots=True)
#histpriceandtm = data[['ending','tm']]
#histpriceandtm.set_index(data['date'])
#histpriceandtm.plot(subplots=True)
savefile = basen + '_' + 'histpriceandtm.png'
savefig(savefile)
