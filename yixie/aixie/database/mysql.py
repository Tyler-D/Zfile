#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
doc:http://mysql-python.sourceforge.net/MySQLdb.html
"""

import MySQLdb
import logging

log = logging.getLogger(__name__)

class MySQLDB(object):
    def __init__(self, host, user, passwd, charset="utf8"):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.charset = charset
        self._connect()

    def _connect(self):
        try:
            # 连接设置
            self.conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.passwd)
            # 设置编码
            self.conn.set_character_set(self.charset)
            # 获取游标
            self.cur = self.conn.cursor()
        except MySQLdb.Error, e:
            log.error("Mysql error %d: %s" % (e.args[0], e.args[1]))

    # 选择数据库
    def select_db(self, db_name):
        try:
            self.db_name = db_name
            self.conn.select_db(db_name)
        except MySQLdb.Error, e:
            log.error("Mysql error %d: %s" % (e.args[0], e.args[1]))

    def query(self, sql, *params):
        """#how to correctly do secured & scaped queries
        #http://stackoverflow.com/a/1307413
        """
        try:
            # 执行语句
            ret = self.cur.execute(sql, *params)
            return ret
        except (AttributeError, MySQLdb.OperationalError):
            log.info("mysql reconnect");
            # 2014 Error – Commands out of sync
            # http://eric.lubow.org/2009/python/pythons-mysqldb-2014-error-commands-out-of-sync/
            #self.close()
            # error 2013 lost connection to mysql server during query
            self._connect()
            self.select_db(self.db_name)
            # 执行语句
            ret = self.cur.execute(sql, *params)
            return ret
        except MySQLdb.Error, e:
            log.error("Mysql error %d: %s" % (e.args[0], e.args[1]))

    def query_row(self, sql):
        self.query(sql)
        ret = self.cur.fetchone()
        return ret[0]

    def query_all(self, sql):
        self.query(sql)
        ret = self.cur.fetchall()
        desc = self.cur.description
        d = []

        for inv in ret:
            _d = {}
            for i in range(0, len(inv)):
                _d[desc[i][0]] = str(inv[i])

            d.append(_d)
        return d

    def insert(self, table_name, data):
        for key in data:
            data[key] = "'" + str(data[key]) + "'"

        key = ','.join(data.keys())
        value = ','.join(data.values())

        sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"

        return self.query(sql)

    # 提交事务，否则不能真正的插入数据
    def commit(self):
        self.conn.commit()

    # 事务回滚
    def rollback(self):
        self.conn.rollback()

    # 关闭数据库连接，释放资源
    def close(self):
        self.cur.close()
        self.conn.close()

from MySQLdb.cursors import DictCursor
from DBUtils.PooledDB import PooledDB

class MySQLDB_(object):
    """MySQL 数据库对象，负责产生数据库连接 , 此类中的连接采用连接池实现
    获取连接对象: conn = MysqlPool._connect()
    释放连接对象: conn.close()
    http://my.oschina.net/zhouguanghu/blog/32422
    http://www.dbafree.net/?p=1125
    """
    # 连接池对象
    pool = None
    def __init__(self, host, user, passwd, db, charset="utf8"):
        """数据库构造函数，从连接池中取出连接，并生成操作游标
        """
        self.conn = MySQLDB_._connect(host, user, passwd, charset, db)
        self.cur = self.conn.cursor()

    @staticmethod
    def _connect(host, user, passwd, charset, db):
        """静态方法，从连接池中取出连接
        """
        if MySQLDB_.pool is None:
            pool = PooledDB(MySQLdb, host=host, user=user, passwd=passwd,
                    charset=charset, port=3306, db=db, mincached=1,
                    maxcached=20, maxshared=2, maxconnections=2)
        return pool.connection()

    def query(self, sql, *params):
        """#how to correctly do secured & scaped queries
        #http://stackoverflow.com/a/1307413
        """
        try:
            # 执行语句
            ret = self.cur.execute(sql, *params)
            return ret
        except (AttributeError, MySQLdb.OperationalError):
            log.error("mysql lose connection");
        except MySQLdb.Error, e:
            log.error("Mysql error %d: %s" % (e.args[0], e.args[1]))

    def query_row(self, sql):
        self.query(sql)
        ret = self.cur.fetchone()
        return ret[0]

    def query_all(self, sql):
        self.query(sql)
        ret = self.cur.fetchall()
        desc = self.cur.description
        d = []

        for inv in ret:
            _d = {}
            for i in range(0, len(inv)):
                _d[desc[i][0]] = str(inv[i])

            d.append(_d)
        return d

    def insert(self, table_name, data):
        for key in data:
            data[key] = "'" + str(data[key]) + "'"

        key = ','.join(data.keys())
        value = ','.join(data.values())

        sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"

        return self.query(sql)

    # 提交事务，否则不能真正的插入数据
    def commit(self):
        self.conn.commit()

    # 事务回滚
    def rollback(self):
        self.conn.rollback()

    # 关闭数据库连接，释放资源
    def close(self):
        self.cur.close()
        self.conn.close()


'''
if __name__ == "__main__":
    mysqlUtil = MySQLDB("localhost", "root", "uestc8020")
    mysqlUtil.select_db("test")
    #mysqlUtil.query("create table if not exists test1(name varchar(128) primary key, age int(4))")
    #mysqlUtil.insert("test1", {"name": "lisi", "age": 26})
    #sql = "insert into test1(name, age) values ('%s', %d)" % ("张三", 21)
    #mysqlUtil.query(sql)
    print mysqlUtil.query_row("select * from test1")
    mysqlUtil.commit()
    mysqlUtil.close()

if __name__ == "__main__":
    import config
    config.config_logger()
    mysqlUtil = MySQLDB("localhost", "root", "root")
    mysqlUtil.select_db("video_db")
    ret = mysqlUtil.query_row("select heat from bt where infohash='91f3657dfec65bd69bf27c5388ea9dadd23edf32'")
    print ret, type(ret)
    mysqlUtil.query("update bt set heat=10 wherenfohash='91f3657dfec65bd69bf27c5388ea9dadd23edf32'")
    mysqlUtil.commit()
    mysqlUtil.close()
'''
