#!/usr/bin/python

"""
coded by lorddarthvader for project 'stranger'
todo : 
1) find a better way to 'find_pair', 'pair_available' and 'allocate_pair' [for loop could make the server slow :c]
2) make a 'report' function
"""

import socket, select

class server:
    def __init__(self, ip='', port=1337):
        self.ip = ip
        self.port = port
        self.black_list = [] #add ip of people you hate [forthelulz]
        self.run()

    def msg(self, **kwargs):
        print "[%s] : %s" % (kwargs.keys()[0], kwargs[kwargs.keys()[0]])
    
    def m_send(self, data, *socks):
        for sock in socks:
            try:
                sock.send(data+'\n')
            except:
                continue
    
    def pair_available(self):
        for dic in self.pairs:
            for i in dic:
                if dic[i]==None:
                    return True
        return False
    
    def find_pair(self, sock):
        #a<->b
        for dic in self.pairs:
            for i in dic:
                if dic[i] is sock:
                    return i #a
                elif i is sock:
                    return dic[i] #b
    
    def allocate_pair(self, *socks):
        for sock in socks:
            if self.pair_available() != True:
                self.pairs.append(dict({sock:None}))
                self.m_send("[server] : there are currently no available stranger you can chat with, please be patient while I try to connect you with a stranger", sock)
            else:
                for dic in self.pairs:
                    for i in dic:
                        if dic[i]==None:
                            dic[i]=sock
                            self.m_send("[server] : you're now connected with a stranger", sock, i)
                            break

    def send_message(self, data, sock):
        if data: #just to make sure
            try:
                self.find_pair(sock).send('[stranger] : '+data+'\n')
            except:
                pass
                    
    def disconnect_handler(self, sock):
        self.allocate_pair(self.find_pair(sock))
        try:
            self.pairs.remove(dict({sock:self.find_pair(sock)}))
        except:
            self.pairs.remove(dict({self.find_pair(sock):sock}))
        self.input.remove(sock)

    def run(self):
        self.main_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.main_sock.bind((self.ip, self.port))
        self.main_sock.setblocking(False)
        self.main_sock.listen(21)#max strangers
        self.input = [self.main_sock]
        self.pairs = []
        self.msg(info="server started at port "+str(self.port)+"")
        
        while True:
            read, write, error = select.select(self.input, [], [])
            for sock in read:
                if sock != self.main_sock:
                    try:
                        data = sock.recv(1024).strip()
                    except:
                        continue
                    if data:
                        if data.lower()=='/ping':
                            self.m_send("[server] : pong", sock)
                        else:
                            self.send_message(data, sock)
                    else:
                        sock.close()
                        #sock.shutdown('SHUT_RDWR')
                        self.disconnect_handler(sock)
                        self.msg(info="user disconnected from server. total users : "+str(len(self.input)-1)+"")
                else:
                    client, addr = sock.accept()
                    if addr[0] in self.black_list:
                        self.m_send("[server] : your ip is blacklisted! which means you can no longer use this service >:D", client)
                        client.close()
                    else:
                        self.input.append(client)
                        self.msg(info="new user connected to the server")
                        self.allocate_pair(client)

server()
