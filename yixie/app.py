#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from aixie import settings

urls = (
    '([a-z0-9\/_]*)', 'ActionDispatcher'
    )

class ActionDispatcher(object):
    def __init__(self):
        pass

    def GET(self, uri):
        return self.process(uri, False)

    def POST(self, uri):
        return self.process(uri, True)

    def process(self, uri='', is_post=False):
        try:
            parts = uri.split('/')
            if len(parts) < 2:
                return

            #加载action类
            action_name = parts[1] if parts[1] else 'index'
            action_method_name = parts[2] if len(parts) > 2 and parts[2] else 'index'

            modules = __import__('controller')
            action_obj = getattr(modules, action_name.capitalize() + 'Action')()
            if hasattr(action_obj, action_method_name):
                return getattr(action_obj, action_method_name)()

            return web.notfound('404 Not Found.')
        except Exception, e:
            print 'except', e
            if e.message == '303 See Other':
                return
            return web.notfound('404 Not Found.')

def main():
    import conf
    conf.config_logger()
    import cgi
    # Maximum input we will accept when REQUEST_METHOD is POST
    # 0 ==> unlimited input
    # http://webpy.org/cookbook/limiting_upload_size.zh-cn
    #cgi.maxlen = 1024 * 1024 * 1024 # 1GB

    #web.webapi.internalerror = web.debugerror
    app = web.application(urls, globals())

    web.config.session_parameters['cookie_name'] = 'webpy_session_id'
    web.config.session_parameters['cookie_domain'] = None
    web.config.session_parameters['timeout'] = 86400, #24 * 60 * 60, # 24 hours   in seconds
    web.config.session_parameters['ignore_expiry'] = True
    web.config.session_parameters['ignore_change_ip'] = True
    web.config.session_parameters['secret_key'] = 'fLjUfxqXtfNoIldA0A0J'
    web.config.session_parameters['expired_message'] = 'Session expired'

    """
    issue: EOFError when loading empty session files
    https://github.com/webpy/webpy/issues/83


    webpy disk session file should not be an empty file, it's a pickle serialized object. So whenever EOF is encountered, it should be always because another thread is trying to write, thus truncating the size to zero.

    I've got a simple fix in session.py's DiskSession, change:

    def __getitem__(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            pickled = open(path).read()
            return self.decode(pickled)
        else:
            raise KeyError, key

    to:

    def __getitem__(self, key):
        path = self._get_path(key)
        if os.path.exists(path):
            while True:
                try:
                    pickled = open(path).read()
                    return self.decode(pickled)
                except EOFError:
                    time.sleep(0.1)
        else:
            raise KeyError, key

    It's a bit ugly. But since we are dealing with files with no concurrency support, this shall be as good as it gets. It helps to keep stuff simple without tapping into a full-fledged db like mysql too early, just for sessions.
    """
    if web.config.get('_session') is None:
        session = web.session.Session(app, web.session.DiskStore('sessions'),
                initializer={'token': None})
        web.config._session = session
    else:
        session = web.config._session
    # session 挂钩
    def session_hook():
        web.ctx.session = session
    app.add_processor(web.loadhook(session_hook))
    app.run()

if __name__ == "__main__": main()
