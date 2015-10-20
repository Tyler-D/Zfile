#!/usr/bin/env python
# -*- coding: utf-8 -*-

import web
from aixie import settings
from aixie.database.mysql import MySQLDB_
import simplejson

# 枚举简洁的表示方法
(errno_ok, errno_notfound, errno_db, errno_client, errno_auth, errno_exist, errno_file_too_large, errno_form, errno_limit) = range(9)
(user_normal, user_admin) = range(2)
(state_inactive, state_activate, state_remove) = range(3)
user_state_name = ['未激活', '激活', '删除']

class BaseAction(object):
    resp = None
    template_dir = settings['TEMPLATE_DIR']
    theme_dir = settings['TEMPLATE_THEME_DIR']
    def __init__(self):
        self.db = MySQLDB_(settings['MYSQL_HOST'], settings['MYSQL_USER'],
                settings['MYSQL_PASSWD'], settings['MYSQL_DB'])

    def get(self):
        return web.ctx.method == 'GET'

    def req_params(self):
        return web.input()

    def session(self):
        return web.ctx.session

    def redirect(self, uri):
        '''301
        '''
        self.db.close()
        raise web.seeother(uri)

    def notfound(self):
        self.db.close()
        return web.notfound('404 Not Found.')

    def _print(self, page_name, base=None):
        """显示模板
        """
        if base:
            render = web.template.render(fileutil.join_path(self.template_dir, self.theme_dir),
                base=base)
        else:
            render = web.template.render(fileutil.join_path(self.template_dir, self.theme_dir))
        self.db.close()
        return getattr(render, page_name)(self.resp)

    def error(self):
        '''出错
        '''
        self.db.close()
        return self._print('error')

    def json(self):
        """response json
        从webpy返回json被chrome认为是错误的
        http://www.douban.com/group/topic/32487954/
        """
        self.db.close()
        return simplejson.dumps(self.resp)

    def xml(self, xml_name):
        """response xml
        提供XML访问
        http://webpy.org/cookbook/xmlfiles.zh-cn
        """
        web.header('Content-Type', 'text/xml')
        self.db.close()
        return self._print(xml_name)

class TestAction(BaseAction):
    def __init__(self):
        BaseAction.__init__(self)

    def index(self):
        pass
        #return self._print('test')
        self.redirect('/test/test')
        #return self.notfound()
        #return self.error()
        #self.resp = {'a': 1}
        #return self.json()
        #return self.xml('x')

    def test(self):
        return self.xml('x')

import os
import os.path
import time
import shutil
from web import form
from aixie import settings
from aixie.utils import auth
from aixie.utils import timeutil
from aixie.utils import fileutil
from aixie.web import page

BUF_SIZE = 1000
user_passwd_salt = 'yixie.com'
default_passwd = '111111'
default_total_quota = 1024 * 1024 * 1024 # 1G
max_total_quota = 20 * 1024 * 1024 * 1024 # 20G
token_lifetime = 30 * 60 * 1000000 # 30分钟
# 分页大小
fs_page_size = 2
user_page_size = 2

def is_user():
    token = web.ctx.session.token
    if not token:
        return False

    if not auth.is_token_expired(token, token_lifetime):
        return False

    return True

def is_admin():
    if not is_user():
        return False

    token = web.ctx.session.token
    userid = auth.decode_token(token)['userid']
    db = MySQLDB_(settings['MYSQL_HOST'], settings['MYSQL_USER'],
            settings['MYSQL_PASSWD'], settings['MYSQL_DB'])
    user_li = db.query_all("select * from user where `id`='%s'" % userid)
    db.close()

    if 0 == len(user_li):
        return False

    if int(user_li[0]['level']) != user_admin:
        return False

    return True

def user_unique(obj, name, email):
    user_li = obj.db.query_all("""select id from user where name='%s'""" % (name))
    if len(user_li) > 0:
        obj.resp = {'errno': errno_form, 'msg': '用户名已存在'}
        return False

    user_li = obj.db.query_all("""select id from user where email='%s'"""
            % (email))
    if len(user_li) > 0:
        obj.resp = {'errno': errno_form, 'msg': '邮箱已存在'}
        return False

    return True

