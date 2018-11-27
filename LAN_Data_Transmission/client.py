#!/usr/bin/python
import socket
import threading
import cv2
import numpy as np

class receiveThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.socket = socket
        self.thread_stop = False

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop:
            data = s.recv(1024)  # 把接收的数据定义为变量
            print(data)  # 输出变量

    def stop(self):
        self.thread_stop = True


class sendThread(threading.Thread):  # The timer class is derived from the class threading.Thread
    def __init__(self, socket,cap):
        threading.Thread.__init__(self)
        self.socket = socket
        self.thread_stop = False
        if isinstance(cap,cv2.VideoCapture):
            self.video_cap = cap

    def run(self):  # Overwrite run() method, put what you want the thread do here
        while not self.thread_stop and self.video_cap.isOpened():
            ret,im = self.video_cap.read()
            #im = cv2.resize(im,(80,60))
            print(im.shape)
            if ret:
                data = bytes(im)
                s.sendall(data)  # 把命令发送给对端
            cv2.waitKey(10)

    def stop(self):
        self.thread_stop = True
        
HOST='127.0.0.1'
PORT=50007
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)      #定义socket类型，网络通信，TCP
s.connect((HOST,PORT))       #要连接的IP与端口

rece = receiveThread(s)

cap = cv2.VideoCapture(0)
send = sendThread(s,cap)

rece.start()
send.start()
while rece.thread_stop and send.thread_stop:
    s.close()   #关闭连接