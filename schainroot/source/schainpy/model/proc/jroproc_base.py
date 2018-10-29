'''
'''

class ProcessingUnit:
    
    """
    Esta es la clase base para el procesamiento de datos.
    
    Contiene el metodo "call" para llamar operaciones. Las operaciones pueden ser:
        - Metodos internos (callMethod)
        - Objetos del tipo Operation (callObject). Antes de ser llamados, estos objetos
          tienen que ser agreagados con el metodo "add".
    
    """
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataIn = None
    dataInList = []
    
    # objeto de datos de entrada (Voltage, Spectra o Correlation)
    dataOut = None
    
    operations2RunDict = None
    
    isConfig = False
    
    
    def __init__(self):
        
        self.dataIn = None
        self.dataInList = []
        
        self.dataOut = {}
        
        self.operations2RunDict = {}
        
        self.isConfig = False
            
    def addOperation(self, opObj, objId):
        
        """
        Agrega un objeto del tipo "Operation" (opObj) a la lista de objetos "self.objectList" y retorna el
        identificador asociado a este objeto. 
        
        Input:
        
            object    :    objeto de la clase "Operation"
        
        Return:
            
            objId    :    identificador del objeto, necesario para ejecutar la operacion
        """
        
        self.operations2RunDict[objId] = opObj
        
        return objId
    
    def operation(self, **kwargs):
        
        """
        Operacion directa sobre la data (dataOut.data). Es necesario actualizar los valores de los
        atributos del objeto dataOut
        
        Input:
        
            **kwargs    :    Diccionario de argumentos de la funcion a ejecutar
        """
        
        raise ValueError, "ImplementedError"
    
    def callMethod(self, name, **kwargs):
        
        """
        Ejecuta el metodo con el nombre "name" y con argumentos **kwargs de la propia clase.
        
        Input:
            name        :    nombre del metodo a ejecutar
            
            **kwargs     :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        """
        if name == 'run':
            
            if not self.checkInputs():
                self.dataOut.flagNoData = True
                return False
        else:
            #Si no es un metodo RUN la entrada es la misma dataOut (interna)
            if self.dataOut.isEmpty():
                return False
        
        #Getting the pointer to method
        methodToCall = getattr(self, name)
        
        #Executing the self method
        methodToCall(**kwargs)
        
        #Checkin the outputs
        
#         if name == 'run':
#             pass
#         else:
#             pass
#         
#         if name != 'run':
#             return True
         
        if self.dataOut.isEmpty():
            return False
        
        return True
    
    def callObject(self, objId, **kwargs):
        
        """
        Ejecuta la operacion asociada al identificador del objeto "objId"
        
        Input:
            
            objId        :    identificador del objeto a ejecutar
            
            **kwargs    :    diccionario con los nombres y valores de la funcion a ejecutar.
        
        Return:
            
            None    
        """
        
        if self.dataOut.isEmpty():
            return False
        
        externalProcObj = self.operations2RunDict[objId]
        
        externalProcObj.run(self.dataOut, **kwargs)
        
        return True
    
    def call(self, opType, opName=None, opId=None, **kwargs):
        
        """
        Return True si ejecuta la operacion "operationConf.name" con los
        argumentos "**kwargs". False si la operacion no se ha ejecutado.
        La operacion puede ser de dos tipos:
        
            1. Un metodo propio de esta clase:
                
                operation.type = "self"
            
            2. El metodo "run" de un objeto del tipo Operation o de un derivado de ella:
                operation.type = "other".
                
               Este objeto de tipo Operation debe de haber sido agregado antes con el metodo:
               "addOperation" e identificado con el operation.id
               
            
        con el id de la operacion.
        
        Input:
        
            Operation    :    Objeto del tipo operacion con los atributos: name, type y id.
            
        """
        
        if opType == 'self':
            
            if not opName:
                raise IOError, "opName parameter should be defined"
            
            sts = self.callMethod(opName, **kwargs)
        
        if opType == 'other' or opType == 'external':
            
            if not opId:
                raise IOError, "opId parameter should be defined"
            
            if opId not in self.operations2RunDict.keys():
                raise IOError, "This id operation have not been registered"
            
            sts = self.callObject(opId, **kwargs)
        
        return sts 
    
    def setInput(self, dataIn):
        
        self.dataIn = dataIn
        self.dataInList.append(dataIn)
    
    def getOutputObj(self):
        
        return self.dataOut
    
    def checkInputs(self):
        
        for thisDataIn in self.dataInList:
            
            if thisDataIn.isEmpty():
                return False
        
        return True
    
    def setup(self):
        
        raise ValueError, "Not implemented"
    
    def run(self):
        
        raise ValueError, "Not implemented"
        
class Operation():
    
    """
    Clase base para definir las operaciones adicionales que se pueden agregar a la clase ProcessingUnit
    y necesiten acumular informacion previa de los datos a procesar. De preferencia usar un buffer de
    acumulacion dentro de esta clase
    
    Ejemplo: Integraciones coherentes, necesita la informacion previa de los n perfiles anteriores (bufffer)
    
    """
    
    __buffer = None
    isConfig = False
    
    def __init__(self):
        
        self.__buffer = None
        self.isConfig = False
    
    def setup(self):
        
        self.isConfig = True
        
        raise ValueError, "Not implemented"

    def run(self, dataIn, **kwargs):
        
        """
        Realiza las operaciones necesarias sobre la dataIn.data y actualiza los atributos del objeto dataIn.
        
        Input:
        
            dataIn    :    objeto del tipo JROData
        
        Return:
            
            None
        
        Affected:
            __buffer    :    buffer de recepcion de datos.
            
        """
        if not self.isConfig:
            self.setup(**kwargs)
            
        raise ValueError, "ImplementedError"