class UserFilterAction(BaseAction):
    def __init__(self):
        super(UserFilterAction, self).__init__()

        if not is_user():
            self.redirect('/account/login')

class AdminFilterAction(BaseAction):
    def __init__(self):
        super(AdminFilterAction, self).__init__()

        if not is_admin():
            self.redirect('/disk/')

        """setting server side dir"""
        homedir = os.getcwd()
        self.filedir = '%s/static/upload/' % (homedir)

class DiskAction(UserFilterAction):
    """文件操作
    """
    vnotnullname = form.Validator("文件夹名不能为空", lambda x: 0 !=
            len(x.strip()))
    vnotnullpath = form.Validator("违规操作", lambda x: 0 != len(x.strip()))
    # 正则匹配不包含某字符串
    # http://blog.csdn.net/maqingli20/article/details/7317925
    # http://www.redicecn.com/html/Python/20111230/359.html
    vxname = form.regexp(r"^(?!.*?(\.|\?|/)).*$", "文件名不能包含特殊字符(/, ., ?)")
    vname = form.regexp(r".{1,255}$", "文件夹名格式出错(1-255字符)")
    def __init__(self):
        super(DiskAction, self).__init__()

        """setting server side dir"""
        homedir = os.getcwd()
        token = web.ctx.session.token
        userid = auth.decode_token(token)['userid']
        quota_li = self.db.query_all("select fs_path from quota where user_id='%s'" % (userid))
        if 0 == len(quota_li):
            self.redirect('error')
        self.userdir = quota_li[0]['fs_path']
        self.filedir = '%s/static/upload/%s' % (homedir, self.userdir)

    def index(self):
        """默认项
        """
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        return self._print('disk', 'layout')

    def upload(self):
        """上传文件，并保存
        http://webpy.org/cookbook/fileupload.zh-cn
        http://webpy.org/cookbook/storeupload.zh-cn
        http://outofmemory.cn/code-snippet/3286/webpy-upload-file
        """
        try:
            x = web.input(disk={})
        except ValueError:
            self.resp = {'errno': errno_file_too_large, 'msg': e.message}
            return self.json()

        params = self.req_params()
        path = params.path

        if 'disk' in x:
            filepath = x.disk.filename.replace('\\', '/')
            if not filepath:
                self.resp = {'errno': 1, 'msg': '请选择文件'}
                return self.json()
            filename = filepath.split('/')[-1]
            # 获取文件大小
            # https://groups.google.com/forum/#!topic/webpy/si190XseR30
            size = int(web.ctx.env['CONTENT_LENGTH'])
            token = web.ctx.session.token
            userid = auth.decode_token(token)['userid']

            quota_li = self.db.query_all("""select used, total, fs_path from quota where user_id='%s'"""
                    % (userid))
            if 0 == len(quota_li):
                self.redirect('error')

            if size + int(quota_li[0]['used']) > int(quota_li[0]['total']):
                self.resp = {'errno': errno_file_too_large, 'msg': '您的存在空间不足'}
                return self.json()

            f = open(fileutil.join_path(fileutil.join_path(self.filedir, path), filename), 'w')
            f.write(x.disk.file.read())
            f.close()
            userdir = quota_li[0]['fs_path']
            size = os.path.getsize(fileutil.join_path(fileutil.join_path(self.filedir,
                path), filename))
            used = int(quota_li[0]['used']) + size
            filepath = fileutil.join_path(fileutil.join_path(userdir, path), filename)
            # 更新存储容量
            self.db.query("""update quota set used='%d' where user_id='%s'""" %
                    (used, userid))
            self.db.query("insert into file_system (name, path, size, create_time, user_id) values('%s', '%s', '%s', '%s', '%s')" % (filename,
                        filepath, size, timeutil.get_current_date(), userid));
            self.db.commit()
            self.resp = {'errno': 0, 'msg': '上传成功'}

        return self.json()

    def add(self):
        """新建文件夹
        """
        params = self.req_params()
        # 格式验证
        add_form = form.Form(
                form.Textbox('path', self.vnotnullpath),
                form.Textbox('name', self.vnotnullname, self.vxname, self.vname),
                )
        f = add_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        path, name = params.path, params.name
        filepath = fileutil.join_path(self.filedir, path)

        if not os.path.exists(filepath):
            self.resp = {'errno': errno_exist, 'msg': '路径不存在'}
            return self.json()

        filepath = fileutil.join_path(filepath, name)
        if os.path.exists(filepath):
            self.resp = {'errno': errno_exist, 'msg': '文件夹已存在'}
            return self.json()

        os.mkdir(filepath)
        self.resp = {'errno': errno_ok, 'msg': '新建文件夹完成'}
        return self.json()

    def download(self):
        """下载文件
        http://simple-is-better.com/news/632
        http://outofmemory.cn/code-snippet/1308/webpy-xiazai-file
        """
        params = self.req_params()
        path = params.path
        filepath = fileutil.join_path(self.filedir, path)
        filename = filepath.split('/')[-1]
        f = None
        try:
            f = open(filepath, "rb")
            web.header('Content-Type','application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s' % filename)
            while True:
                c = f.read(BUF_SIZE)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error', e.message
        finally:
            if f:
                f.close()

    def list(self):
        params = self.req_params()
        path = params.path
        filepath = fileutil.join_path(self.filedir, path)
        try:
            files = os.listdir(filepath)
        except OSError, e:
            self.resp = {'errno': errno_client, 'msg': '路径不存在'}
            return self.json()

        self.resp = {}
        self.resp['errno'] = errno_ok
        self.resp['label'] = '所有文件'
        self.resp['path'] = path
        self.resp['list'] = []
        for filename in files:
            file_info = {}
            file_info['server_filename'] = filename
            fpath = fileutil.join_path(filepath, filename)
            file_info['size'] = fileutil.friend_size(os.path.getsize(fpath))
            file_info['path'] = fileutil.join_path(path, filename)
            file_info['isdir'] = 1 if os.path.isdir(fpath) else 0
            file_info['server_ctime'] = timeutil.time_sec_to_str(os.path.getctime(fpath), timeutil.common_date)
            file_info['server_mtime'] = timeutil.time_sec_to_str(os.path.getmtime(fpath), timeutil.common_date)
            if file_info['isdir']:
                file_info['dir_empty'] = 0 if os.listdir(fpath) else 1
            file_info['fs_id'] = 0
            file_info['category'] = 0
            self.resp['list'].append(file_info)

        return self.json()

    def remove(self):
        """删除文件(非目录)
        """
        params = self.req_params()
        path = params.path
        filepath = fileutil.join_path(self.filedir, params.path)
        token = web.ctx.session.token
        userid = auth.decode_token(token)['userid']

        quota_li = self.db.query_all("""select used, total, fs_path from quota where user_id='%s'"""
                % (userid))

        if 0 == len(quota_li):
            self.redirect('error')

        used = int(quota_li[0]['used'])

        if os.path.isdir(filepath):
            try:
                f_li = fileutil.list_all_files(filepath)
                # http://www.cnblogs.com/xiaowuyi/archive/2012/05/04/2482113.html
                # 删除非空目录
                shutil.rmtree(filepath)
                #os.rmdir(filepath)
                for f in f_li:
                    filepath = fileutil.join_path(self.userdir, f[len(self.filedir):])
                    used -= self._get_fs_size(filepath, userid)
                    self.db.query("delete from file_system where path='%s' and user_id='%s'" %
                            (filepath, userid))

                # 更新存储容量
                self.db.query("""update quota set used='%d' where user_id='%s'""" %
                        (used, userid))
                self.db.commit()
            except OSError, e:
                print 'e.message', e.message
                self.resp = {'errno': errno_notfound, 'msg': '目录不存在'}
                self.db.rollback()
                return self.json()
            self.resp = {'errno': errno_ok, 'msg': '目录删除完成'}
            return self.json()

        try:
            # 删除文件
            os.remove(filepath)
        except OSError, e:
            self.resp = {'errno': errno_notfound, 'msg': '文件不存在'}
            return self.json()

        filepath = fileutil.join_path(self.userdir, path)
        used -= self._get_fs_size(filepath, userid)
        self.db.query("delete from file_system where path='%s' and user_id='%s'" %
                (filepath, userid))
        # 更新存储容量
        self.db.query("""update quota set used='%d' where user_id='%s'""" %
                (used, userid))
        self.db.commit()
        self.resp = {'errno': errno_ok, 'msg': '删除完成'}
        return self.json()

    def _get_fs_size(self, path, userid):
        fs_li = self.db.query_all("""select size from file_system where path='%s' and user_id='%s'"""
                % (path, userid))
        if 0 == len(fs_li):
            self.redirect('error')
        return int(fs_li[0]['size'])

