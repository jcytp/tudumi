import cgi
import json
from urllib.parse import parse_qs

class Request:
    def __init__(self, env):
        self.method = env.get('REQUEST_METHOD').upper()
        self.path = env.get('PATH_INFO') or '/'
        self.params = parse_qs(env.get('QUERY_STRING'))
        self.length = int(env.get('CONTENT_LENGTH') or 0)
        self.body = env['wsgi.input'].read(self.length)
        form_data = cgi.FieldStorage(
            fp=env['wsgi.input'],
            environ=env,
            keep_blank_values=True,
        )
        for mfs in form_data.list:
            self.params[mfs.name] = mfs.value

