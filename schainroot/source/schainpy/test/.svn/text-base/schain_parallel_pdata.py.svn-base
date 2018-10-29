from mpi4py import MPI
import datetime
import os, sys
#import timeit

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from controller import *

def conversion(x1,x2):
    a=[x1,x2]
    for x in a:
        m,s = divmod(x,60)
        h,m = divmod(m,60)
        if x==x1:
            startime= str("%02d:%02d:%02d" % (h, m, s))
        if x==x2:
            endtime =str("%02d:%02d:%02d" % (h, m, s))
    return startime,endtime



def loop(startime,endtime,rank,size):
    desc = "HF_EXAMPLE"+str(rank)
    path= "/media/Data_HF/HFA/hfdata_d2015252_d2015328/procdata"
    savepath= "/home/alex/Documents/pdata_parallel"
    #+str(rank)

    filename = "hf_test"+str(rank)+".xml"
    
    controllerObj = Project()
    
    controllerObj.setup(id = '191', name='test01'+str(rank), description=desc)
# 
# 
    readUnitConfObj = controllerObj.addReadUnit(datatype='HFReader',
                                                path=path,
                                                frequency=2.72,
                                                startDate='2015/09/26',#0810
                                                endDate='2015/09/26',#0825
                                                startTime=startime,
                                                endTime=endtime,
                                                online=0,
                                                #delay=20,
                                                walk=0,
                                                timezone=-5*3600)
    
    procUnitConfObj0 = controllerObj.addProcUnit(datatype='VoltageProc', inputId=readUnitConfObj.getId())
# 
    opObj12 = procUnitConfObj0.addOperation(name='setRadarFrequency')
    opObj12.addParameter(name='frequency', value='2.72e6', format='float')
      
    procUnitConfObj1 = controllerObj.addProcUnit(datatype='SpectraProc', inputId=procUnitConfObj0.getId())
    procUnitConfObj1.addParameter(name='nFFTPoints', value='100', format='int')
    procUnitConfObj1.addParameter(name='nProfiles', value='100', format='int')
    procUnitConfObj1.addParameter(name='pairsList', value='(0,1)', format='pairsList')
 
    opObj11 = procUnitConfObj1.addOperation(name='IncohInt', optype='other')
    opObj11.addParameter(name='n', value='6', format='float')
#     
    opObj11 = procUnitConfObj1.addOperation(name='SpectraWriter', optype='other')
    opObj11.addParameter(name='path', value=savepath)
    opObj11.addParameter(name='blocksPerFile', value='2', format='int')
    opObj11.addParameter(name='rank', value=rank, format='int')
    opObj11.addParameter(name='cpu', value=size, format='int')
     
    print "Escribiendo el archivo XML"
    controllerObj.writeXml(filename)
    print "Leyendo el archivo XML"
    controllerObj.readXml(filename)
    
    controllerObj.createObjects()
    controllerObj.connectObjects()
    
    #timeit.timeit('controllerObj.run()', number=2)
    
    controllerObj.run()

    

def parallel():
    
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()  
    totalStartTime = time.time()
    print "Hello world from process %d/%d"%(rank,size)
    # First just for one day :D!
    num_hours = 24/size
    time1,time2 = rank*num_hours*3600,(rank+1)*num_hours*3600-60
    #print time1,time2
    startime,endtime =conversion(time1,time2)
    print startime,endtime
    loop(startime,endtime,rank,size)
    print "Total time %f seconds" %(time.time() -totalStartTime)

if __name__=='__main__':
    parallel()