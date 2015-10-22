#!/usr/bin/env python
# coding=utf-8

import os
import torndb
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado import escape
#setting
from tornado.options import define, options 

define("port", default=8888,help="run port",type=int)
define("mysql_host", default="127.0.0.1:3306", help="db host")  
define("mysql_database", default="Zfile", help="db name")  
define("mysql_user", default="root", help="db user")  
define("mysql_password", default="123", help="db password")

TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "templates")  
STATIC_PATH = os.path.join(os.path.dirname(__file__), "static") 

class BaseHandler(tornado.web.RequestHandler):
    def get_curret_user(self):
        return self.get_secure_cookie("user")
    def check_user(self):
        if not self.current_user:
            self.redirect("/login")
            return 
    def req_params(self):
        return tornado.input()
    def _print(self, page_name, base =None):
        pass

class MyRequestHandler(tornado.web.RequestHandler):
    def check_xsrf_cookie(self):
        pass
class HomeHandler(BaseHandler):
    def get(self):
        self.check_user()
        self.render("templates/index.html")

def user_auth(name, pw=None):
    db = torndb.Connection(
        host = options.mysql_host,
        database = options.mysql_database,
        user = options.mysql_user,
        password = options.mysql_password
        )
    user = db.get("select * from user where username=%s", name)
    if not pw:
        if user == None:
                return False
        return True
    else:
        if name==user[1]:
            if pw==user[2]:
                return True
            else:
                return False
        return False
#Account Action
class RegisterHandler(BaseHandler):
    def get(self):
        self.render("register.html")
    def post(self):
        db = self.application.db
        name = self.get_argument("username")
        pw = self.get_argument("password")
        res = user_auth(name)
        print("%s", res);
        if not res:
            sql = "INSERT INTO user(username, password)VALUES(%s,%s)"
            db.insert(sql, name, pw)
            self.set_secure_cookie("user", name)
            self.redirect("/disk")
        else:
            self.redirect("/register")

class LoginHandler(BaseHandler):
    def get(self):
       self.render() 
    def post(self):
        name = self.get_argument("username")
        pw = self.get_argument("password")
        res = user_auth(name,pw)

        if res :
            self.set_secure_cookie("user", name)
            self.redirect("/disk")
        else:
            self.redirect("/login")
'''        
#File Action
class FileHandler(BaseHandler):
    def __init__(self):

    def index(self):

    def upload(self):

    def download(self):

    def remove(self):
'''    
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
            (r"/register", RegisterHandler),
            (r"/login", LoginHandler),
        ]
        settings = dict(
            template_path = TEMPLATE_PATH,
            static_path = STATIC_PATH,
            debug = True,
            cookie_secret = "61oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo="
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