class FileAction(AdminFilterAction):
    def __init__(self):
        super(FileAction, self).__init__()

    def index(self):
        """默认项
        """
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        return self._print('file', 'layout')

    def list(self):
        """查看文件列表
        """
        params = self.req_params()
        page_no = int(params.pn) if params.pn else 1

        try:
            userid = params.id
            total = self.db.query_row("""select count(*) from file_system where user_id='%s'""" % (userid));
            pg = page.Page(total, page_no, fs_page_size)
            fs_li = self.db.query_all("""select file_system.name as name, file_system.path
                    as path, file_system.size as size, file_system.create_time as
                    create_time, user.id as userid, user.name as username from file_system, user where file_system.user_id=user.id and user.id='%s' limit %d,
                    %d""" % (userid, (pg.current - 1) * fs_page_size, fs_page_size))

        except Exception, e:
            total = self.db.query_row("select count(*) from file_system");
            pg = page.Page(total, page_no, fs_page_size)
            fs_li = self.db.query_all("""select file_system.name as name, file_system.path
                    as path, file_system.size as size, file_system.create_time as
                    create_time, user.id as userid, user.name as username from file_system, user where file_system.user_id=user.id limit %d,
                    %d""" % ((pg.current - 1) * fs_page_size, fs_page_size))

        self.db.commit()
        for f in fs_li:
            f_idx = fs_li.index(f)
            fs_li[f_idx]['size'] = fileutil.friend_size(f['size'])
        self.resp = {'errno': errno_ok, 'list': fs_li}
        # http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        # http://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        # http://stackoverflow.com/questions/4014621/a-python-class-that-acts-like-dict
        self.resp.update(pg.__dict__)
        return self.json()

    def remove(self):
        """删除文件
        """
        params = self.req_params()
        path = params.path
        filepath = fileutil.join_path(self.filedir, path)

        if os.path.isdir(filepath):
            self.resp = {'errno': errno_client, 'msg': '无法删除目录'}
            return self.json()

        try:
            os.remove(filepath)
        except OSError, e:
            self.resp = {'errno': errno_notfound, 'msg': '文件不存在'}
            return self.json()

        self.db.query("delete from file_system where path='%s'" % (path))
        self.db.commit()
        self.resp = {'errno': errno_ok, 'msg': '删除完成'}
        return self.json()

    def download(self):
        """下载文件
        """
        params = self.req_params()
        filepath = fileutil.join_path(self.filedir, params.path)
        filename = filepath.split('/')[-1]
        f = None
        try:
            f = open(filepath, "rb")
            web.header('Content-Type','application/octet-stream')
            web.header('Content-disposition', 'attachment; filename=%s' % filename)
            while True:
                c = f.read(BUF_SIZE)
                if c:
                    yield c
                else:
                    break
        except Exception, e:
            print e
            yield 'Error', e.message
        finally:
            if f:
                f.close()

