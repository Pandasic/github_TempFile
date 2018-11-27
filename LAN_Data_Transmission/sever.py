#!/usr/bin/python
import socket   #socket模块
import threading
import cv2
import numpy as np

im = np.zeros((480,640,3))
class receiveThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        data = bytes()
        while not self.thread_stop:
            global im
            data += self.socket.recv(1024)  # 把接收的数据定义为变量
            if len(data) > 480*640*3:
                im = np.fromstring(data[:480*640*3],np.uint8).reshape((480,640,3))
                data = data[ 480*640*3:]

    def stop(self):
        self.thread_stop = True


class imgshowThreading(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self):
        threading.Thread.__init__(self)
        self.thread_stop = False
    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            global im
            cv2.imshow("receive",im)
            if cv2.waitKey(10) == ord('q'):
                break

    def stop(self):
        self.thread_stop = True

class sendThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            cmd = input("Please input cmd:")  # 与人交互，输入命令
            s.sendall(bytes(cmd, encoding='utf-8'))  # 把命令发送给对端

    def stop(self):
        self.thread_stop = True

HOST='127.0.0.1'
PORT=50007
s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)   #定义socket类型，网络通信，TCP
s.bind((HOST,PORT))   #套接字绑定的IP与端口
s.listen(1)         #开始TCP监听
while 1:
    conn,addr=s.accept()   #接受TCP连接，并返回新的套接字与IP地址
    print('Connected by',addr)    #输出客户端的IP地址
    if conn is not None:
        rece = receiveThread(conn)
        rece.start()
        imthread = imgshowThreading()
        imthread.start()
conn.close()     #关闭连接