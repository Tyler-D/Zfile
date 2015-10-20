#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

"""
文件名命名规则：

*   目录一定以 '/‘ 结尾
*   文件名不包含 './' 之类的前缀
"""

def list_all_files(dir):
    """递归遍历置顶目录，返回所有文件(不包含目录)
    """
    f_li = []
    for f in os.listdir(dir):
        filepath = join_path(dir, f)
        if os.path.isdir(filepath):
            f_li.extend(list_all_files(filepath))
        else:
            f_li.append(filepath)

    return f_li

def join_path(path, filename):
    """连接目录和文件
    """
    if not path.endswith('/'):
        path += '/'
    if filename.startswith('/'):
        filename = filename[1:]

    # 去除路径中多余的/, ./
    path += filename
    li = path.split('/')
    li2 = []
    li2.append(li[0])
    for x in li[1:]:
        if '' == x or '.' == x:
            continue
        li2.append(x)

    filepath = '/'.join(li2)
    if filepath.startswith('./'):
        return filepath[2:]

    return filepath

import math
def friend_size(size):
    size = int(size)
    if 0 == size:
        return '0'
    unit_name = ['B', 'KB', 'MB', 'GB', 'TB', 'PB', 'ZB', 'YB']
    i = int(math.floor(math.log(size, 1024)))
    return "%s%s" % (str(round(size / math.pow(1024, i), 2)), unit_name[i])
