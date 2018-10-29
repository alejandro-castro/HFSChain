import os, sys
import getopt
path = os.path.split(os.getcwd())[0]
#path="C://Users//alex//workspace//gui_14_03_13"
sys.path.append(path)

from controller  import *

class scProcessController():
    def __init__(self):
        print "ESTOY EJECUTANDO EL NUEVO PROCESO PERO APARENTEMENTE NO QUIERE"
        self.setfilename()
        self.operation()
   
    def setfilename(self):
        arglist= ''
        longarglist=['filename=']
        optlist,args=getopt.getopt(sys.argv[1:],arglist,longarglist)
        for opt in optlist:
            if opt[0]== '--filename':
               self.filename = opt[1]
            
    def operation(self):
        print 'inicia operation'    
        controllerObj = Project()
        print "Leyendo el archivo XML"
        #self.filename="C://Users//alex//schain_workspace//Alexander1.xml"
        controllerObj.readXml(self.filename)
        #controllerObj.printattr()
    
        controllerObj.createObjects()
        controllerObj.connectObjects()
        controllerObj.run()
  
  
def main():
    a=scProcessController()
  
    
if __name__ == "__main__":
    main()