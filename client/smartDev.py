#import zerorpc
import xmlrpclib 
import SimpleXMLRPCServer
import time
import sys
sys.path.append("./")
import setting

class SmartDev:
    ''' Represents any smart device'''
    def __init__(self,name,serveradd,localadd):
        self.name = name
        self.ctype = 'device'
        self.localadd = localadd
        self.c = xmlrpclib.ServerProxy("http://"+serveradd[0]+":"+str(serveradd[1]))
        #self.c = zerorpc.Client()
        #self.c.connect(serveradd)

        self.state = '1'

    def register_to_server(self):
        '''register with the gateway, sending name, type and listening address'''
        self.cid = self.c.register(self.ctype,self.name,self.localadd)   
    
    
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
        '''function used to debug and test'''
        self.state = state

    def change_state(self, state):
        '''change state according to the request of the gateway, write change to file'''
        self.state = state
        cur_t = time.time()
        timestamp = round(cur_t - setting.start_time, 2)
        filename = "devout-" + self.name + '.txt' 
        content = str(timestamp) + ',' + str(self.state)+ '\n'
        with open(filename, 'a') as f:
            f.write(content)
        return 1

    def update_vector_clock(self,vector):
        for i in range(len(vector)):
            if vector[i] > self.vector[i]:
                self.vector[i] = vector[i]

        self.vector[self.cid] = self.vector[self.cid]+1

        