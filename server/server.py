from os import path

from configparser import ConfigParser
from pdf2image import convert_from_path

from tornado import auth, httpserver, ioloop, web, escape
from database import DataBase


config = ConfigParser()
config.read('config.ini')

db = DataBase('sqlite:///{}'.format(config['server']['database_path']))


class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        cookie = self.get_secure_cookie('user')
        if cookie is not None:
            cookie = cookie.decode()
            if db.get_user(cookie) is None:
                self.clear_cookie('user')
                cookie = None
        return cookie


class MainHandler(BaseHandler):
    @web.authenticated
    def get(self):
        print('main get')
        if not self.current_user:
            self.redirect('/login/')
            return
        name = escape.xhtml_escape(self.current_user)
        self.render('main.html',
                    username=name,
                    file_list=self._generate_file_list(),
                    error=self.get_argument('error', None))

    def post(self):
        action = self.get_argument(
            'logout', None) or self.get_argument('upload', None)
        if action == 'Logout':
            self.clear_cookie('user')
            self.redirect('/')
        elif action == 'Upload':
            error = self._upload_file()
            if error is not None:
                self.redirect(
                    '/?error={}'.format(escape.url_escape(error)))
            else:
                self.redirect('/')

    def _generate_file_list(self):
        files = db.get_file('%')
        result = []
        for file in files:
            result.append(file)
            result.extend(db.get_pages(file.id))
        return result

    def _upload_file(self):
        error = None
        fileinfo = self.request.files['filearg'][0]
        filename = path.splitext(fileinfo['filename'])
        if filename[1] == '.pdf':
            existing_files = db.get_file(name=filename[0])
            if len(existing_files) == 0:
                self._save_file_and_pages(fileinfo)
            else:
                filename = (
                    filename[0] + '_({})'.format(len(existing_files)),
                    filename[1]
                )
                fileinfo['filename'] = ''.join(filename)
                self._save_file_and_pages(fileinfo)
        else:
            error = 'Only .pdf files allowed'
        return error

    def _save_file_and_pages(self, fileinfo):
        filepath = path.join(
            config['server']['files_path'], fileinfo['filename'])
        with open(path.join(config['server']['static_path'],
                            filepath), 'wb') as f:
            f.write(fileinfo['body'])

        db.add_file(author_id=db.get_user(self.current_user).id,
                    name=fileinfo['filename'],
                    path=filepath)

        for i, img in enumerate(convert_from_path(filepath)):
            file_base_name = path.splitext(fileinfo['filename'])[0]
            page_name = '{}_page{}.png'.format(file_base_name, i + 1)
            page_path = path.join(config['server']['files_path'], page_name)
            db.add_page(origin_id=db.get_file(fileinfo['filename'])[0].id,
                        name='__page_{}.png'.format(i + 1),
                        path=page_path)
            img.save(path.join(config['server']['static_path'],
                               page_path))


class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html', error=self.get_argument('error', None))

    def post(self):
        action = self.get_argument(
            'signin', None) or self.get_argument('signup', None)

        if action == 'Sign In':
            error = self._signin()
        elif action == 'Sign Up':
            error = self._signup()
        else:
            error = 'Unknown command'
        if error is not None:
            self.redirect('/login/?error={}'.format(escape.url_escape(error)))
        else:
            self.redirect('/')

    def _signin(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        error = None
        if username is not None and password is not None:
            user = db.get_user(username)
            if user is not None and user.password == password:
                self.set_secure_cookie('user', username)
            else:
                error = 'Incorrect login/password'
        else:
            error = 'Both login and password must be filled'
        return error

    def _signup(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        error = None
        if username is not None and password is not None:
            user = db.get_user(username)
            if user is None:
                db.add_user(name=username, password=password)
                self.set_secure_cookie('user', username)
            else:
                error = 'User already exists'
        else:
            error = 'Both login and password must be filled'
        return error


class Application(web.Application):
    def __init__(self):
        handlers = [
            ('/', MainHandler),
            ('/login/', LoginHandler),
        ]
        settings = {
            'template_path': config['server']['template_path'],
            'cookie_secret': config['user']['cookie_secret'],
            'login_url': '/login/',
            'static_path': config['server']['static_path'],
            'auto_reload': True
        }
        web.Application.__init__(self, handlers, **settings)

    def run(self):
        http_server = httpserver.HTTPServer(self)
        http_server.listen(int(config['server']['port']))
        ioloop.IOLoop.instance().start()

    def stop(self):
        ioloop.IOLoop.instance().stop()
