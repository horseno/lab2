import zerorpc
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

        self.c = zerorpc.Client()
        self.c.connect(serveradd)

        self.state = '1'

    def register_to_server(self):
        '''register with the gateway, sending name, type and listening address'''
        self.cid = self.c.register(self.ctype,self.name,self.localadd)   
    
    
    def start_listen(self):
        '''To enable communication with the gateway, start a server to catch queries and instructions'''
        self.s = zerorpc.Server(self)
        self.s.bind(self.localadd)
        self.s.run()

    def query_state(self):
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
    

        