class AccountAction(BaseAction):
    vnotnullaccount = form.Validator("账户(用户名/邮箱)为空", lambda x: 0 != len(x.strip()))
    vnotnullname = form.Validator("用户名为空", lambda x: 0 != len(x.strip()))
    vnotnullemail = form.Validator("邮箱为空", lambda x: 0 != len(x.strip()))
    vnotnullpassword = form.Validator("密码为空", lambda x: 0 != len(x.strip()))
    vaccount = form.regexp(r".{4,30}$", "用户名或邮箱出错")
    vname = form.regexp(r"[a-zA-Z0-9]{4,20}", "用户名错误(4-20个字符[字母, 数字])")
    vemail = form.regexp(r".*@.*", "邮箱格式错误")
    vpassword = form.regexp(r".{6,30}$", "密码错误(6-30个字符)")
    vcmppassword = form.Validator("两次密码输入不一致", lambda x: x.password ==
            x.repeat_password)

    def __init__(self):
        super(AccountAction, self).__init__()

    def login(self):
        """登录页面
        """
        if is_user():
            self.redirect('/disk/')
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        return self._print('login', 'layout')

    def login_auth(self):
        """登录认证
        """
        params = self.req_params()
        # 字段信息验证
        login_auth_form = form.Form(
                form.Textbox('account', self.vnotnullaccount, self.vaccount),
                form.Password('password', self.vnotnullpassword, self.vpassword),
                )
        f = login_auth_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        account, password = params.account, params.password
        user_li = self.db.query_all("select * from user where `name`='%s' and `password`='%s'" % (account, auth.get_hashed_password(password, user_passwd_salt)))
        self.db.commit()

        if 0 == len(user_li):
            user_li = self.db.query_all("select * from user where `email`='%s' and `password`='%s'" % (account, auth.get_hashed_password(password, user_passwd_salt)))
            self.db.commit()

        if 0 == len(user_li):
            self.resp = {'errno': errno_auth, 'msg': '用户名或密码错误'}
            return self.json()

        if int(user_li[0]['state']) == state_inactive:
            self.resp = {'errno': errno_auth, 'msg': '未激活'}
            return self.json()

        web.ctx.session.token = auth.create_token(user_li[0]['id'])
        self.resp = {'errno': errno_ok, 'msg': '登录完成'}
        return self.json()

    def logout(self):
        """退出
        """
        web.ctx.session.token = None
        self.redirect('/account/login')

    def register(self):
        """注册
        """
        # 字段信息验证
        register_form = form.Form(
                form.Textbox('name', self.vnotnullname, self.vname),
                form.Textbox('email', self.vnotnullemail, self.vemail),
                form.Password('password', self.vnotnullpassword, self.vpassword),
                validators = [
                    self.vcmppassword,
                    ]
                )
        f = register_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        params = self.req_params()
        name, email, password = params.name, params.email, params.password

        if not user_unique(self, name, email):
            return self.json()

        self.db.query("""insert into user (`name`, `email`, `password`, `create_time`, `last_login_time`) values('%s', '%s', '%s', '%s', '%s')""" % (name, email,
                    auth.get_hashed_password(password, user_passwd_salt),
                    timeutil.get_current_date(), timeutil.get_current_date()))
        user_li = self.db.query_all("""select id from user where name='%s'""" % (name))
        if 0 == len(user_li):
            self.resp = {'errno': errno_db, 'msg': '数据库操作失败'}
            return self.json()
        fs_path = user_li[0]['id'] + '/'
        print 'fs_path', fs_path
        self.db.query("""insert into quota (total, create_time, fs_path,
                user_id) values('%s', '%s', '%s', '%s')""" %
                (default_total_quota, timeutil.get_current_date(), fs_path,
                user_li[0]['id']))

        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '注册完成'}
        return self.json()

