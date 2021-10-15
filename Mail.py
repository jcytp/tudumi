import copy
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate

class Mail:
    class Server:
        def __init__(self, host, port, timeout, account, password):
            self.host = host
            self.port = port
            self.timeout = timeout
            self.account = account
            self.password = password

    class Address:
        def __init__(self, name, addr):
            self.name = name
            self.addr = addr

    ### ------------------------------------------------------------
    def __init__(self, settings):
        server = settings.get('server', {})
        self.server = Mail.Server(
            host=server.get('host', None),
            port=server.get('port', None),
            timeout=server.get('timeout', 10),
            account=server.get('account', None),
            password=server.get('password', None),
        )
        from_addr = settings.get('from')
        self.from_addr = Mail.Address(from_addr.get('name'), from_addr.get('addr'))
        self.to_list = []
        to_list = settings.get('to', [])
        for to_addr in to_list:
            self.to_list.append(Mail.Address(to_addr.get('name'), to_addr.get('addr')))
        self.cc_list = []
        cc_list = settings.get('cc', [])
        for cc_addr in cc_list:
            self.cc_list.append(Mail.Address(cc_addr.get('name'), cc_addr.get('addr')))
        self.bcc_list = []
        bcc_list = settings.get('bcc', [])
        for bcc_addr in bcc_list:
            self.bcc_list.append(Mail.Address(bcc_addr.get('name'), bcc_addr.get('addr')))
        self.subject = settings.get('subject', '')
        self.body = settings.get('body', '')
        
    def copy(self):
        return copy.deepcopy(self)

    def set_subject(self, subject):
        self.subject = subject

    def set_body(self, body):
        self.body = body

    def set_from(self, name, addr):
        self.from_addr = Mail.Address(name, addr)

    def add_to(self, name, addr):
        self.to_list.append(Mail.Address(name, addr))

    def add_cc(self, name, addr):
        self.cc_list.append(Mail.Address(name, addr))

    def add_bcc(self, name, addr):
        self.bcc_list.append(Mail.Address(name, addr))

    def send(self):
        result = True
        msg = MIMEText(self.body)
        msg['Subject'] = self.subject
        msg['From'] = formataddr((self.from_addr.name, self.from_addr.addr))
        msg_to_list = []
        for to_addr in self.to_list:
            msg_to_list.append(formataddr((to_addr.name, to_addr.addr)))
        msg['To'] = ','.join(msg_to_list)
        msg_cc_list = []
        for cc_addr in self.cc_list:
            msg_cc_list.append(formataddr((cc_addr.name, cc_addr.addr)))
        msg['Cc'] = ','.join(msg_cc_list)
        msg_bcc_list = []
        for bcc_addr in self.bcc_list:
            msg_bcc_list.append(formataddr((bcc_addr.name, bcc_addr.addr)))
        msg['Bcc'] = ','.join(msg_bcc_list)
        msg['Date'] = formatdate()
        smtp_ssl = smtplib.SMTP_SSL(
            host=self.server.host,
            port=self.server.port,
            timeout=self.server.timeout
        )
        smtp_ssl.login(self.server.account, self.server.password)
        try:
            smtp_ssl.send_message(msg)
        except:
            result = False
        smtp_ssl.quit()
        return result





