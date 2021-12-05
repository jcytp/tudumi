from datetime import datetime, timedelta
import random
from base64 import b64encode, b64decode
import bcrypt
from urllib.parse import quote, unquote
from Crypto.Hash import SHA256
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes

class Util:
    SECRET_KEY = None
    datetime = datetime

    @staticmethod
    def generate_secret(secret, iterations_count=100):
        salt = b'\xd1\xf1\x8c\xb3E\xf3\x12\xeb\x98orv!\xb4\x00\xcc\xdcw\xe4\xc8\x1f\xfd\x91\xfb\xb2\x95\x8b\x9b\x84Vkz'
        Util.SECRET_KEY = PBKDF2(secret, salt, 32, count=iterations_count, hmac_hash_module=SHA256)

    @staticmethod
    def encrypt_text(plain_text, flg_quote=False):
        pt_bytes = plain_text.encode()
        cipher = AES.new(Util.SECRET_KEY, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(pt_bytes, AES.block_size))
        iv_b64 = b64encode(cipher.iv, altchars=b'-:').decode()
        ct_b64 = b64encode(ct_bytes, altchars=b'-:').decode()
        cipher_text = '{}|{}'.format(iv_b64, ct_b64)
        if flg_quote:
            cipher_text = quote(cipher_text, safe='')
        return cipher_text

    @staticmethod
    def decrypt_text(cipher_text, flg_quote=False):
        try:
            if flg_quote:
                cipher_text = unquote(cipher_text)
            iv_b64, ct_b64 = tuple(cipher_text.split('|'))
            iv_bytes = b64decode(iv_b64.encode(), altchars=b'-:')
            ct_bytes = b64decode(ct_b64.encode(), altchars=b'-:')
            cipher = AES.new(Util.SECRET_KEY, AES.MODE_CBC, iv_bytes)
            pt_bytes = unpad(cipher.decrypt(ct_bytes), AES.block_size)
            plain_text = pt_bytes.decode()
        except (ValueError, KeyError):
            print('### Util.decrypt_text()| Error')
            return ''
        return plain_text

    @staticmethod
    def random_text(length):
        approvals = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        applen = len(approvals)
        result = ''
        for i in range(length):
            result += approvals[random.randrange(applen)]
        return result

    # @staticmethod
    # def b64_encode(text):
    #     return b64encode(text.encode()).decode()

    # @staticmethod
    # def b64_decode(b64text):
    #     return b64decode(b64text.encode()).decode()

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt(rounds=10, prefix=b'2a')
        passhash = bcrypt.hashpw(password.encode(), salt).decode()
        return passhash
    
    @staticmethod
    def check_password(password, passhash):
        return bcrypt.checkpw(password.encode(), passhash.encode())

    @staticmethod
    def get_approval_chars(chartype):
        approvals = ''
        prohibitions = ''
        if 'a' in chartype:
            approvals += 'abcdefghijklmnopqrstuvwxyz'
        if 'A' in chartype:
            approvals += 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        if '0' in chartype:
            approvals += '0123456789'
        if '!' in chartype: ### 一般記号
            approvals += '!#$%&\'*+-/=?^_`{|}~'
        if '(' in chartype: ### 括弧系記号
            approvals += '().,:;<>@[]"\\'
        if '@' in chartype: ### メール使用記号
            approvals += '.-[]@'
        if 'x' in chartype: ### 文面出力の禁止文字
            prohibitions += '.,:;<>@[]"\'`|\r\n'
        return approvals, prohibitions

    @staticmethod
    def get_approval_chars_explain(chartype):
        approval_list = []
        prohibitions = ''
        if 'a' in chartype:
            approval_list.append('a-z')
        if 'A' in chartype:
            approval_list.append('A-Z')
        if '0' in chartype:
            approval_list.append('0-9')
        if '!' in chartype: ### 一般記号
            approval_list.append('!#$%&\'*+-/=?^_`{|}~')
        if '(' in chartype: ### 括弧系記号
            approval_list.append('().,:;<>@[]"\\')
        if '@' in chartype: ### メール使用記号
            approval_list.append('.-[]@')
        if 'x' in chartype: ### 文面出力の禁止文字
            prohibitions += '.,:;<>@[]"\'`|\r\n'
        return ' '.join(approval_list), prohibitions
    
    @staticmethod
    def now():
        return datetime.now()

    @staticmethod
    def strftime(time_val):
        if type(time_val) != datetime:
            return None
        return time_val.strftime('%Y/%m/%d %H:%M:%S')

    @staticmethod
    def strptime(time_str):
        try:
            str_time = datetime.strptime(time_str, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            return None
        return str_time

    @staticmethod
    def timedelta(**kwargs):
        return timedelta(**kwargs)






