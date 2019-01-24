import time
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from tinydb import TinyDB, Query
from datetime import datetime


import logging
import threading
import socket

# 
HOST_NAME = '0.0.0.0'
PORT_NUMBER = 9000

# REMOTE WIFI MODULE
# REMOTE_HOST = '192.168.199.228'
# REMOTE_HOST_PORT = 8080
REMOTE_HOST = '127.0.0.1'
REMOTE_HOST_PORT = 9999

# create a db module
db = TinyDB("db.json")

# todo:regex expression to match static files
# static_file = 

# STATE STRING 
STATE_PASSWORD_RETTING_SUCCESSFULLY = "密码重置成功"
STATE_PASSWORD_VALID = "密码正确，大门打开"
STATE_PASSWORD_INVALID = "密码错误"
STATE_WAITING_INPUT = '等待大门密码输入。。。'
STATE_DOOR_OPEN = 'DOOR OPEN'
STATE_DOOR_CLOSE = 'DOOR CLOSE'
STATE_DOOR_ALERT = 'DOOR ALERT'

PASSWORD = "12345678"
connection = None

def get_current_time():
    return str(datetime.now())

def insert_open_record(res):
    db.insert({'event' : "open", 'res' : res, 'time' : get_current_time()})

def insert_alert_record():
    # 记录开门的消息
    db.insert({'event' : "alert", 'res' : "null", 'time' : get_current_time()})

def handle_static_file(rel_path):
    prefix = "../front_end"
    content = None
    try:
        path = prefix + rel_path
        print("static => read file in " + path)
        content = open(path, "r").read()    
    except FileNotFoundError:
        content = "File not found"
    return content

# share variable, will be altered by the receiver thread.
state = STATE_WAITING_INPUT
WATING_FOR_CONNECT = False

class MyHandler(BaseHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        path = self.path
        if(path == "/" or '.html' in path):
            # 作为静态文件服务器
            # content = None
            # try:
            #     content = open("../front_end/index.html", "r").read()
            # except FileNotFoundError:
            #     content = "file not found"
            if path == '/':
                path += 'index.html'
            content = handle_static_file(path)
            response = self.handle_http(200, content, "text/html")
            self.wfile.write(response)
        elif(self.path == "/poll"):
            # polling the lcok state
            self.wfile.write(self.handle_http(200, state))
        elif('.css' in path):
            # write password file
            content = handle_static_file(path)        
            self.wfile.write(self.handle_http(200, content, "text/css"))

    def do_POST(self):
        print("receive post request from browser", self.path)
        if(self.path == "/open-door"):
            # 输入密码，打开门
            content_len = int(self.headers.get('content-length', 0))
            pw = self.rfile.read(content_len)
            print("post data : ", pw)
            # 把远程开锁的结果发送给wifi模块，wifi模块控制单片机开门, 同时把结果放回给浏览器显示密码的正确情况 
            data = None
            if pw.decode == PASSWORD: 
                data = b't'
            elif pw.decode != PASSWORD:
                data = b'f'
            else:
                pass
            
            SendDataToWifiModule(REMOTE_HOST, REMOTE_HOST_PORT, data).start()
            # 把结果返回给浏览器
            self.wfile.write(self.handle_http(200, str(data), "text/html"))

    def handle_http(self, status_code, content, type = 'text/html'):
        self.send_response(status_code)
        self.send_header('Content-type', type)
        self.end_headers()
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
        sock.send(self.data)
        sock.close()
        print("done send data to wifi module")
        

# another handle the input from wifi module
# 等待来自
def receiver():
    global connection, state
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('0.0.0.0',8080))
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
        pass
    httpd.server_close()
    print(time.asctime(), 'Server Stops - %s:%s' % (HOST_NAME, PORT_NUMBER))
