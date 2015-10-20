#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
python时间函数和常用格式化:http://canlynet.iteye.com/blog/1543184
python time, datetime, string, timestamp相互转换:http://blog.sina.com.cn/s/blog_b09d460201018o0v.html
Python模块学习 ---- datetime:http://blog.csdn.net/JGood/article/details/5457284
python time模块 格式化输出时间:http://blog.sina.com.cn/s/blog_6392417a0100gxxb.html
"""

import datetime
import time

# 格式：年－月－日 小时：分钟：秒
common_date = "%Y-%m-%d %H:%M:%S"
# 格式：年－月－日
long_date = "%Y-%m-%d"
# 格式：月－日
short_date = "%m-%d"
# 格式：年-月
year_date = "%Y-%m"
# 格式：小时：分钟：秒
long_time = "%H:%M:%S"

def str_to_date(string, fmt):
    """字符串转时间(datetime)
    """
    return datetime.datetime.strptime(string, fmt)

def date_to_str(dt, fmt):
    """时间(datetime)转字符串
    """
    return datetime.datetime.strftime(dt, fmt)

def time_sec_to_str(sec, fmt):
    """秒数(timestamp, float)转时间字符串
    """
    return time.strftime(fmt, time.localtime(sec))

def str_to_time_sec(string, fmt):
    """时间字符串转秒数(timestamp, float)
    """
    dt = datetime.datetime.strptime(string, fmt)
    time_sec = time.mktime(dt.timetuple())
    return time_sec

def get_default_date():
    """获取默认时间(datetime) 1970-01-01 00:00:00
    """
    return str_to_date("1970-01-01 00:00:00", common_date)

def get_current_date():
    """获取当前时间(datetime)
    """
    return datetime.datetime.now()

def main():
    """main
    """
    t = time.time()
    print time_sec_to_str(t, common_date)
    print str_to_time_sec("1970-01-01 00:00:00", common_date)
    print date_to_str(datetime.datetime.now(), common_date)
    print str_to_date("2010-10-12 00:00:12", common_date)
    print get_default_date()
    print get_current_date()

if __name__ == "__main__": main()
