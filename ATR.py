# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import os,sys

from stockutil import stockpool
from stockutil import monthATR,calcATR
from stockutil import monthMeanValue
from stockutil import getStockData
from stockutil import cleanTxt

for stockfile in stockpool:
    basen = os.path.splitext(stockfile)[0]
    data = getStockData(stockfile)
    if data is None:
        continue

    '''
    querydate = '2011-01-31'
    queryperiod = 30
    meanATR,stdATR = calcATR(dataATR,querydate,queryperiod)
    print "2011-01"
    print "meanATR : %f"%meanATR
    print "stdATR  : %f"%stdATR
    '''
    dataATR = data.set_index('date')
    dataATR = dataATR.resample('B').fillna(method='ffill')
    #meanATR,stdATR,daterangeATR = monthATR(dataATR,"2011-01-04")
    #meanEnding,daterangeEnding = monthMeanValue(dataATR,"2011-01-04",daterangeATR)
    meanATR,stdATR,daterangeATR = monthATR(dataATR)
    meanEnding,daterangeEnding = monthMeanValue(dataATR,drange=daterangeATR)

    fig = plt.Figure()
    ax1 = plt.subplot(211)
    ax2 = plt.subplot(212)
    plt.sca(ax1)
    Series(meanATR,index=daterangeATR).plot(kind='bar',color='r')
    plt.sca(ax2)
    Series(meanEnding,index=daterangeEnding).plot(kind='bar',color='b')
    '''
    plt.show()
    '''
    filename = basen + '_' + "ATR_meanStockPrice.png"
    savefig(filename)

cleanTxt()
