'''
Created on June 5, 2012

$Author: dsuarez $
$Id: Controller.py 107 2012-07-10 16:53:45Z dsuarez $
'''

import os
import sys
import datetime
import ConfigParser

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.Voltage import Voltage
from IO.VoltageIO import *

from Model.Spectra import Spectra
from IO.SpectraIO import *

from Processing.VoltageProcessor import *
from Processing.SpectraProcessor import *

class Operation:
    def __init__(self,name,parameters):
        self.name = name
        self.parameters = []
        parametersList = parameters.split(',')
        nparms = len(parametersList)/2
        for id in range(nparms):
            parmtype = parametersList[id*2]
            value = parametersList[id*2+1]
            if value == 'None': 
                value = None
            else:
                if parmtype == 'int': 
                    value = int(value)
                elif parmtype == 'float':
                    value = float(value)
                elif parmtype == 'str':
                    value = str(value)
                elif parmtype == 'datetime':
                    value = value.split('-'); value = numpy.asarray(value,dtype=numpy.int32)
                    value = datetime.datetime(value[0],value[1],value[2],value[3],value[4],value[5])
                else:
                    value = None
            
            self.parameters.append(value)
    

class ExecUnit:
    def __init__(self,):
        self.id = None
        self.type = None
        self.execObjIn = None
        self.execObjOut = None
        self.execProcObj = None
        self.input = None
        self.operationList = []
        self.flagSetIO = False
        
    def setIO(self):
        self.execProcObj.setIO(self.execObjIn,self.execObjOut)
        self.flagSetIO = True
    
    
    def Pfunction(self,name):
        
        def setup(*args):
            inputs = args[0]
            if self.type == 'VoltageReader':
                path = inputs[0]
                startDateTime = inputs[1]
                endDateTime = inputs[2]
                set = inputs[3]
                expLabel = inputs[4]
                ext = inputs[5]
                online = inputs[6]
            
                return self.execProcObj.setup(path,startDateTime,endDateTime,set,expLabel,ext,online)
            
            if self.type == 'Voltage':
                return self.execProcObj.setup()
            
            if self.type == 'Spectra':
                nFFTPoints = inputs[0]
                pairList = inputs[1]
                return self.execProcObj.setup(nFFTPoints,pairList)
            
        def getData(*args):
            
            return self.execProcObj.getData()

        def init(*args):
            inputs = args[0]
            
            parm1 = inputs[0]
            
            if self.type == 'Voltage':
                return self.execProcObj.init()
            
            if self.type == 'Spectra':
                return self.execProcObj.init()
            

        def plotData(*args):
            inputs = args[0]
            
            if self.type == 'Voltage':
                xmin = inputs[0]
                xmax = inputs[1]
                ymin = inputs[2]
                ymax = inputs[3]
                type = inputs[4]
                winTitle = inputs[5]
                index = inputs[6]
                
                return self.execProcObj.plotData(xmin,xmax,ymin,ymax,type,winTitle,index)
            
            if self.type == 'Spectra':
                xmin = inputs[0]
                xmax = inputs[1]
                ymin = inputs[2]
                ymax = inputs[3]
                winTitle = inputs[4]
                index = inputs[5]
                
                return self.execProcObj.plotData(xmin,xmax,ymin,ymax,winTitle,index)
        
        def integrator(*args):
            inputs = args[0]
            N = inputs[0]
            timeInterval = inputs[1]
            self.execProcObj.integrator(N, timeInterval)
                    
        pfuncDict = {   "setup":    setup, 
                        "getdata":  getData, 
                        "init":     init,
                        "plotdata": plotData,
                        "integrator":   integrator} 
        
        return pfuncDict[name]
    
    
    def run(self):
        nopers = len(self.operationList)
        for idOper in range(nopers):
            operObj = self.operationList[idOper]
            self.Pfunction(operObj.name)(operObj.parameters)
            
            
class Controller:
    
    def __init__(self):
        self.sectionList = None
        self.execUnitList = None
        self.execObjList = None
        self.readConfigFile()
        self.createObjects()
        self.setupOjects()
        self.start()
    
    def readConfigFile(self, filename='experiment.cfg'):
        
        parser = ConfigParser.SafeConfigParser()
        parser.read(filename)
        self.sectionList = parser.sections()
        self.execUnitList = []
        
        for section_name in  self.sectionList:
            itemList = parser.items(section_name)
            self.execUnitList.append(itemList)
        
        print 
    
    def createObjects(self):
        self.execObjList = []
        
        for itemList in self.execUnitList:
            execObj = ExecUnit()
            for item in itemList:
                name, value = item[0], item[1]
                
                if name == 'id':
                    execObj.id = int(value)
                    continue
                
                if name == 'type':
                    execObj.type = value
                    
                    if value == 'VoltageReader':
                        execObj.execObjOut = Voltage()
                        execObj.execProcObj = VoltageReader(execObj.execObjOut)
                        

                    if value == 'SpectraReader':
                        execObj.execObjOut = Spectra()
                        execObj.execProcObj = SpectraReader(execObj.execObjOut)
                        
                        
                    if value == 'CorrelationReader':
                        execObj.execObjOut = Correlation()
                        execObj.execProcObj = CorrelationReader(execObj.execObjOut)
                        
                        
                    if value == 'Voltage':
                        execObj.execProcObj = VoltageProcessor()
                        execObj.execObjOut = Voltage()

                    if value == 'Spectra':
                        execObj.execProcObj = SpectraProcessor()
                        execObj.execObjOut = Spectra()

                    if value == 'Correlation':
                        execObj.execProcObj = CorrelationProcessor() 
                        execObj.execObjOut = Correlation() 
                        
                elif name == 'input':
                    execObj.input = int(value)
                
                else:
                    operObj = Operation(name,value)
                    
                    if name != 'setup':
                        execObj.operationList.append(operObj)
                    else:
                        execObj.Pfunction(name)(operObj.parameters)
                    
                    del(operObj)
            
            self.execObjList.append(execObj)   
            del(execObj)
                
            
   
    def setupOjects(self):
        for objIndex in range(len(self.execObjList)):
            currExecObj = self.execObjList[objIndex]
            
            if not(currExecObj.type in ['VoltageReader','SpectraReader','CorrelationReader']):
            
                idSearch = currExecObj.input
                
                for objIndex2 in range(len(self.execObjList)):
                
                    lastExecObj = self.execObjList[objIndex2] # este objeto si puede ser un readerl
                    
                    if lastExecObj.id == idSearch and currExecObj.flagSetIO == False:
                        currExecObj.execObjIn = lastExecObj.execObjOut
                        currExecObj.setIO()
                        

        
        
                        
        
    def start(self):

        while(True):
            for indexObj in range(len(self.execObjList)):
                 ExecObj = self.execObjList[indexObj]
                 ExecObj.run()
                    
            readExecObj = self.execObjList[0] # se asume que el primer elemento es un Reader
            if readExecObj.execProcObj.flagNoMoreFiles:
                break
            if readExecObj.execProcObj.flagIsNewBlock:
                print 'Block No %04d, Time: %s' %(readExecObj.execProcObj.nTotalBlocks,
                                                  datetime.datetime.fromtimestamp(readExecObj.execProcObj.m_BasicHeader.utc),)


            
            
if __name__ == '__main__':
    Controller()
    