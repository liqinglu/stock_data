# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import os,sys

from stockutil import stockpool
from stockutil import getStockData
from stockutil import cleanTxt

MAlist = [5,10,30,60]
MAcolor = ['w','y','m','c']

for stockfile in stockpool:
    basen = os.path.splitext(stockfile)[0]
    data = getStockData(stockfile)
    if data is None:
        print '%s is missing'%stockfile
        continue

    dataMA = data.set_index('date')
    dataMA = dataMA.resample('B').fillna(method='ffill')
    #only see MA data in recent one year
    dataMA.ending[-360:].plot(color='b')
    for days,usedcolor in zip(MAlist,MAcolor):
        pd.rolling_mean(dataMA.ending[-360:],days).plot(color=usedcolor)

    filename = basen + '_' + "MA_5_10_30_60.png"
    savefig(filename)
    '''
    plt.show()
    '''

    data,dataMA = None,None

cleanTxt()
