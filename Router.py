import re
import mimetypes
import json
from .Response import Response

class Router:
    def __init__(self):
        self.route_list = []
    
    class Route:
        def __init__(self, method, uri_pattern, uri_param_names=(), file_path_pattern=None, func=None):
            self.method = method
            self.uri_pattern = uri_pattern
            self.uri_param_names = uri_param_names
            self.file_path_pattern = file_path_pattern
            self.func = func

        def match(self, method, path):
            # print('path: {}, self.uri_pattern: {}'.format(path, self.uri_pattern))
            if self.method == method and re.match(self.uri_pattern, path):
                return True
            return False

        def exec(self, request, env):
            response = Response()
            databases = env['db'].values()
            m = re.match(self.uri_pattern, request.path)
            uri_params = m.groups()
            for i in range(len(self.uri_param_names)):
                param_name = self.uri_param_names[i]
                param_value = uri_params[i]
                request.add_param(param_name, param_value)
            if self.func is not None:
                for db in databases:
                    db.connect()
                res = self.func(request, env)
                for db in databases:
                    db.close()
                response.merge(res)
            if self.file_path_pattern is not None:
                res = self._get_file(request.path)
                response.merge(res)
            return response

        def _get_file(self, request_path):
            file_path = self.file_path_pattern
            match = re.search(self.uri_pattern, request_path)
            if len(match.groups()) > 0:
                sub_path = match.group(1)
                file_path = file_path.replace('{sub_path}', sub_path)
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
            except (FileNotFoundError, IsADirectoryError, PermissionError):
                return Response(404)
            content_type = mimetypes.guess_type(file_path)[0]
            headers = {'Content-Type': content_type} if content_type is not None else {}
            return Response(200, headers, data)

    def add_static_dir(self, request_path_root, target_path_root):
        # request_path_root
        #   - 中括弧 {} を使用してパス変数を設定可能。
        uri_pattern = '^{}(.*)$'.format(request_path_root)
        file_path_pattern = '{}{{sub_path}}'.format(target_path_root)
        route = self.Route('GET', uri_pattern, file_path_pattern=file_path_pattern)
        self.route_list.append(route)

    def add_static_dir_dict(self, static_dir_dict):
        for k, v in static_dir_dict.items():
            self.add_static_dir(k, v)

    def add_static_file(self, request_path_pattern, target_path):
        uri_pattern = request_path_pattern
        uri_params_list = re.findall('\{[^\}]*\}', uri_pattern)
        for i in range(len(uri_params_list)):
            uri_params_list[i] = uri_params_list[i][1:-1]
        uri_pattern = re.sub('\{[^\}]*\}', '([^/]*)', uri_pattern)
        uri_pattern = '^{}$'.format(uri_pattern)
        file_path_pattern = '{}'.format(target_path)
        route = self.Route('GET', uri_pattern, file_path_pattern=file_path_pattern)
        self.route_list.append(route)

    def add_static_file_dict(self, static_file_list):
        for k, v in static_file_list.items():
            self.add_static_file(k, v)

    def add_dynamic_route(self, method, request_path_pattern, target_func):
        # request_path_pattern
        #   - ワイルドカード * を使用可能。
        #   - 中括弧 {} を使用してパス変数を設定可能。
        uri_pattern = request_path_pattern
        uri_pattern = uri_pattern.replace('*', '[^/]*')
        uri_params_list = re.findall('\{[^\}]*\}', uri_pattern)
        for i in range(len(uri_params_list)):
            uri_params_list[i] = uri_params_list[i][1:-1]
        uri_param_names = tuple(uri_params_list)
        uri_pattern = re.sub('\{[^\}]*\}', '([^/]*)', uri_pattern)
        uri_pattern = '^{}$'.format(uri_pattern)
        route = self.Route(method, uri_pattern, uri_param_names=uri_param_names, func=target_func)
        self.route_list.append(route)

    def add_dynamic_route_dict(self, dynamic_route_dict):
        for path, d in dynamic_route_dict.items():
            for method, func in d.items():
                self.add_dynamic_route(method, path, func)

    def find(self, method, path):
        for route in self.route_list:
            if route.match(method, path):
                return route
        return None



