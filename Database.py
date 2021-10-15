from importlib import import_module

class Database:
    def __init__(self, database_dict, debug_mode=False):
        self.type = database_dict.get('kind', 'MySQL')
        if self.type == 'MySQL':
            self.module = import_module('mysql.connector')
        else:
            self.module = None
        self.host = database_dict.get('host', 'localhost')
        self.port = database_dict.get('port', 3306)
        self.user = database_dict.get('user', 'root')
        self.password = database_dict.get('password', None)
        self.database = database_dict.get('database', None)
        self.cur = None
        self.con = None
        self.debug_mode = debug_mode

    def connect(self):
        if self.debug_mode:
            print('### Database.connect()')
        self.con = self.module.connect(
            user=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )
        self.cur = self.con.cursor()

    def close(self):
        if self.debug_mode:
            print('### Database.close()')
        if self.cur is not None:
            self.cur.close()
        if self.con is not None:
            self.con.close()

    def query(self, sql, params=()):
        result = None
        if self.debug_mode:
            print('### Database.query() | sql: {}'.format(sql))
            print('### Database.query() | params: {}'.format(params))
        try:
            self.cur.execute(sql, params)
            result = self.cur.fetchall()
        except self.module.Error as e:
            print('DB query Error: {}'.format(e))
            print('    sql: {}'.format(sql))
            print('    params: {}'.format(params))
        return result

    def execute(self, sql, params=()):
        result = False
        if self.debug_mode:
            print('### Database.execute() | sql: {}'.format(sql))
            print('### Database.execute() | params: {}'.format(params))
        try:
            self.cur.execute(sql, params)
            self.con.commit()
            result = True
        except self.module.Error as e:
            print('DB execute Error: {}'.format(e))
            print('    sql: {}'.format(sql))
            print('    params: {}'.format(params))
        return result

    def last_row_id(self):
        return self.cur.lastrowid


