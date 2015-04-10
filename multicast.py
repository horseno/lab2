import setting
import xmlrpclib 
import SimpleXMLRPCServer

devNum = setting.devNum
addli=[]

addli.append(setting.serveradd)
for i in setting.localadd:
    addli.append(setting.localadd[i])

def multicast(selfadd,vector):
    '''multi-cast to all other users in the group, except for self address'''
    
    for add in addli:
        if add != selfadd:
            c = xmlrpclib.ServerProxy("http://"+add[0]+":"+str(add[1]))
            c.update_vector_clock(vector)

