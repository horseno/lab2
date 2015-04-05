#import zerorpc
import sys
sys.path.append("./")
import multicast
import xmlrpclib 
import SimpleXMLRPCServer

class Sensor:
    ''' Represents any senors'''
    def __init__(self,name,serveradd,localadd,devNum):
        '''initialize a sensor, create a client to connect to server'''
        self.name = name
        self.ctype = 'sensor'
        self.localadd = localadd

        self.c = xmlrpclib.ServerProxy("http://"+serveradd[0]+":"+str(serveradd[1]))#self.c = zerorpc.Client()
        #self.c.connect(serveradd)
        
        self.state = '0'
        self.vector = [0] * devNum

    def register_to_server(self):
        '''register with the gateway, sending name, type and listening address'''
        self.cid = self.c.register(self.ctype,self.name,self.localadd)
        return 1

    def start_listen(self):
        '''To enable communication with the gateway, start a server to catch queries and instructions'''
        self.s = SimpleXMLRPCServer.SimpleXMLRPCServer(self.localadd)#zerorpc.Server(self)
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



