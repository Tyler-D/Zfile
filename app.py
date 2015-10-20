#!/usr/bin/env python
# coding=utf-8

import os
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

#setting
from tornado.options import define, options 

define("port", defaut=8888,help="run port",type=int)
define("mysql_host", default="127.0.0.1:3306", help="db host")  
define("mysql_database", default="todo", help="db name")  
define("mysql_user", default="root", help="db user")  
define("mysql_password", default="", help="db password")

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")  
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static") 

class Application(tornado.web.Application):
    def __init__(self):
        '''
         handlers = [
            (r"/", IndexHandler),
            (r"/account/register", RegisterHandler)
            (r"/account/login", Login)
        ]
        '''
        handlers =[
            (r"/", IndexHandler),
        ]
        settings = dict(
            template_path = TEMPLATE_PATH,
            static_path = STATIC_PATH,
            debug = True
        )
        tornado.web.Application.__init__(self, handlers, **settings)
        self.db = torndb.Connection(
            host = options.mysql_host,
            database = options.mysql_database,
            user = options.mysql_user,
            password = options.mysql_password
        )
def main():
    tornado.options.parse_command_line()
    app = tornado.httpserver.HTTPServer(Application())
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()

