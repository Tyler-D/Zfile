#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pymongo.connection import MongoClient
import traceback
from aixie.settings

class BasePipeline(object):
    """save the data to mongodb.
    """
    def __init__(self):
        """The only async framework that PyMongo fully supports is Gevent.
        Currently there is no great way to use PyMongo in conjunction with
        Tornado or Twisted. PyMongo provides built-in connection pooling, so
        some of the benefits of those frameworks can be achieved just by
        writing multi-threaded code that shares a MongoClient.
        """

        try:
            client = MongoClient(settings['MONGODB_SERVER'],
            settings['MONGODB_PORT'])
            self.db = client[settings['MONGODB_DB']]
            self.coll = self.db[settings['MONGODB_DB_COLL']]
        except Exception as e:
            log.msg("connect to mongodb{%s:%d %s %s} error. %s" %
                    (settings['MONGODB_SERVER'], settings['MONGODB_PORT'],
                        settings['MONGODB_DB'], settings['MONGODB_DB_COLL'],
                        traceback.print_exc()), level=log.ERROR, spider=None)

    def count(self, query={}):
        if type(query) is not dict:
            return None

        return self.coll.find(query).count()

    def find(self, query={}):
        if type(query) is not dict:
            return None

        return self.coll.find(query)

    def find_data(self, query={}, data={}):
        if type(query) is not dict or type(data) is not dict:
            return None

        return self.coll.find(query, data)

    def insert(self, data):
        if type(data) is not dict:
            return

        result = self.coll.save(data)

    def remove(self, data={}):
        if type(data) is not dict:
            return

        result = self.coll.remove(data)

    def update_inc(self, data, incdata):
        if type(data) is not dict or type(incdata) is not dict:
            return

        self.coll.update(data, {'$inc': incdata})

    def update_set(self, data, setdata):
        if type(data) is not dict or type(setdata) is not dict:
            return

        self.coll.update(data, {'$set': setdata})
