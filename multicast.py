import setting
import xmlrpclib 
import SimpleXMLRPCServer

#import zerorpc
devNum = setting.devNum
addli=[]

addli.append(setting.serveradd)
for i in setting.localadd:
    addli.append(setting.localadd[i])
#print addli

#addli = ["tcp://0.0.0.0:12000","tcp://0.0.0.0:12001","tcp://0.0.0.0:12002"]

def multicast(selfadd,vector):
    '''multi-cast to all other users in the group, except for self address'''
    
    for add in addli:
        if add != selfadd:
            c = xmlrpclib.ServerProxy("http://"+add[0]+":"+str(add[1]))
            #print "http://"+add[0]+":"+str(add[1])
            #c = zerorpc.Client()
            #c.connect(add)

            c.update_vector_clock(vector)
            #c.close()

    

#multicast(('127.0.0.1', 10003),[5,1,2,3,4,5])