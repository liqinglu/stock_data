# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import os,sys

from stockutil import stockpool,getStockData,cleanTxt

for stockfile in stockpool:
    basen = os.path.splitext(stockfile)[0]
    data = getStockData(stockfile)
    if data is None:
        print '%s is missing'%stockfile
        continue

    dataMA = data.set_index('date')
    dataMA = dataMA.resample('B').fillna(method='ffill')
    #only see MACD data in recent 180 days
    ema12 = pd.rolling_mean(dataMA.ending[-180:],12)
    ema26 = pd.rolling_mean(dataMA.ending[-180:],26)
    edif = ema12 - ema26
    edea = pd.rolling_mean(edif,9)
    macd_polar = 2 * (edif - edea)

    plt.figure(1)
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)
    plt.sca(ax1)
    edif.plot(color='r')
    edea.plot(color='g')
    plt.sca(ax2)
    macd_polar.plot(kind='bar',color='c')

    filename = basen + '_' + "MACD.png"
    #savefig(filename)
    plt.show()
    data,dataMA = None,None
    ema12,ema26,edif,edea,macd_polar = None,None,None,None,None

cleanTxt()
