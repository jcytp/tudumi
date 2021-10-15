import json
from http import cookies

class Response:
    CODE_STATUS = {
          0: None,
        200: '200 OK',
        404: '404 Not Found',
        500: '500 Internal Server Error',
    }

    def __init__(self, code=0, headers={}, data=b'', text_data='', json_data=None):
        self.status = Response.CODE_STATUS.get(code)
        self.headers = []
        for key, value in headers.items():
            self.headers.append((key, value))
        self.data = data
        if len(text_data) > 0:
            self.data = text_data.encode('utf-8')
        if json_data is not None:
            self.data = json.dumps(json_data).encode('utf-8')

    def set_code(self, code):
        self.status = Response.CODE_STATUS.get(code)

    def set_status(self, status):
        self.status = status

    def set_headers(self, headers):
        self.headers = headers

    def add_header(self, key, value):
        # dict_headers = dict(self.headers)
        # dict_headers[key] = value
        # self.headers = list(dict_headers.items())
        self.headers.append((key, value))

    def set_data(self, data):
        self.data = data

    def add_data(self, data):
        self.data += data

    def merge(self, response):
        if response.status is not None:
            self.status = response.status
        # dict_headers = dict(self.headers)
        # for item in response.headers:
        #     dict_headers[item[0]] = item[1]
        # self.headers = list(dict_headers.items())
        for item in response.headers:
            self.headers.append(item)
        self.data += response.data

