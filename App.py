import os
import mimetypes
import json
from .Router import Router
from .Response import Response
from .Request import Request
from .Database import Database
from .Session import Session
from .Mail import Mail
from .Util import Util

class App:
    def __init__(self):
        self.router = Router()
        self.default_response = Response(code=500)
        self.settings = {
            'Content-Length': True,
            'Database-Auto-Connect': True,
        }
        self.databases = {}
        self.mail = None
        self.params = {}
        self.session = None
        self.debug_mode = False

    def set_secret(self, secret):
        Util.generate_secret(secret)

    def set_settings(self, settings_dict):
        for k, v in settings_dict.items():
            self.settings[k] = v
        self.debug_mode = self.settings.get('Debug-Mode', False)

    def set_default_headers(self, header_dict):
        for k, v in header_dict.items():
            self.default_response.add_header(k, v)

    def set_database(self, name, database_dict):
        self.databases[name] = Database(database_dict, debug_mode=self.debug_mode)

    def set_session(self, session_dict):
        self.session = Session(session_dict)

    def set_mail_default(self, mail_dict):
        self.mail = Mail(mail_dict, debug_mode=self.debug_mode)
    
    def add_params(self, params_dict):
        self.params.update(params_dict)

    def set_dynamic_routes(self, route_dict):
        self.router.add_dynamic_route_dict(route_dict)

    def set_static_dir_routes(self, route_dict):
        self.router.add_static_dir_dict(route_dict)

    def set_static_file_routes(self, route_dict):
        self.router.add_static_file_dict(route_dict)

    def set_spa_routes(self, route_file_dict):
        for route_file, target_file in route_file_dict.items():
            with open(route_file, 'r') as f:
                spa_routes = json.load(f)
            for spa_page in spa_routes:
                self.router.add_static_file('/{}'.format(spa_page[0]), target_file)

    def __call__(self, env, start_response):
        request = Request(env)
        response = Response()
        response.merge(self.default_response)
        response = self._before_setting(response, request)
        route = self.router.find(request.method, request.path)
        if route is not None:
            app_env = {
                'settings': self.settings,
                'db': self.databases,
                'session': self.session,
                'mail': self.mail,
                'params': self.params,
            }
            route_result = route.exec(request, app_env)
            response.merge(route_result)
        else:
            response.merge(Response(404))
        response = self._after_setting(response)
        start_response(response.status, response.headers)
        return [response.data]

    def _before_setting(self, response, request):
        if self.settings.get('Use-Session'):
            self.session.input(request.cookie('session'))
        return response

    def _after_setting(self, response):
        if self.settings.get('Use-Session') and self.session.flg_update:
            response.add_header('Set-Cookie', self.session.cookie_format())
        if self.settings['Content-Length']:
            content_length = str(len(response.data))
            response.add_header('Content-Length', content_length)
        return response


