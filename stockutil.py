# coding: utf-8

import datetime
import os

def datetime_offset_by_month(datetime1,n=1):
    q,r = divmod(datetime1.month + n,12)
    datetime2 = datetime.datetime(r and datetime1.year+q or datetime1.year+q-1, r and r or 12, 1)
    return datetime2

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
