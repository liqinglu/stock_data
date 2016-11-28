# -*- coding: utf-8 -*-
'''
2. handle stock_analyse_res
'''

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

logging.config.fileConfig('log.conf')
root_logger = logging.getLogger('root')
logger = logging.getLogger('stockanalyse')

#import stockutil
from stockutil import stockpool,getStockData,cleanTxt
from stockutil import vibrate,errcode,quantity,get_price,up_and_down

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

logger.info("stock log start ...")

analyselist=['vibrate_rate','vibrate_rate_100','quantity_rate','quantity_rate_100',\
        'max_price','max_price_100','current_price','up_day_200','down_day_200',\
        'up_and_down_200']
changed_stockpool = retkey(stockpool)
stock_analyse_res = pd.DataFrame(index=changed_stockpool,columns=analyselist)

start_time = time.time()
for stockfile in stockpool:
    basekey = retkey(stockfile)
    #logger.info("now handling stock code : %s"%basekey)
    data = getStockData(stockfile)
    if data is None or len(data.index) == 0:
        logger.warning("%s is missing" % stockfile)
        continue
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
cleanTxt()
logger.info(stock_analyse_res)
logger.info("Duration : %s" % ( end_time - start_time ))
logger.info("stock log ended ...")