class UserAction(AdminFilterAction):
    """用户
    """
    vnotnullname = form.Validator("用户名为空", lambda x: 0 != len(x.strip()))
    vnotnullemail = form.Validator("邮箱为空", lambda x: 0 != len(x.strip()))
    vname = form.regexp(r"[a-zA-Z0-9]{4,20}", "用户名错误(4-20个字符[字母, 数字])")
    vemail = form.regexp(r".*@.*", "邮箱格式错误")

    def __init__(self):
        super(UserAction, self).__init__()

    def index(self):
        """默认项
        """
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        return self._print('user', 'layout');

    def get(self):
        """账号信息
        """
        params = self.req_params()
        userid = params.id
        user_li = self.db.query_all("select `id`, `name`, `email`, state from user where `id`='%s'" % (userid))
        self.db.commit()
        if 0 == len(user_li):
            self.resp = {'errno': errno_db, 'msg': '用户不存在'}
            return self.json()
        self.resp = {'errno': errno_ok}
        user_li[0]['state'] = user_state_name[int(user_li[0]['state'])]
        self.resp.update(user_li[0])
        return self.json()

    def add(self):
        """添加用户
        """
        # 字段信息验证
        add_form = form.Form(
                form.Textbox('name', self.vnotnullname, self.vname),
                form.Textbox('email', self.vnotnullemail, self.vemail),
                )
        f = add_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        params = self.req_params()
        name, email = params.name, params.email

        if not user_unique(self, name, email):
            return self.json()

        self.db.query("""insert into user (`email`, `name`, `password`, `create_time`,
                `last_login_time`) values('%s', '%s', '%s', '%s', '%s')""" % (email, name,
                    auth.get_hashed_password(default_passwd, user_passwd_salt),
                    timeutil.get_current_date(),
                timeutil.get_current_date()))
        user_li = self.db.query_all("""select id from user where name='%s'""" % (name))
        if 0 == len(user_li):
            self.resp = {'errno': errno_db, 'msg': '数据库操作失败'}
            return self.json()
        fs_path = user_li[0]['id'] + '/'
        print 'fs_path', fs_path
        self.db.query("""insert into quota (total, create_time, fs_path,
                user_id) values('%s', '%s', '%s', '%s')""" %
                (default_total_quota, timeutil.get_current_date(), fs_path,
                user_li[0]['id']))
        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '添加用户完成'}
        return self.json()

    def list(self):
        """查看用户
        """
        params = self.req_params()
        page_no = int(params.pn) if params.pn else 1
        total = self.db.query_row("""select count(user.id) from user, quota where
                user.id=quota.user_id and user.level='%d'""" % (user_normal));
        pg = page.Page(total, page_no, user_page_size)

        user_li = self.db.query_all("""select user.id as id, user.name as name,
                user.email as email, user.state as state,
                user.create_time as create_time,
                user.last_login_time as last_login_time,
                quota.total as total, quota.used as used from user,
                quota where user.id=quota.user_id and user.level='%d' limit %d, %d""" %
                (user_normal, (pg.current - 1) * user_page_size, user_page_size))
        if len(user_li) > 0:
            for u in user_li:
                u_idx = user_li.index(u)
                user_li[u_idx]['file_num'] = self.db.query_row("select count(*) from file_system where file_system.user_id='%s'" % (u['id']))
                user_li[u_idx]['total'] = fileutil.friend_size(user_li[u_idx]['total'])
                user_li[u_idx]['used'] = fileutil.friend_size(user_li[u_idx]['used'])
                user_li[u_idx]['state'] = user_state_name[int(user_li[u_idx]['state'])]

        self.db.commit()
        self.resp = {'errno': errno_ok, 'list': user_li}
        self.resp.update(pg.__dict__)
        return self.json()

    def active(self):
        """审核通过，激活
        """
        params = self.req_params()
        userid = params.id
        quota_li = self.db.query_all("""select fs_path from quota where user_id='%s'""" %
                (userid))
        self.db.query("""update user set state='%d' where id='%s'""" % (state_activate, userid))
        self.db.commit()

        filepath = fileutil.join_path(self.filedir, quota_li[0]['fs_path'])
        os.mkdir(filepath)

        self.resp = {'errno': errno_ok, 'msg': '激活完成'}
        return self.json()

    def remove(self):
        """删除
        """
        params = self.req_params()
        userid = params.id
        self.db.query("update user set state='%d' where id='%s'" %
                (state_remove, userid))
        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '删除用户完成'}
        return self.json()

    def reset(self):
        """重置密码
        """
        params = self.req_params()
        userid = params.id

        self.db.query("""update user set password='%s' where id='%s'""" %
                (auth.get_hashed_password(default_passwd, user_passwd_salt),
                    userid))
        self.db.commit()
        self.resp = {'errno': errno_ok, 'msg': '重置完成'}
        return self.json()

    def u(self):
        """单个用户详细信息
        """
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        params = self.req_params()
        self.resp['userid'] = params.id

        return self._print('u', 'layout')

