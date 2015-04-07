#import zerorpc
import xmlrpclib 
import SimpleXMLRPCServer
import time
import csv
import sys
sys.path.append("./")
import setting

def compare_float(f1, f2):
    return abs(f1 - f2) <= 0.001

class Database:
    '''Backend Database'''
    def __init__(self,Dbadd):
        #store current state and history state in separate files
        self.fname = "dbfile.csv"
        self.s = SimpleXMLRPCServer.SimpleXMLRPCServer(Dbadd)#zerorpc.Server(self)
        self.s.register_instance(self)
        #self.s.serve_forever()
    
    def str_to_vector(self,string):
        string = string[1:-1].split(',')
        for i in range(len(string)):
            string[i]= int(string[i])
        return string 

    def write(self, cid, state, timestamp,vector):
        print "#$^$#"
        with open(self.fname, 'ab') as f:
            curWriter = csv.writer(f)
            curWriter.writerow([cid,state,timestamp,vector])
        return 1
        
    def time_syn(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        time.sleep(1+random.random())
        s.connect(("127.0.0.1",setting.synport))
        mt = s.recv(1024)
        offset = time.time()-10.0-float(mt)
        #time.sleep(3*random.random())
        s.send(str(offset))
        moffset = s.recv(1024)
        print "sensor ",self.name,mt,offset,moffset
        self._timeoffset = float(moffset) - offset
        s.close()

    def read(self, cid, timestamp):
        '''read the file to get current state/ all the states/ state at a particular time of a device
         timestamp == 0 -> return current state 
         timestamp >0 return state of time indicated by timestamp
         timestamp < 0 return all the state history of the device 
         return values are a list of tuple(state, timestamp)
         '''
        state_l=[]
        maxtime = 0 
        curState = '-1'
        with open(self.fname, 'rb') as f:
            curReader = csv.reader(f)
            for row in reversed(list(curReader)):
                qid = row[0]
                vector = self.str_to_vector(row[3])
                state = str(row[1])
                time = float(row[2])
                if int(qid)==cid:
                    if timestamp < 0:
                        state_l.append((state,time,vector))
                        #print state_l
                    elif timestamp >0 and compare_float(timestamp,time):
                        state_l.append((state,time,vector))
                    elif compare_float(timestamp,0) and time>maxtime:
                        curState = state
                        maxtime = time 
            if compare_float(timestamp,0) and curState != '-1':
                state_l.append((curState, maxtime,vector))

                        
        return state_l


def main():

    DB = Database(setting.Dbadd)
    DB.s.serve_forever()
    print "serve forever!!!!!!\n"
    a = [1,2,3,4,5,6]
    DB.write(1,1,1234,a)
    DB.write(2,1,1235,a)
    DB.write(1,0,1256,a)
    DB.write(2,1,1259,a)
    
    print DB.read (2,-1)
    time.sleep(30)

if __name__ == "__main__":
    main()
