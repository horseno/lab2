#import zerorpc
import xmlrpclib 
import SimpleXMLRPCServer
import csv

class Database:
    '''Backend Database'''
    def __init__(self,Dbadd):
        #store current state and history state in separate files
        self.fname = "dbfile.csv"

        self.s = SimpleXMLRPCServer.SimpleXMLRPCServer(Dbadd)#zerorpc.Server(self)
        self.s.register_instance(self)
        self.s.serve_forever()
    
    def str_to_vector(self,string):
        string = string[1:-1].split(',')
        for i in range(len(string)):
            string[i]= int(string[i])
        return string 

    def write(self, cid, state, timestamp,vector):
        with open(self.fname, 'ab') as f:
            curWriter = csv.writer(f)
            curWriter.writerow([cid,state,timestamp,vector])
        return 1


    def read(self, cid, timestamp):
        '''read the file to get current state/ all the states/ state at a particular time of a device
         timestamp == 0 -> return current state 
         timestamp >0 return state of time indicated by timestamp
         timestamp < 0 return all the state history of the device 
         return values are a list of tuple(state, timestamp)
         '''
        state_l=[]
        maxtime = 0 
        curState = -1
        with open(self.fname, 'rb') as f:
            curReader = csv.reader(f)
            for row in reversed(list(curReader)):
                vector = self.str_to_vector(row[3])
                if int(row[0])==cid:
                    if timestamp < 0:
                        state_l.append((int(row[1]),int(row[2]),vector))
                        #print state_l
                    elif timestamp >0 and timestamp == int(row[2]):
                        state_l.append((int(row[1]),int(row[2]),vector))
                    elif timestamp == 0 and int(row[2])>maxtime:
                        curState = int(row[1]) 
                        maxtime = int(row[2]) 
            if timestamp == 0 and curState != -1:
                state_l.append((curState, maxtime,vector))

            
                        
        return state_l


def main():

    DB = Database("tcp://127.0.0.1:10000")
    a = [1,2,3,4,5,6]
    DB.write(1,1,1234,a)
    DB.write(2,1,1235,a)
    DB.write(1,0,1256,a)
    DB.write(2,1,1259,a)
    
    print DB.read (2,0)


if __name__ == "__main__":
    main()
