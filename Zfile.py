#!/usr/bin/env python
# coding=utf-8

import os
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import simplejson
from tornado import escape
#setting
from tornado.options import define, options 

define("port", defaut=8888,help="run port",type=int)
define("mysql_host", default="127.0.0.1:3306", help="db host")  
define("mysql_database", default="user", help="db name")  
define("mysql_user", default="root", help="db user")  
define("mysql_password", default="", help="db password")

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")  
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static") 

class BaseHandler(tornado.web.RequestHandler):
    resp = None
    def get_curret_user(self):
        return self.get_secure_cookie("user")
    def check_user(self):
        if not self.current_user:
            self.redirect("/account/login")
            return 
    def req_params(self):
        return tornado.input()
    def _print(self, page_name, base =None):
        pass
    def json(self):
        self.db.close()
        return simplejson.dumps(self.resp)

class MyRequestHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass
class HomeHandler(BaseHandler):
    def get(self):
        self.check_user()
        self.render("static/index.html")
#Account Action
class AccountHandler(BaseHandler):
    def login(self):

    def login_auth(self):

    def log_out(self):

    def register(self):

#File Action
class FileHandler(BaseHandler):
    def __init__(self):

    def index(self):

    def upload(self):

    def download(self):

    def remove(self):
    
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
            (r"/", HomeHandler),
            (r"/account/(.*)", AccountHandler),
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

