import os
import mimetypes
import json
from .Router import Router
from .Response import Response

class App:
    def __init__(self):
        self.router = Router()
        self.default_response = Response(code=500)
        self.settings = {
            'Content-Length': True,
        }

    def set_default_headers(self, header_dict):
        for k, v in header_dict.items():
            self.default_response.add_header(k, v)

    def set_settings(self, settings_dict):
        for k, v in settings_dict.items():
            self.settings[k] = v

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
        response = Response()
        response.merge(self.default_response)
        method = env['REQUEST_METHOD'].upper()
        path = env['PATH_INFO'] or '/'
        route = self.router.find(method, path)
        if route is not None:
            route_result = route.exec(env)
            response.merge(route_result)
        else:
            response.merge(Response(404))
        response = self._after_setting(response)
        # print('status: {}\nheaders: {}\ndata: {}'.format(response.status, response.headers, response.data.decode('utf-8')))
        start_response(response.status, response.headers)
        return [response.data]

    def _after_setting(self, response):
        if self.settings['Content-Length']:
            content_length = str(len(response.data))
            response.add_header('Content-Length', content_length)
        return response


