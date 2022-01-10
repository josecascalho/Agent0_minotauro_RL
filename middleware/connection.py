#!/usr/bin/env python3
import socket
from middleware.constants import HOST
from middleware.constants import PORT
import time
import ast

class Connection:
    def __init__(self, host=HOST, port=PORT):
        self.host = host
        self.port = port
        self.s = None
        #Server
        self.addr = None
        self.conn = None

    def print_message(self, data):
        print("Data:", data)

    def connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.connect((self.host, self.port))
            return(0)
        except:
            print('A connection error occurred!')
            return(-1)

    def binding(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((self.host, self.port))
        #Test
        print("Server listening...")
        self.s.listen()
        #Test
        self.conn, self.addr = self.s.accept()
        print('Connected by', self.addr)

    def setTimeOut(self,value:float):
        self.conn.settimeout(value)

    def snd_rcv_msg(self, action, value, sleep_t=0.1):
        self.s.sendall(str.encode(action+" "+value))
        data = self.s.recv(2048)
        # test
        # print('Received', repr(data))
        message = data.decode()
        # message(ast.literal_eval(data.decode()))
        time.sleep(sleep_t)
        return message

    def rcv_msg(self):
#        try:
        data = self.conn.recv(1024)
        data = data.decode().split()
        cmd_type, value = "", ""
        if len(data) >= 2:
            cmd_type, value = data
        #test
        #print("Command type:",cmd_type)
        #print("Value:",value)
        return (cmd_type,value)
 #       except socket.timeout:
 #           print("Timeout!")

    def snd_msg(self,return_msg):
        #print("Sending return message...")
        self.conn.sendall(return_msg)




#test
#Client
#s = Connection(HOST,PORT)
#s.connect()
