
class Response:
    CODE_STATUS = {
          0: None,
        200: '200 OK',
        404: '404 Not Found',
        500: '500 Internal Server Error',
    }

    def __init__(self, code=0, headers={}, data=b''):
        self.status = Response.CODE_STATUS.get(code)
        self.headers = []
        for k, v in headers.items():
            self.headers.append((k, v))
        self.data = data

    def set_code(self, code):
        self.status = Response.CODE_STATUS.get(code)

    def set_status(self, status):
        self.status = status

    def set_headers(self, headers):
        self.headers = headers

    def add_header(self, key, value):
        dict_headers = dict(self.headers)
        dict_headers[key] = value
        self.headers = list(dict_headers.items())

    def set_data(self, data):
        self.data = data

    def add_data(self, data):
        self.data += data

    def merge(self, response):
        if response.status is not None:
            self.status = response.status
        dict_headers = dict(self.headers)
        for item in response.headers:
            dict_headers[item[0]] = item[1]
        self.headers = list(dict_headers.items())
        self.data += response.data

