# coding: utf-8

import pandas as pd
import numpy as np
import datetime,time
import os,sys
import re
import shutil
import logging
import collections as coll

##########################

columnlist=['date','start','highest','lowest','ending','tq','tm']

reshapescript = "format_one_file.sh"
datapath = './data'
tmppath = './tmp'
stockpoolini = 'stockpool.ini'

##########################

logger = logging.getLogger('stockanalyse.util')

class errcode:
    NOERR = 0
    NOT_DF_TYPE = 1

def _convertName(name):
    cmd = "ls {0}/*{1}*".format(datapath,name)
    ret = os.popen(cmd).read()
    namewithpath = ret.split('\n')[0]
    return namewithpath.split('/')[-1]

def _getStockPool():
    pool = []
    with open(stockpoolini) as f:
        for line in f:
            m = re.match(r"#\d+",line)
            if m:
                continue
            else:
                pool.append(_convertName(line.strip()))

    logger.info("get pool list OK")
    return pool

stockpool = _getStockPool()

def reshapeDataFile(file):
    cmd = "./{0} {1}".format(reshapescript,file)
    return os.system(cmd)

def getStockData(name):
    sourcefile = "{0}/{1}".format(datapath,name)
    targetfile = "{0}/{1}".format(tmppath,name)

    try:
        shutil.copy(sourcefile,targetfile)
    except IOError,e:
        logger.error("IOError when copy: [%d] [%s]"%(e.errno,e.strerror))
        return None

    val = reshapeDataFile(targetfile)
    # example : data = pd.read_table('SH#600198.txt',sep=',',names=['date','start','highest','lowest','ending','tq','tm'])
    data = None
    data = pd.read_table(targetfile,sep=',',names=columnlist)
    data['date'] = pd.to_datetime(data['date'])  # convert string to datetime series

    return data

def cleanTxt():
    cmd = "rm -f {0}/*.txt".format(tmppath)
    return os.system(cmd)

def vibrate(handle):
    if not isinstance(handle,pd.DataFrame):
        logger.error("handle is not the instance of pd.DataFrame")
        return False,errcode.NOT_DF_TYPE,None,None,None

    handle['vibrate'] = handle['highest'] - handle['lowest']
    thismean = np.mean(handle['vibrate'][-20:])
    max_vibrate = max(handle['vibrate'])
    max_vibrate_100 = max(handle['vibrate'][-100:])
    del handle['vibrate']
    return True,errcode.NOERR,max_vibrate,max_vibrate_100,thismean

def quantity(handle):
    if not isinstance(handle,pd.DataFrame):
        logger.error("handle is not the instance of pd.DataFrame")
        return False,errcode.NOT_DF_TYPE,None,None,None

    thismean = np.mean(handle['tq'][-20:])
    return True,errcode.NOERR,max(handle['tq']),max(handle['tq'][-100:]),thismean

def get_price(handle):
    if not isinstance(handle,pd.DataFrame):
        logger.error("handle is not the instance of pd.DataFrame")
        return False,errcode.NOT_DF_TYPE,None,None,None

    return True,errcode.NOERR,max(handle['ending']),max(handle['ending'][-100:]),handle.ix[-1]['ending']

def up_and_down(handle):
    if not isinstance(handle,pd.DataFrame):
        logger.error("handle is not the instance of pd.DataFrame")
        return False,errcode.NOT_DF_TYPE,None,None,None

    handle['updown'] = handle['ending'] - handle['start']
    handle_200 = handle[-200:]
    up_handle = handle_200[handle_200['updown']>0]
    down_handle = handle_200[handle_200['updown']<0]
    up_day,down_day,up_down = np.count_nonzero(up_handle['updown']),\
            np.count_nonzero(down_handle['updown']),\
            np.sum(up_handle['updown']) - np.abs(np.sum(down_handle['updown']))
    del handle['updown']
    return True,errcode.NOERR,up_day,down_day,up_down

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
def _calcMax(highest,lowest,yesterday):
    return max(abs(highest-lowest),max(abs(highest-yesterday),abs(lowest-yesterday)))

def _calcDayATR(df):
    return _calcMax(df['highest'],df['lowest'],df['yesterday'])

def calcATR(data,end_date=None,period=30):
    if end_date == None:
        return False

    ATRperiod = pd.date_range(end=end_date,periods=period+1,freq='B')
    dataslice = data[ATRperiod[0]:ATRperiod[-1]]
    dataslice['yesterday'] = dataslice['ending'].shift(1)
    #print dataslice
    dayATRlist = dataslice.apply(_calcDayATR,axis=1).dropna()
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
        monthATRlist = dataslice.apply(_calcDayATR,axis=1).dropna()

        meanATRlist.append(monthATRlist.mean())
        stdATRlist.append(monthATRlist.std())

    return meanATRlist,stdATRlist,rng
#end ATR function

def tosuggest(count):
    if ( count <= 5 ):
        return count
    elif ( 5 < count <= 25 ):
        return 5
    elif ( 25 < count <= 100 ):
        return count / 5
    else:
        return 20

def suggeststock(df,count,category=None):
    if category == None:
        return None,None

    if category == "vibrate":
        cols = ['vibrate_rate','vibrate_rate_100']
        df_op = df[cols]
        return df_op.sort_index(by='vibrate_rate_100')[:count].index,\
                df_op.sort_index(by='vibrate_rate_100')[:count]
    elif category == "quantity":
        cols = ['quantity_rate','quantity_rate_100']
        df_op = df[cols]
        return df_op.sort_index(by='quantity_rate_100')[:count].index,\
                df_op.sort_index(by='quantity_rate_100')[:count]
    elif category == "up_and_down":
        cols = ['up_day_200','down_day_200','up_and_down_200']
        df_op = df[cols]
        return df_op.sort_index(by='up_and_down_200')[:count].index,\
                df_op.sort_index(by='up_and_down_200')[:count]
    else:
        return None,None

def default_zero():
    return 0

def suggestsingle(*args):
    ret = coll.defaultdict(default_zero)
    for i in args:
        for single in i:
            ret[single] += 1

    return ret

def analyse_stock(handle,op_num):
    vibrate_list,vibrate_suggest = suggeststock(handle,op_num,"vibrate")
    logger.debug("vibrate:\n%s"%vibrate_suggest)
    quantity_list,quantity_suggest = suggeststock(handle,op_num,"quantity")
    logger.debug("quantity:\n%s"%quantity_suggest)
    up_and_down_list,up_and_down_suggest = suggeststock(handle,op_num,"up_and_down")
    logger.debug("up_and_down:\n%s"%up_and_down_suggest)
    ddict = suggestsingle(vibrate_list,quantity_list,up_and_down_list)
    logger.debug("suggest stock [high priority first] :\n%s" % sorted(ddict.items(),key=lambda item:item[1],reverse=True))

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