class SettingsAction(UserFilterAction):
    vnotnullname = form.Validator("用户名为空", lambda x: 0 != len(x.strip()))
    vnotnullemail = form.Validator("邮箱为空", lambda x: 0 != len(x.strip()))
    vnotnullpassword = form.Validator("密码为空", lambda x: 0 != len(x.strip()))
    vaccount = form.regexp(r".{4,30}$", "用户名或邮箱出错")
    vname = form.regexp(r"[a-zA-Z0-9]{4,20}", "用户名错误(4-20个字符[字母, 数字])")
    vemail = form.regexp(r".*@.*", "邮箱格式错误")
    vpassword = form.regexp(r".{6,30}$", "密码错误(6-30个字符)")
    vcmppassword = form.Validator("两次密码输入不一致", lambda x: x.new_password ==
            x.repeat_password)

    def __init__(self):
        super(SettingsAction, self).__init__()

    def index(self):
        """默认页
        """
        self.resp = {}
        if is_admin():
            self.resp['userlevel'] = user_admin
        elif is_user():
            self.resp['userlevel'] = user_normal
        else:
            self.resp['userlevel'] = -1

        return self._print('settings', 'layout');

    def account(self):
        """设置(邮箱、姓名)
        """
        token = web.ctx.session.token
        userid = auth.decode_token(token)['userid']
        if self.get():
            # 账号信息
            user_li = self.db.query_all("select `id`, `name`, `email` from user where `id`='%s'" % (userid))
            self.db.commit()
            if 0 == len(user_li):
                self.resp = {'errno': errno_db, 'msg': '用户不存在'}
                return self.json()
            self.resp = {'errno': errno_ok}
            self.resp.update(user_li[0])
            return self.json()

        params = self.req_params()
        # 字段信息验证
        account_form = form.Form(
                form.Textbox('name', self.vnotnullname, self.vname),
                form.Textbox('email', self.vnotnullemail, self.vemail),
                )
        f = account_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        email, name = params.email, params.name

        if not user_unique(self, name, email):
            return self.json()

        self.db.query("update user set `email`='%s', `name`='%s' where `id`='%s'" % (email, name, userid))
        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '修改完成'}
        return self.json()

    def password(self):
        """修改密码
        """
        # 字段信息验证
        password_form = form.Form(
                form.Password('password', self.vnotnullpassword),
                form.Password('new_password', self.vnotnullpassword,
                    self.vpassword),
                validators = [
                    self.vcmppassword,
                    ]
                )
        f = password_form()
        if not f.validates():
            self.resp = {'errno': errno_form, 'msg': f.get_note()}
            return self.json()

        params = self.req_params()
        password, new_password, repeat_password = params.password, params.new_password, params.repeat_password
        token = web.ctx.session.token
        userid = auth.decode_token(token)['userid']

        user_li = self.db.query_all("select id from user where id='%s' and password='%s'" % (userid, auth.get_hashed_password(password,
                    user_passwd_salt)))
        if 0 == len(user_li):
            self.resp = {'errno': errno_db, 'msg': '密码出错'}
            return self.json()

        self.db.query("""update user set password='%s' where id='%s'""" %
                (auth.get_hashed_password(new_password, user_passwd_salt), userid))
        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '修改完成'}
        return self.json();

