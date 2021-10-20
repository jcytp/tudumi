from .Response import Response
from .Util import Util

class API:
    ### ------------------------------------------------------------
    class Code:
        ERR_NONE = 0
        ERR_SESSION_INVALID = 1
        ERR_NO_REQUIRED_PARAM = 10
        ERR_INVALID_PARAM = 11
        ERR_AUTH_FAILED = 20
        ERR_DATA_FAILED = 30
        ERR_DATA_NOT_EXIST = 31
        ERR_DATA_CONFLICT = 32
        ERR_MAIL_FAILED = 41
        ERR_UNKNOWN = 99

    ### ------------------------------------------------------------
    class ErrorMessage:
        def __init__(self):
            self.messages = []
        
        def add(self, category, message):
            self.messages.append((category, message))
        
        def get_all(self):
            all_messages = []
            for message_set in self.messages:
                all_messages.append(message_set[1])
            return all_messages

        def get_list(self, category):
            category_messages = []
            for message_set in self.messages:
                if message_set[0] == category:
                    category_messages.append(message_set[1])
            return category_messages
        
        def clear(self):
            self.messages = []
    
    ### ------------------------------------------------------------
    def __init__(self, request, db=None, code=200):
        self.response = Response(code)
        self.request = request
        self.params = {}
        self.error_code = 0
        self.error_message = API.ErrorMessage()
        self.db = db
    
    def result(self, data=None):
        json_data = {
            'error': self.get_error_code(),
            'message': self.get_error_messages(),
            'data': data
        }
        self.update_response(json_data=json_data)
        return self.response

    def update_response(self, code=0, headers={}, data=b'', text_data='', json_data=None):
        resp = Response(code, headers, data, text_data, json_data)
        self.response.merge(resp)

    def set_custom_error(self, code, message='ERROR'):
        self.error_code = code
        self.error_message.add('custom_error', message)

    def is_error(self):
        return self.error_code > API.Code.ERR_NONE

    def get_error_code(self):
        return self.error_code

    def get_error_messages(self, category='all', delimiter='\n'):
        if category == 'all':
            return delimiter.join(self.error_message.get_all())
        return delimiter.join(self.error_message.get_list(category))

    def clear_errors(self):
        self.error_code = API.Code.ERR_NONE
        self.error_message.clear()

    ### ------------------------------------------------------------
    def check_param(self, name, default=None, type=str,
            minlength=None, maxlength=None, chartype=None,
            minvalue=None, maxvalue=None, valid_list=None,
            display_name=None, required=False):
        if display_name is None:
            display_name = name
        if not name in self.request.params:
            if required:
                self.error_code = API.Code.ERR_NO_REQUIRED_PARAM
                self.error_message.add('check_param', '{} は必須です'.format(display_name))
            self.params[name] = default
            return default
        value = self.request.params.get(name)
        if type == str:
            try:
                if (minlength is not None) and (len(value) < minlength):
                    raise ValueError()
                if (maxlength is not None) and (len(value) > maxlength):
                    raise ValueError()
                if chartype is not None:
                    approvals, prohibitions = Util.get_approval_chars(chartype)  # self._get_approvals(chartype)
                    for c in value:
                        if c in prohibitions:
                            raise ValueError()
                        if len(approvals) > 0 and not c in approvals:
                            raise ValueError()
                if valid_list is not None:
                    if not value in valid_list:
                        raise ValueError()
            except ValueError:
                if required and default is None:
                    self.error_code = API.Code.ERR_INVALID_PARAM
                    approvals = ''
                    prohibitions = ''
                    if chartype is not None:
                        approvals, prohibitions = Util.get_approval_chars_explain(chartype)  # self._get_approval_explain(chartype)
                    msg = '{} は{}{}{}{}{} の文字列です'.format(
                        display_name,
                        '' if minlength is None else ' {}文字以上'.format(minlength),
                        '' if maxlength is None else ' {}文字以下'.format(maxlength),
                        '' if approvals == '' else ' 使用可能文字{}'.format(approvals),
                        '' if prohibitions == '' else ' 使用禁止文字{}'.format(prohibitions),
                        '' if valid_list is None else 'または'.join(valid_list)
                    )
                    self.error_message.add('check_param', msg)
                value = default
        elif type == int or type == float:
            value = int(value) if type == int else float(value)
            try:
                if (minvalue is not None) and (value < minvalue):
                    raise ValueError()
                if (maxvalue is not None) and (value > maxvalue):
                    raise ValueError()
                if valid_list is not None:
                    if not value in valid_list:
                        raise ValueError()
            except ValueError:
                if required and default is None:
                    self.error_code = API.Code.ERR_INVALID_PARAM
                    msg = '{} は{}{}{} の{}です'.format(
                        display_name,
                        '' if minvalue is None else ' {}以上'.format(minvalue),
                        '' if maxvalue is None else ' {}以下'.format(maxvalue),
                        '' if valid_list is None else 'または'.join(valid_list),
                        '整数' if type == int else '数値'
                    )
                    self.error_message.add('check_param', msg)
                value = default
        else:
            print('### Error| API.check_param() | invalid parameter type {}.'.format(type))
            value = default
        self.params[name] = value
        return value

    def param(self, param_name):
        return self.params.get(param_name, None)

    ### ------------------------------------------------------------
    def _build_conditions(self, conditions):
        condition_list = []
        for condition_set in conditions:
            if not condition_set[1] in ['=', '<', '>', '!=']:
                raise ValueError
            condition_list.append('`{}` {} %s'.format(condition_set[0], condition_set[1]))
        if len(condition_list) == 0:
            return ''
        conditions_text = 'WHERE {}'.format(' AND '.join(condition_list))
        return conditions_text

    def _build_bulk_conditions(self, conditions_list):
        conditions_text_list = []
        for conditions in conditions_list:
            condition_list = []
            for condition_set in conditions:
                if not condition_set[1] in ['=', '<', '>', '!=']:
                    raise ValueError
                condition_list.append('`{}` {} %s'.format(condition_set[0], condition_set[1]))
            if len(condition_list) == 0:
                pass
            else:
                conditions_text = '({})'.format(' AND '.join(condition_list))
                conditions_text_list.append(conditions_text)
        if len(conditions_text_list) == 0:
            return ''
        all_conditions_text = 'WHERE {}'.format(' OR '.join(conditions_text_list))
        return all_conditions_text

    def _build_substitutions(self, values):
        substitution_list = []
        for value_set in values:
            substitution_list.append('`{}` = %s'.format(value_set[0]))
        substitutions_text = ', '.join(substitution_list)
        return substitutions_text
    
    def _build_columns(self, values):
        column_list = []
        for value_set in values:
            column_list.append('`{}`'.format(value_set[0]))
        columns_text = ', '.join(column_list)
        return columns_text

    def _build_placeholders(self, values):
        placeholder_list = []
        for value_set in values:
            placeholder_list.append('%s')
        placeholders_text = ', '.join(placeholder_list)
        return placeholders_text

    def _build_params(self, values=[], conditions=[], bulk_conditions=[]):
        params_list = []
        for value_set in values:
            params_list.append(value_set[1])
        for condition_set in conditions:
            params_list.append(condition_set[2])
        for b_conditions in bulk_conditions:
            for b_condition_set in b_conditions:
                params_list.append(b_condition_set[2])
        return tuple(params_list)

    def _build_order(self, order):
        if order is None:
            return ''
        if not order[1] in ['ASC', 'DESC']:
            raise ValueError
        order_text = 'ORDER BY `{}` {}'.format(order[0], order[1])
        return order_text

    def get_one(self, table, conditions):
        data = self._select(table, conditions, None, 1, 0)
        if data is None or len(data) == 0:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('check_exist', 'データベース操作にエラーが発生しました')
            return None
        return data[0]

    def get_list(self, table, conditions, order=None, limit=100, offset=0):
        data = self._select(table, conditions, order, limit, offset)
        if data is None:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('check_exist', 'データベース操作にエラーが発生しました')
            return None
        return data

    def _select(self, table, conditions, order, limit, offset):
        sql = 'SELECT * FROM `{}` {} {} LIMIT {} OFFSET {}'.format(table, self._build_conditions(conditions), self._build_order(order), limit, offset)
        params = self._build_params(conditions=conditions)
        return self.db.query(sql, params)

    def get_max_value(self, table, column, conditions):
        sql = 'SELECT MAX(`{}`) FROM {} {}'.format(column, table, self._build_conditions(conditions))
        params = self._build_params(conditions=conditions)
        data = self.db.query(sql, params)
        if data is None or len(data) == 0:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('check_exist', 'データベース操作にエラーが発生しました')
            return None
        return data[0][0]

    def check_exist(self, table, conditions):
        data = self._select_count(table, conditions)
        if data is None or len(data) == 0:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('check_exist', 'データベース操作にエラーが発生しました')
            return False
        if data[0][0] == 0:
            self.error_code = API.Code.ERR_DATA_NOT_EXIST
            self.error_message.add('check_exist', '対象データがありません')
            return False
        return True

    def check_conflict(self, table, conditions):
        data = self._select_count(table, conditions)
        if data is None or len(data) == 0:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('check_conflict', 'データベース操作にエラーが発生しました')
            return True
        if data[0][0] > 0:
            self.error_code = API.Code.ERR_DATA_CONFLICT
            self.error_message.add('check_conflict', '競合データが存在します')
            return True
        return False
    
    def _select_count(self, table, conditions):
        sql = 'SELECT COUNT(*) FROM `{}` {}'.format(table, self._build_conditions(conditions))
        params = self._build_params(conditions=conditions)
        return self.db.query(sql, params)

    def count(self, table, conditions):
        data = self._select_count(table, conditions)
        if data is None or len(data) == 0:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('count', 'データベース操作にエラーが発生しました')
            return 0
        return data[0][0]

    def register(self, table, values):
        sql = 'INSERT INTO `{}` ({}) VALUES ({})'.format(table, self._build_columns(values), self._build_placeholders(values))
        params = self._build_params(values=values)
        result = self.db.execute(sql, params)
        if not result:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('register', 'データベース操作にエラーが発生しました')
            return None
        return self.db.last_row_id()

    def update(self, table, values, conditions):
        sql = 'UPDATE `{}` SET {} {}'.format(table, self._build_substitutions(values), self._build_conditions(conditions))
        params = self._build_params(values=values, conditions=conditions)
        result = self.db.execute(sql, params)
        if not result:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('update', 'データベース操作にエラーが発生しました')
            return False
        return True

    def ins_od_upd(self, table, ins_values, upd_values):
        sql = 'INSERT INTO `{table}` ({columns}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {substitutions}'.format(
            table = table,
            columns = self._build_columns(ins_values),
            placeholders = self._build_placeholders(ins_values),
            substitutions = self._build_substitutions(upd_values),
        )
        params_list = list(self._build_params(values=ins_values))
        params_list.extend(list(self._build_params(values=upd_values)))
        params = tuple(params_list)
        result = self.db.execute(sql, params)
        if not result:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('ins_od_upd', 'データベース操作にエラーが発生しました')
            return False
        return True

    def delete(self, table, conditions):
        sql = 'DELETE FROM `{}` {}'.format(table, self._build_conditions(conditions))
        params = self._build_params(conditions=conditions)
        result = self.db.execute(sql, params)
        if not result:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('delete', 'データベース操作にエラーが発生しました')
            return False
        return True
    
    def delete_bulk(self, table, bulk_conditions):
        sql = 'DELETE FROM `{}` {}'.format(table, self._build_bulk_conditions(bulk_conditions))
        params = self._build_params(bulk_conditions=bulk_conditions)
        result = self.db.execute(sql, params)
        if not result:
            self.error_code = API.Code.ERR_DATA_FAILED
            self.error_message.add('delete_bulk', 'データベース操作にエラーが発生しました')
            return False
        return True


    ### ------------------------------------------------------------


