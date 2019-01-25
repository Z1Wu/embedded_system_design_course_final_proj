import time
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
#from tinydb import TinyDB, Query
from datetime import datetime
import json

import logging
import threading
import socket

# 
HOST_NAME = '0.0.0.0'
PORT_NUMBER = 9000

# REMOTE WIFI MODULE
REMOTE_HOST = '192.168.199.228'
REMOTE_HOST_PORT = 8080
# REMOTE_HOST = '127.0.0.1'
# REMOTE_HOST_PORT = 9999

# create a db module
#db = TinyDB("db.json")

# todo:regex expression to match static files
# static_file = 

# STATE STRING 
STATE_PASSWORD_RETTING_SUCCESSFULLY = "密码重置成功"
STATE_PASSWORD_VALID = "密码正确，大门打开"
STATE_PASSWORD_INVALID = "密码错误"
STATE_WAITTING_INPUT = '等待大门密码输入。。。'
STATE_DOOR_OPEN = 'DOOR OPEN'
STATE_DOOR_CLOSE = 'DOOR CLOSE'
STATE_DOOR_ALERT = 'DOOR ALERT'

PASSWORD = "12345678"
ADMIN_USER = "123456"
ADMIN_PASSWORD = "123456"

# global connection
connection = None

def get_current_time():
    return str(datetime.now())

def insert_open_record(res):
    db.insert({'type' : 'log', 'event' : "open", 'res' : res, 'time' : get_current_time()})

def insert_alert_record():
    # 记录开门的消息
    db.insert({'type' : 'log', 'event' : "alert", 'res' : "null", 'time' : get_current_time()})

def changeLockPassword(new_password):
    PASSWORD = new_password

def changeAdminInfo(new_user, new_password):
    ADMIN_PASSWORD = new_password
    ADMIN_USER = new_user

# share variable, will be altered by the receiver thread.
state = STATE_WAITTING_INPUT
WATING_FOR_CONNECT = False

class MyHandler(BaseHTTPRequestHandler):
    
    # static member
    STATIC_FILE_PATTERN = r'.*(/|\.html|\.js|\.css|\.png)$'
    
    suffix2MIME = {
        "png" : "image/png",
        "jpeg" : "image/jpeg",
        "html": "text/html",
        "js":"text/javascript",
        "css":"text/css"
    }

    def handle_static_file(self, rel_path, is_binary = False):
        prefix = "../front_end"
        content = None
        try:
            path = prefix + rel_path
            print("static => read file in " + path)
            mode = "r"
            if is_binary :
                mode = "rb"
            content = open(path, mode).read()    
        except FileNotFoundError:
            content = "File not found"
        return content
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        path = self.path
        static_file_match = re.match(MyHandler.STATIC_FILE_PATTERN, path)
        
        if static_file_match != None:
            suffix = static_file_match.group(1)
            is_binary = False
            print("suffix: " + suffix)
            if suffix == '/':
                suffix = '.html'
                path += 'index.html'
            mime_type = MyHandler.suffix2MIME[suffix[1:]] 
            if not mime_type.startswith('text'):
                is_binary = True
            content = self.handle_static_file(path, is_binary)
            response = self.handle_http(200, content, mime_type)
            self.wfile.write(response)
        elif path == '/get_lock_status':
            self.wfile.write(self.handle_http(200, state, "text/plain"))
        #elif path == '/get_log':
            

    def do_POST(self):
        print("receive post request from browser", self.path)
        
        content_len = int(self.headers.get('content-length', 0))
        content = self.rfile.read(content_len)
        if(self.path == "/open-door"):
            # 输入密码，打开门
            content_len = int(self.headers.get('content-length', 0))
            pw = self.rfile.read(content_len)
            print("post data : ", pw)
            # 把远程开锁的结果发送给wifi模块，wifi模块控制单片机开门, 同时把结果放回给浏览器显示密码的正确情况 
            data = None
            pw_str = pw.decode()
            if pw_str == PASSWORD: 
                data = b't'
                # 如果输入结果正确，打开门
                SendDataToWifiModule(REMOTE_HOST, REMOTE_HOST_PORT, b'o').start()
            elif pw_str != PASSWORD:
                data = b'f'
            else:
                pass
            
            # 把结果返回给浏览器
            self.wfile.write(self.handle_http(200, str(data), "text/html"))
        elif self.path == "/login":
            print(content)
            # get the target
            post_body = str(content)
            try:
                user, password = self.extractInfoFromPB(post_body)
                print(user, password)
            except:
                print("invalid post-body", post_body)

            data = None
            if user != ADMIN_USER or password != ADMIN_PASSWORD:
                data = 2
            else:
                data = 0
            self.wfile.write(self.handle_http(200, str(data), "text/plain"))
        elif self.path == "/change_info":
            print(content)
            new_user, new_password = self.extractInfoFromPB(post_body)
            changeAdminInfo(new_user, new_password)
            self.wfile.write(self.handle_http(200, "true", "text/plain"))
        elif self.path == "/change_lock_password":
            print(content)
            changeLockPassword(str(content))
            self.wfile.write(self.handle_http(200, "true", "text/plain"))

    def extractInfoFromPB(self, raw):
        user, password = raw.split("&")
        user = user[user.index('=') + 1 : ]
        password = password[password.index('=') + 1: -1]
        return user, password


    def handle_http(self, status_code, content, type = 'text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', type)
        self.end_headers()
        if not type.startswith("text"):
            return content
        return bytes(content, 'UTF-8')


class SendDataToWifiModule(threading.Thread):
    '''
        send data the remote wifi module, data is required to be 
    '''
    def __init__(self, host_name, port_num, data):
        threading.Thread.__init__(self)
        self.host_name = host_name
        self.port_num = port_num
        self.data = data
    def run(self):
        print("send data to wifi module", self.host_name, self.port_num)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host_name, self.port_num))
        # send data to wifi module
        msg = sock.recv(1024) 
        sock.send(self.data)
        sock.close()
        print("done send data to wifi module: " + str(msg))
        

# another handle the input from wifi module
# 等待来自
def receiver():
    global connection, state
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',9090))
    sock.listen(5)
    while True:
        connection = None
        print("wating connection from wifi module ... ")
        connection, address = sock.accept()
        print("connect to wifi module with address: ", address)
        buf = connection.recv(1024)            
        input = buf.decode()
        print("from wifi module:", input)
        
        # the check order matters
        if input == 'oooooooo':
            state = STATE_DOOR_OPEN
        elif input == 'cccccccc':
            state = STATE_DOOR_CLOSE
        elif input == 'aaaaaaaa':
            state = STATE_DOOR_ALERT
            insert_alert_record()
        elif input == PASSWORD:
            connection.send(b"t")
            insert_open_record(res = "successded to open")
        else:
            connection.send(b"f")
            insert_open_record(res = "fail to open")


# 如果收到信息，则打印
thread_recv = threading.Thread(target=receiver)
thread_recv.setDaemon(True)
thread_recv.start()

if __name__ == '__main__':
    server_class = HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), MyHandler)
    print(time.asctime(), 'Server Starts - %s:%s' % (HOST_NAME, PORT_NUMBER))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("press control + c")
        httpd.server_close()
        print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
    