class QuotaAction(UserFilterAction):
    """网盘容量
    """
    def __init__(self):
        super(QuotaAction, self).__init__()

    def index(self):
        userid = auth.decode_token(web.ctx.session.token)['userid']
        quota_li = self.db.query_all("select * from quota where `user_id`='%s'" % (userid))
        self.db.commit()
        if 0 == len(quota_li):
            self.resp = {'errno': errno_db, 'msg': '暂无数据'}
            return self.json()

        self.resp = {'errno': errno_ok, 'total':
                fileutil.friend_size(quota_li[0]['total']), 'used':
                fileutil.friend_size(quota_li[0]['used'])}
        return self.json()

    def add(self):
        """修改存储容量
        """
        params = self.req_params()
        total, userid = int(params.total.strip()), params.userid

        print 'total', params.total

        if total < 0:
            self.resp = {'errno': errno_limit, 'msg': '容量必须大于0'}
            return self.json()
        elif total > max_total_quota:
            self.resp = {'errno': errno_limit, 'msg': '容量超过上限%d' % max_total_quota}
            return self.json()

        quota_li = self.db.query_all("select * from quota where `user_id`='%s'" % (userid))
        if 0 == len(quota_li):
            self.redirect('error')
        if total < int(quota_li[0]['used']):
            self.resp = {'errno': errno_limit, 'msg': '容量小于已占用磁盘容量'}
            return self.json()

        self.db.query("""update quota set total='%d' where user_id='%s'""" %
                (total, userid))
        self.db.commit()

        self.resp = {'errno': errno_ok, 'msg': '修改容量完成'}
        return self.json()
