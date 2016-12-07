# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from pandas import Series,DataFrame
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from datetime import datetime
import os
import time
import logging
import logging.config
import collections as coll

logging.config.fileConfig('log.conf')
root_logger = logging.getLogger('root')
logger = logging.getLogger('stockanalyse')

#import stockutil
from stockutil import stockpool,getStockData,cleanTxt
from stockutil import vibrate,errcode,quantity,get_price,up_and_down

analyselist=['vibrate_rate','vibrate_rate_100','quantity_rate','quantity_rate_100',\
        'max_price','max_price_100','current_price','up_day_200','down_day_200',\
        'up_and_down_200']

def retkey(unknown):
    if isinstance(unknown,str):
        return os.path.splitext(unknown)[0][-6:]
    elif isinstance(unknown,list):
        changestockpool = []
        for stock in unknown:
            changestock = os.path.splitext(stock)[0][-6:]
            changestockpool.append(changestock)

        return changestockpool
    else:
        pass

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

logger.info("#####stock log start#####")

changed_stockpool = retkey(stockpool)
stock_analyse_res = pd.DataFrame(index=changed_stockpool,columns=analyselist)

start_time = time.time()
stock_count = 0
for stockfile in stockpool:
    basekey = retkey(stockfile)
    #logger.info("now handling stock code : %s"%basekey)
    data = getStockData(stockfile)
    if data is None or len(data.index) == 0:
        logger.warning("%s is missing" % stockfile)
        continue

    stock_count += 1
    data_handle = data.set_index('date')
    data_handle = data_handle.resample('B').fillna(method='ffill')

    #vibrate
    result,errcode,max_vibrate,max_vibrate_100,last_mean_20 = vibrate(data_handle)
    if result:
        #logger.info("vibrate : %s %s %s"%(max_vibrate,max_vibrate_100,last_mean_20))
        stock_analyse_res.loc[basekey,'vibrate_rate'] = last_mean_20/max_vibrate
        stock_analyse_res.loc[basekey,'vibrate_rate_100'] = last_mean_20/max_vibrate_100
    else:
        logger("error handle : %s when %s" % (stockfile,'execute vibrate'))

    #deal quantity
    result,errcode,max_quantity,max_quantity_100,last_mean_20 = quantity(data_handle)
    if result:
        #logger.info("quantity : %s %s %s"%(max_quantity,max_quantity_100,last_mean_20))
        stock_analyse_res.loc[basekey,'quantity_rate'] = last_mean_20/max_quantity
        stock_analyse_res.loc[basekey,'quantity_rate_100'] = last_mean_20/max_quantity_100
    else:
        logger.warning( "error handle : %s when %s" % (stockfile,'execute quantity') )

    #ending price
    result,errcode,max_price,max_price_100,current_price = get_price(data_handle)
    if result:
        #logger.info("price : %s %s %s"%(max_price,max_price_100,current_price))
        stock_analyse_res.loc[basekey,'max_price'] = max_price
        stock_analyse_res.loc[basekey,'max_price_100'] = max_price_100
        stock_analyse_res.loc[basekey,'current_price'] = current_price
    else:
        logger.warning( "error handle : %s when %s" % (stockfile,'execute get_price') )

    #up @vs down
    result,errcode,up_day_200,down_day_200,up_and_down_200 = up_and_down(data_handle)
    if result:
        #logger.info("up and down : %s %s %s"%(up_day_200,down_day_200,up_and_down_200))
        stock_analyse_res.loc[basekey,'up_day_200'] = up_day_200
        stock_analyse_res.loc[basekey,'down_day_200'] = down_day_200
        stock_analyse_res.loc[basekey,'up_and_down_200'] = up_and_down_200
    else:
        logger.warning("error handle : %s when %s" % (stockfile,'execute up_and_down'))

    data,data_handle = None,None

end_time = time.time()
logger.info("Duration : %s" % ( end_time - start_time ))

#logger.debug("stock_analyse_res:\n%s"%stock_analyse_res)
suggestion_count = tosuggest(stock_count)
logger.info("suggestion output has %s stocks" % suggestion_count )
vibrate_list,vibrate_suggest = suggeststock(stock_analyse_res,suggestion_count,"vibrate")
logger.debug("vibrate:\n%s"%vibrate_suggest)
quantity_list,quantity_suggest = suggeststock(stock_analyse_res,suggestion_count,"quantity")
logger.debug("quantity:\n%s"%quantity_suggest)
up_and_down_list,up_and_down_suggest = suggeststock(stock_analyse_res,suggestion_count,"up_and_down")
logger.debug("up_and_down:\n%s"%up_and_down_suggest)
ddict = suggestsingle(vibrate_list,quantity_list,up_and_down_list)
logger.debug("suggest stock [high priority first] :\n%s" % sorted(ddict.items(),key=lambda item:item[1],reverse=True))

cleanTxt()
logger.info("#####stock log ended#####")
