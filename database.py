import zerorpc
import csv
class Database:
    '''Backend Database'''
    def __init__(self,Dbadd):
        #store current state and history state in separate files
        self.fname = "current.csv"
    
        self.s = zerorpc.Server(self)
        self.s.bind(Dbadd)
        self.s.run()

    def write(self, cid, state, timestamp):
        with open(self.fname, 'ab') as f:
            curWriter = csv.writer(f)
            curWriter.writerow([cid,state,timestamp])



    def read(self, cid, state, timestamp):
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
                
                if int(row[0])==cid:
                    if timestamp < 0:
                        state_l.append((int(row[1]),int(row[2])))
                        #print state_l
                    elif timestamp >0 and timestamp == int(row[2]):
                        state_l.append((int(row[1]),int(row[2])))
                    elif timestamp == 0 and int(row[2])>maxtime:
                        curState = int(row[1]) 
                        maxtime = int(row[2]) 
            if timestamp == 0:
                state_l.append((curState, maxtime))

                        
        return state_l






def main():

    DB = Database("tcp://127.0.0.1:10000")
    DB.write(1,1,1234)
    DB.write(2,1,1235)
    DB.write(1,0,1256)
    DB.write(2,1,1259)
    
    print DB.read (2,1,0)


if __name__ == "__main__":
    main()
