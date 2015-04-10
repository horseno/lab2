#import zerorpc
import sys
sys.path.append("./")
import setting
import multicast
import xmlrpclib 
import SimpleXMLRPCServer
import socket
import select
import time
import random

class Sensor:
    ''' Represents any senors'''
    def __init__(self,name,serveradd,localadd,devNum):
        '''initialize a sensor, create a client to connect to server'''
        self._isLeader = 0
        self._timeoffset = 0
        self._electID = random.random()
        self.name = name
        self.ctype = 'sensor'
        self.localadd = localadd

        self.c = xmlrpclib.ServerProxy("http://"+serveradd[0]+":"+str(serveradd[1]),verbose=0)#self.c = zerorpc.Client()
        #self.c.connect(serveradd)
        
        self.state = '0'
        self.vector = [0] * devNum
        
    def leader_elect(self):
        time.sleep(1+random.random())
        address = ('<broadcast>', setting.eleport)
        clt_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        clt_socket.sendto(self.name, address)
        print self.name," sent"
        nextadd, addr = clt_socket.recvfrom(2048)
        tmp = nextadd[1:-1].split(",")
        nextadd = (tmp[0][1:-1],int(tmp[1]))
        print nextadd,addr
        recv_data, preaddr = clt_socket.recvfrom(2048)
        recv_data = recv_data+"#"+str(self._electID)
        clt_socket.sendto(recv_data, nextadd)
        id_data, addr = clt_socket.recvfrom(2048)
        if id_data == "1":
           self._isLeader = 1
        #time.sleep(10)
        print self.name,self._electID,self._isLeader 
        return 1
        
    def time_syn(self):
        if self._isLeader == 1:
            connect_list = []
            syn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            syn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            syn_socket.bind(("127.0.0.1", setting.synport))
            syn_socket.listen(8)
       
            while len(connect_list) < setting.devNum-1:
                sockfd, addr = syn_socket.accept()
                print addr
                connect_list.append(sockfd)
            
            for sk in connect_list:
                sk.send(str(time.time()))
            offsets = []
            ready = []
       
            while len(offsets)< setting.devNum-1:#setting.devNum-1
                read_sockets,write_sockets,error_sockets = select.select(connect_list,[],[])
                for sk in read_sockets:
                    if sk not in ready:
                        of = sk.recv(1024)
                        offsets.append(float(of))
                        ready.append(sk)   
            moffset = sum(offsets)/(len(offsets)+1.0)
            for sk in connect_list:
                sk.send(str(moffset))
            self._timeoffset = moffset
            syn_socket.close()    
        else:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            time.sleep(1+random.random())
            s.connect(("127.0.0.1",setting.synport))
            mt = s.recv(1024)
            offset = time.time()-float(mt)
       
            s.send(str(offset))
            moffset = s.recv(1024)
        
            self._timeoffset = float(moffset) - offset
            s.close()
    def register_to_server(self):
        '''register with the gateway, sending name, type and listening address'''
        
        self.cid = self.c.register(self.ctype,self.name,self.localadd)
        return 1

    def start_listen(self):
        '''To enable communication with the gateway, start a server to catch queries and instructions'''
        self.s = SimpleXMLRPCServer.SimpleXMLRPCServer(self.localadd,logRequests=False)#zerorpc.Server(self)
        self.s.register_instance(self)
        self.s.serve_forever()
        #self.s = zerorpc.Server(self)
        #self.s.bind(self.localadd)
        #self.s.run()

    def query_state(self):
        multicast.multicast(self.localadd, self.vector)
        return self.state

    def set_state(self,state):

        '''set state from test case'''
        self.state = state
        return 1

    def set_state_push(self,state):
        '''set the state of sensor from test case, push to the gateway if state changed'''
        if self.state != state:
            self.state = state
            self.report_to_server()
        return 1

    def report_to_server(self):
        '''Push to the server'''
        
        multicast.multicast(self.localadd, self.vector)
        self.c.report_state(self.cid, self.state)
        return 1

    def update_vector_clock(self,vector):
        for i in range(len(vector)):
            if vector[i] > self.vector[i]:
                self.vector[i] = vector[i]

        self.vector[self.cid] = self.vector[self.cid]+1

        return 1



