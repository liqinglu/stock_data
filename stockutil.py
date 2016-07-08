# coding: utf-8

import pandas as pd
import numpy as np
import datetime,time
import os,sys
import shutil

##########################

columnlist=['date','start','highest','lowest','ending','tq','tm']

reshapescript = "format_one_file.sh"
datapath = './data'
stockpoolini = 'stockpool.ini'

##########################

def _convertName(name):
    cmd = "ls " + datapath + "/*" + name + "*"
    ret = os.popen(cmd).read()
    namewithpath = ret.split('\n')[0]
    return namewithpath.split('/')[-1]

def _getStockPool():
    pool = []
    with open(stockpoolini) as f:
        for line in f:
            pool.append(_convertName(line.strip()))

    return pool

stockpool = _getStockPool()

def reshapeDataFile(file):
    cmd = "./" + reshapescript + " " + file
    return os.system(cmd)

def getStockData(name):
    sourcefile = datapath + '/' + name

    try:
        shutil.copy(sourcefile,name)
    except IOError,e:
        print "Error: [%d] [%s]"%(e.errno,e.strerror)
        return None

    val = reshapeDataFile(name)
    data = pd.read_table(name,sep=',',names=columnlist)
    data['date'] = pd.to_datetime(data['date'])  # convert string to datetime series

    return data

def monthMeanValue(data,start_date=None,drange=None):
    meanValuelist = []
    rng = []
    if start_date == None:
        rng = pd.period_range(data.index[0],data.index[-1],freq='M')
    else:
        rng = pd.period_range(start_date,data.index[-1],freq='M')

    for eachmonth in rng:
        dataslice = data[str(eachmonth)]
        meanValuelist.append(dataslice['ending'].mean())

    return meanValuelist,rng

#ATR function
def calcMax(highest,lowest,yesterday):
    return max(abs(highest-lowest),max(abs(highest-yesterday),abs(lowest-yesterday)))

def calcDayATR(df):
    return calcMax(df['highest'],df['lowest'],df['yesterday'])

def calcATR(data,end_date=None,period=30):
    if end_date == None:
        return False

    ATRperiod = pd.date_range(end=end_date,periods=period+1,freq='B')
    dataslice = data[ATRperiod[0]:ATRperiod[-1]]
    dataslice['yesterday'] = dataslice['ending'].shift(1)
    #print dataslice
    dayATRlist = dataslice.apply(calcDayATR,axis=1).dropna()
    #print dayATRlist
    return dayATRlist.mean(),dayATRlist.std()

def monthATR(data,start_date=None):
    meanATRlist = []
    stdATRlist = []
    rng = []
    if start_date == None:
        rng = pd.period_range(data.index[0],data.index[-1],freq='M')
    else:
        rng = pd.period_range(start_date,data.index[-1],freq='M')
    for eachmonth in rng:
        dataslice = data[str(eachmonth)]
        dataslice['yesterday'] = dataslice['ending'].shift(1)
        monthATRlist = dataslice.apply(calcDayATR,axis=1).dropna()

        meanATRlist.append(monthATRlist.mean())
        stdATRlist.append(monthATRlist.std())

    return meanATRlist,stdATRlist,rng
#end ATR function

def datetime_offset_by_month(datetime1,n=1):
    q,r = divmod(datetime1.month + n,12)
    datetime2 = datetime.datetime(r and datetime1.year+q or datetime1.year+q-1, r and r or 12, 1)
    return datetime2

def str2date(datestr):
    t = time.strptime(datestr,"%Y-%m-%d")
    y,m,d = t[0:3]
    return datetime.datetime(y, m, d)

def date2str():
    pass

def test():
    file = "SH#600000.txt"
    print os.path.splitext(file)[0]
    print os.path.basename(file)

def test_datetime_offset_by_month():
    d1 = datetime.datetime(2007,11,1)
    d2 = datetime_offset_by_month(d1,1)
    print d2.year,d2.month
    d1 = datetime.datetime(2007,11,1)
    d2 = datetime_offset_by_month(d1,13)
    print d2.year,d2.month
    d1 = datetime.datetime(2007,11,1)
    d2 = datetime_offset_by_month(d1,14)
    print d2.year,d2.month

if __name__ == "__main__":
    #test()
    test_datetime_offset_by_month()
