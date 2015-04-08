#import zerorpc
import xmlrpclib 
import SimpleXMLRPCServer
import time
import threading
import csv
import socket
import sys
sys.path.append("./")
import setting
import random

#class for user process
class UserProcess(object):
	#initial
    def __init__(self,localadd,devNum):
        self._isLeader = 0
        self._electID = 0.2#random.random()
        self._timeoffset = 0
        
        self._mode = "HOME"
        self._gid = -1 #global id 
        self._localadd = localadd
        self.log=open("user_output.txt",'w+')#output file
        self.vector = [0]* devNum
    def leader_elect(self):
        time.sleep(1+random.random())
        address = ('<broadcast>', setting.eleport)
        clt_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        clt_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        clt_socket.sendto("user", address)
        print "usr sent"
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
        print "user ",self._isLeader 
        return 1
        
    def time_syn(self):
        if self._isLeader == 1:
            connect_list = []
            syn_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            syn_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            syn_socket.bind(("127.0.0.1", setting.synport))
            syn_socket.listen(8)
        #print "server listen"
            while len(connect_list) < 5:
                sockfd, addr = syn_socket.accept()
                print addr
                connect_list.append(sockfd)
            #print "server send"
            for sk in connect_list:
                sk.send(str(time.time()))
            offsets = []
            ready = []
        #print "server receive"
            while len(offsets)< 5:#setting.devNum-1
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
            offset = time.time()+3.0-float(mt)
        #time.sleep(3*random.random())
            s.send(str(offset))
            moffset = s.recv(1024)
        #print "User ",mt,offset,moffset
            self._timeoffset = float(moffset) - offset
            s.close()
        
    #thread for listening 
    def start_listen(self):
        self.s = SimpleXMLRPCServer.SimpleXMLRPCServer(self._localadd,logRequests=False)#zerorpc.Server(self)
        self.s.register_instance(self)
        self.s.serve_forever()
    	#s = zerorpc.Server(self)
        #s.bind(self._localadd)
        #s.run()
    
    #rpc call for register
    def register(self):
        self.c = xmlrpclib.ServerProxy("http://"+setting.serveradd[0]+":"+str(setting.serveradd[1]),verbose=0)
        self._gid = self.c.register("user","user",self._localadd)
    	#c = zerorpc.Client()
        #c.connect(setting.serveradd)
    	#self._gid = c.register("user","user",self._localadd)
    	#c.close()
        return 1
    #rpc interface for text message
    def text_message(self,msg):
        self.log.write(msg+'\n')
        return 1
    #rpc call for change mode 
    def change_mode(self,mode):
        self.c.change_mode(mode)
        self._mode = self.c.change_mode(mode)
     	#c = zerorpc.Client()
        #c.connect(setting.serveradd)
    	#c.change_mode(mode)
        #self._mode = mode
        #c.close()
        return 1

    def update_vector_clock(self,vector):
        for i in range(len(vector)):
            if vector[i] > self.vector[i]:
                self.vector[i] = vector[i]

        self.vector[self._gid] = self.vector[self._gid]+1

        return 1

#thread for listening   			
class user(threading.Thread):
    def __init__(self,user):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self._user = user
    def run(self):
        self._user.start_listen()
#read test case
def readTest(filename,col):
        with open(filename, 'rb') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
            time=[]
            action=[]
            spamreader.next()
            for row in spamreader:
            	#print row,row[0],len(
                time.append(row[0])
                action.append(row[col])     
            return time, action    
        
timel,action = readTest('test-input.csv',4)
devNum = setting.devNum
myuser = UserProcess(setting.localadd["user"],devNum)

myuser.leader_elect()
myuser.time_syn()
listen_thread = user(myuser)
listen_thread.start()


#calculate start time
current_time = int(time.time())
waitT = setting.start_time - current_time
time.sleep(waitT)

if action[0]!='Register':
            print "Error: register client first"
myuser.register()
waitTime = float(timel[1])+float(setting.start_time) - time.time()
if waitTime>0:
    time.sleep(waitTime)
for index in range(1,len(timel)):
    if  action[index] == "HOME" or action[index] == "AWAY":
        if myuser._mode != action[index]:
        	myuser.change_mode(action[index])
    if index+1<len(timel):
        waitTime = float(timel[index+1])+float(setting.start_time) - time.time()
        if waitTime>0:
            time.sleep(waitTime)

