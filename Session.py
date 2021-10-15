import json

from .Util import Util

class Session:
    def __init__(self, session_dict={}):
        self.db = session_dict.get('database', None)
        self.timelimit_delta = Util.timedelta(minutes=session_dict.get('minutes', 30))
        self.timelimit_update = Util.timedelta(minutes=session_dict.get('update', 1))
        self.name = session_dict.get('name', 'session')
        self.path = session_dict.get('path', '/')
        self.secure = session_dict.get('secure', False)
        self.httponly = session_dict.get('httponly', True)
        self.id = ''
        self.data = {}
        self.update = False

    def input(self, encrypted_session):
        self.id = ''
        self.data = {}
        self.flg_update = False
        if encrypted_session is not None:
            decrypted = Util.decrypt_text(encrypted_session)
            if self.db is None:
                decrypted_list = decrypted.split('|', 2)
                if decrypted_list[0] == self.name:
                    timelimit = Util.strptime(decrypted_list[1])
                    now = Util.now()
                    if timelimit > now:
                        self.data = json.loads(decrypted_list[2])
                        if now + self.timelimit_delta > timelimit + self.timelimit_update:
                            self.flg_update = True
                            print('### session update')
            else:
                self.id = decrypted
                ### ToDo: get timelimit and data from database, and check time
        else:
            if self.db is None:
                self.flg_update = True
            else:
                pass

    def get_data(self, key):
        return self.data.get(key)

    def set_data(self, name, value):
        self.data[name] = value
        self.flg_update = True

    def generate(self):
        if self.db is None:
            timelimit = Util.strftime(Util.now() + self.timelimit_delta)
            data = json.dumps(self.data)
            session_str = Util.encrypt_text('{}|{}|{}'.format(self.name, timelimit, data))
        else:
            ### ToDo: insert timelimit and data into database
            session_str = self.id
        return session_str

    def cookie_format(self):
        session_str = self.generate()
        result = '{}={}; path={}'.format(self.name, session_str, self.path)
        if self.secure:
            result += '; Secure'
        if self.httponly:
            result += '; HttpOnly'
        return result





