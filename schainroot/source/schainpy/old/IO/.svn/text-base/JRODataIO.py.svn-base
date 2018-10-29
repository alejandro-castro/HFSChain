'''
Created on 23/01/2012

@author $Author: murco $
@version $Id: JRODataIO.py 172 2012-11-20 14:53:43Z murco $
@version $Id: JRODataIO.py 172 2012-11-20 14:53:43Z murco $
'''

import os, sys
import glob
import time
import numpy
import fnmatch
import time, datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Model.JROHeader import *
from Model.JROData import JROData

def checkForRealPath(path, year, doy, set, ext):
    """
    Por ser Linux Case Sensitive entonces checkForRealPath encuentra el nombre correcto de un path,
    Prueba por varias combinaciones de nombres entre mayusculas y minusculas para determinar
    el path exacto de un determinado file.
    
    Example    :
        nombre correcto del file es  .../.../D2009307/P2009307367.ext
        
        Entonces la funcion prueba con las siguientes combinaciones
            .../.../x2009307/y2009307367.ext
            .../.../x2009307/Y2009307367.ext
            .../.../X2009307/y2009307367.ext
            .../.../X2009307/Y2009307367.ext
        siendo para este caso, la ultima combinacion de letras, identica al file buscado 
        
    Return:
        Si encuentra la cobinacion adecuada devuelve el path completo y el nombre del file 
        caso contrario devuelve None como path y el la ultima combinacion de nombre en mayusculas 
        para el filename  
    """
    filepath = None
    find_flag = False
    filename = None

    if ext.lower() == ".r": #voltage
        header1 = "dD"
        header2 = "dD"
    elif ext.lower() == ".pdata": #spectra
        header1 = "dD"
        header2 = "pP"
    else:
        return None, filename
            
    for dir in header1: #barrido por las dos combinaciones posibles de "D"
        for fil in header2: #barrido por las dos combinaciones posibles de "D"
            doypath = "%s%04d%03d" % ( dir, year, doy ) #formo el nombre del directorio xYYYYDDD (x=d o x=D)
            filename = "%s%04d%03d%03d%s" % ( fil, year, doy, set, ext ) #formo el nombre del file xYYYYDDDSSS.ext
            filepath = os.path.join( path, doypath, filename ) #formo el path completo
            if os.path.exists( filepath ): #verifico que exista
                find_flag = True
                break
        if find_flag:
            break

    if not(find_flag):
        return None, filename

    return filepath, filename


def isNumber(str):
    """
    Chequea si el conjunto de caracteres que componen un string puede ser convertidos a un numero.

    Excepciones: 
        Si un determinado string no puede ser convertido a numero
    Input:
        str, string al cual se le analiza para determinar si convertible a un numero o no
        
    Return:
        True    :    si el string es uno numerico
        False   :    no es un string numerico
    """
    try:
        float( str )
        return True
    except:
        return False


def isThisFileinRange(filename, startUTSeconds, endUTSeconds):
    """
    Esta funcion determina si un archivo de datos se encuentra o no dentro del rango de fecha especificado.
    
    Inputs:
        filename            :    nombre completo del archivo de datos en formato Jicamarca (.r)
        
        startUTSeconds      :    fecha inicial del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
        endUTSeconds        :    fecha final del rango seleccionado. La fecha esta dada en
                                 segundos contados desde 01/01/1970.
    
    Return:
        Boolean    :    Retorna True si el archivo de datos contiene datos en el rango de
                        fecha especificado, de lo contrario retorna False.
    
    Excepciones:
        Si el archivo no existe o no puede ser abierto
        Si la cabecera no puede ser leida.
        
    """
    m_BasicHeader = BasicHeader()
    
    try:
        fp = open(filename,'rb')
    except:
        raise IOError, "The file %s can't be opened" %(filename)
    
    sts = m_BasicHeader.read(fp)
    fp.close()
    
    if not(sts):
        print "Skipping the file %s because it has not a valid header" %(filename)
        return 0
    
    if not ((startUTSeconds <= m_BasicHeader.utc) and (endUTSeconds > m_BasicHeader.utc)):
        return 0
    
    return 1

        
def getlastFileFromPath(path, ext):
    """
    Depura el fileList dejando solo los que cumplan el formato de "PYYYYDDDSSS.ext"
    al final de la depuracion devuelve el ultimo file de la lista que quedo.  
    
    Input: 
        fileList    :    lista conteniendo todos los files (sin path) que componen una determinada carpeta
        ext         :    extension de los files contenidos en una carpeta 
            
    Return:
        El ultimo file de una determinada carpeta, no se considera el path.
    """
    validFilelist = []
    fileList = os.listdir(path)
    
    # 0 1234 567 89A BCDE
    # H YYYY DDD SSS .ext
    
    for file in fileList:
        try:
            year = int(file[1:5])
            doy  = int(file[5:8])
        
            if (os.path.splitext(file)[-1].upper() != ext.upper()) : continue
        except:
            continue

        validFilelist.append(file)

    if validFilelist:
        validFilelist = sorted( validFilelist, key=str.lower )
        return validFilelist[-1]

    return None

class JRODataIO:
    
    #speed of light
    c = 3E8
    
    m_BasicHeader = BasicHeader()
    
    systemHeaderObj = SystemHeader()
    
    radarControllerHeaderObj = RadarControllerHeader()
    
    m_ProcessingHeader = ProcessingHeader()
    
    dataOutObj = None
    
    online = 0
    
    fp = None
    
    dataType = None
    
    fileSizeByHeader = None
    
    filenameList = []
    
    filename = None
    
    fileSize = None
    
    firstHeaderSize = 0
    
    basicHeaderSize = 24
    
    nTotalBlocks = 0

    ippSeconds = 0
    
    blocksize = 0
    
    set = 0
    
    ext = None
    
    path = None
    
    maxTimeStep = 30
    
    
    delay  = 3   #seconds
    
    nTries  = 3  #quantity tries
    
    nFiles = 3   #number of files for searching    
    
    
    flagNoMoreFiles = 0
    
    flagIsNewFile = 1
    
    flagResetProcessing = 0    

    flagIsNewBlock = 0
    
    def __init__(self):
        pass
    
class JRODataReader(JRODataIO):
    
    """
    Esta clase es usada como la clase padre de las clases VoltageReader y SpectraReader.
    Contiene todos lo metodos necesarios para leer datos desde archivos en formato
    jicamarca o pdata (.r o .pdata). La lectura de los datos siempre se realiza por bloques. Los datos
    leidos son array de 3 dimensiones:

                      Para Voltajes  -  perfiles * alturas * canales  
                                        
                      Para Spectra   -  paresCanalesIguales    * alturas * perfiles  (Self Spectra)
                                        paresCanalesDiferentes * alturas * perfiles  (Cross Spectra)
                                        canales * alturas                            (DC Channels)
        
    y son almacenados en su buffer respectivo.
     
    Esta clase contiene instancias (objetos) de las clases BasicHeader, SystemHeader, 
    RadarControllerHeader y DataObj. Los tres primeros se usan para almacenar informacion de la
    cabecera de datos (metadata), y el cuarto (DataObj) para obtener y almacenar los datos desde
    el buffer de datos cada vez que se ejecute el metodo "getData".
    """
    
    nReadBlocks = 0
    
    def __init__(self, dataOutObj=None):
        
        raise ValueError, "This class can't be instanced"


    def hasNotDataInBuffer(self):
        
        raise ValueError, "Not implemented"
    
    def getBlockDimension(self):
        
        raise ValueError, "No implemented"
    
    def readBlock(self):
        
        self.nTotalBlocks += 1
        self.nReadBlocks += 1
        
        raise ValueError, "This method has not been implemented"
    
    def getData( self ):
        
        raise ValueError, "This method has not been implemented"

    def createObjByDefault(self):
        """
        Los objetos creados por defecto por cada clase (Voltaje o Espectro) difieren en el tipo
        raise ValueError, "This method has not been implemented
        """
        raise ValueError, "This method has not been implemented"
        
#    def setup(self, dataOutObj=None, path=None, startDateTime=None, endDateTime=None, set=0, expLabel = "", ext = None, online = 0):
    
    def __searchFilesOnLine(self, path, expLabel = "", ext = None, startDate=None, endDate=None, startTime=None, endTime=None):
        """
        Busca el ultimo archivo de la ultima carpeta (determinada o no por startDateTime) y
        devuelve el archivo encontrado ademas de otros datos.
        
        Input: 
            path           :    carpeta donde estan contenidos los files que contiene data
            
            startDate      :    Fecha inicial. Rechaza todos los directorios donde 
                                file end time < startDate (obejto datetime.date)
                                                         
            endDate        :    Fecha final. Rechaza todos los directorios donde 
                                file start time > endDate (obejto datetime.date)
            
            startTime      :    Tiempo inicial. Rechaza todos los archivos donde 
                                file end time < startTime (obejto datetime.time)
                                                         
            endTime        :    Tiempo final. Rechaza todos los archivos donde 
                                file start time > endTime (obejto datetime.time)
                                
            ext              :    extension de los files  

        Return:
            directory   :    eL directorio donde esta el file encontrado
            filename    :    el ultimo file de una determinada carpeta
            year        :    el anho
            doy         :    el numero de dia del anho
            set         :    el set del archivo
            
            
        """
        dirList = []
        pathList = []
        directory = None
        
        #Filtra solo los directorios
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path, thisPath)):
                dirList.append(thisPath)

        if not(dirList):
            return None, None, None, None, None

        dirList = sorted( dirList, key=str.lower )

        if startDate:
            startDateTime = datetime.datetime.combine(startDate, startTime)
            thisDateTime = startDateTime
            if endDate == None: endDateTime = startDateTime
            else: endDateTime = datetime.datetime.combine(endDate, endTime)
            
            while(thisDateTime <= endDateTime):
                year = thisDateTime.timetuple().tm_year
                doy = thisDateTime.timetuple().tm_yday
                
                match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
                if len(match) == 0:
                    thisDateTime += datetime.timedelta(1)
                    continue
                
                pathList.append(os.path.join(path,match[0], expLabel))
                thisDateTime += datetime.timedelta(1)

            if not(pathList):
                print "\tNo files in range: %s - %s" %(startDateTime.ctime(), endDateTime.ctime())
                return None, None, None, None, None

            directory = pathList[0]
            
        else:
            directory = dirList[-1]
            directory = os.path.join(path,directory)

        filename = getlastFileFromPath(directory, ext)

        if not(filename):
            return None, None, None, None, None

        if not(self.__verifyFile(os.path.join(directory, filename))):
            return None, None, None, None, None

        year = int( filename[1:5] )
        doy  = int( filename[5:8] )
        set  = int( filename[8:11] )        
        
        return directory, filename, year, doy, set


    def __searchFilesOffLine(self, path, startDate, endDate, startTime=datetime.time(0,0,0), endTime=datetime.time(23,59,59),set=None, expLabel = "", ext = ".r"):
        """
        Realiza una busqueda de los archivos que coincidan con los parametros
        especificados y se encuentren ubicados en el path indicado. Para realizar una busqueda
        correcta la estructura de directorios debe ser la siguiente:
        
        ...path/D[yyyy][ddd]/expLabel/D[yyyy][ddd][sss].ext
        
        [yyyy]: anio
        [ddd] : dia del anio
        [sss] : set del archivo        
        
        Inputs:
            path           :    Directorio de datos donde se realizara la busqueda. Todos los
                                ficheros que concidan con el criterio de busqueda seran
                                almacenados en una lista y luego retornados.
            startDate      :    Fecha inicial. Rechaza todos los directorios donde 
                                file end time < startDate (obejto datetime.date)
                                                         
            endDate        :    Fecha final. Rechaza todos los directorios donde 
                                file start time > endDate (obejto datetime.date)
            
            startTime      :    Tiempo inicial. Rechaza todos los archivos donde 
                                file end time < startTime (obejto datetime.time)
                                                         
            endTime        :    Tiempo final. Rechaza todos los archivos donde 
                                file start time > endTime (obejto datetime.time)
                                
            set            :    Set del primer archivo a leer. Por defecto None
            
            expLabel       :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext            :    Extension de los archivos a leer. Por defecto .r
            
        Return:
            
            (pathList, filenameList)
            
            pathList        :    Lista de directorios donde se encontraron archivos dentro 
                                 de los parametros especificados
            filenameList    :    Lista de archivos (ruta completa) que coincidieron con los
                                 parametros especificados.
        
        Variables afectadas:
        
            self.filenameList:    Lista de archivos (ruta completa) que la clase utiliza
                                  como fuente para leer los bloque de datos, si se termina
                                  de leer todos los bloques de datos de un determinado 
                                  archivo se pasa al siguiente archivo de la lista.
             
        Excepciones:
        
        """
        
        dirList = []
        for thisPath in os.listdir(path):
            if os.path.isdir(os.path.join(path,thisPath)):
                dirList.append(thisPath)

        if not(dirList):
            return None, None

        pathList = []
        dateList = []
        
        thisDate = startDate
        
        while(thisDate <= endDate):
            year = thisDate.timetuple().tm_year
            doy = thisDate.timetuple().tm_yday
            
            match = fnmatch.filter(dirList, '?' + '%4.4d%3.3d' % (year,doy))
            if len(match) == 0:
                thisDate += datetime.timedelta(1)
                continue
            
            pathList.append(os.path.join(path,match[0],expLabel))
            dateList.append(thisDate)
            thisDate += datetime.timedelta(1)
        
        filenameList = []
        for index in range(len(pathList)):
            
            thisPath = pathList[index]
            fileList = glob.glob1(thisPath, "*%s" %ext)
            fileList.sort()
            
            #Busqueda de datos en el rango de horas indicados
            thisDate = dateList[index]
            startDT = datetime.datetime.combine(thisDate, startTime)
            endDT = datetime.datetime.combine(thisDate, endTime)
            
            startUtSeconds = time.mktime(startDT.timetuple())
            endUtSeconds = time.mktime(endDT.timetuple())
            
            for file in fileList:
                
                filename = os.path.join(thisPath,file)
                
                if isThisFileinRange(filename, startUtSeconds, endUtSeconds):
                    filenameList.append(filename)
                    
        if not(filenameList):
            return None, None

        self.filenameList = filenameList
        
        return pathList, filenameList
        
    def setup(self, dataOutObj=None, path=None, startDate=None, endDate=None, startTime=datetime.time(0,0,0), endTime=datetime.time(23,59,59), set=0, expLabel = "", ext = None, online = 0):
        """
        setup configura los parametros de lectura de la clase DataReader.
        
        Si el modo de lectura es offline, primero se realiza una busqueda de todos los archivos
        que coincidan con los parametros especificados; esta lista de archivos son almacenados en
        self.filenameList.
        
        Input:
            path                :    Directorios donde se ubican los datos a leer. Dentro de este
                                     directorio deberia de estar subdirectorios de la forma:
                                     
                                     path/D[yyyy][ddd]/expLabel/P[yyyy][ddd][sss][ext]
            
            startDate      :    Fecha inicial. Rechaza todos los directorios donde 
                                file end time < startDate (obejto datetime.date)
                                                         
            endDate        :    Fecha final. Rechaza todos los directorios donde 
                                file start time > endDate (obejto datetime.date)
            
            startTime      :    Tiempo inicial. Rechaza todos los archivos donde 
                                file end time < startTime (obejto datetime.time)
                                                         
            endTime        :    Tiempo final. Rechaza todos los archivos donde 
                                file start time > endTime (obejto datetime.time)
            
            set                 :    Set del primer archivo a leer. Por defecto None
            
            expLabel            :    Nombre del subdirectorio de datos.  Por defecto ""
            
            ext                 :    Extension de los archivos a leer. Por defecto .r
            
            online              :    Si es == a 0 entonces busca files que cumplan con las condiciones dadas
            
        Return:
            0    :    Si no encuentra files que cumplan con las condiciones dadas
            1    :    Si encuentra files que cumplan con las condiciones dadas
        
        Affected:
            self.startYear 
            self.endYear
            self.startDoy
            self.endDoy
            self.pathList
            self.filenameList 
            self.online
        """
        if path == None:
            raise ValueError, "The path is not valid"
        
        if ext == None:
            ext = self.ext
        
        if dataOutObj == None:
            dataOutObj = self.createObjByDefault()
        
        self.dataOutObj = dataOutObj
            
        if online:
            print "Searching files in online mode..."  
            doypath, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=exp)        

            if not(doypath):
                for nTries in range( self.nTries ):
                    print '\tWaiting %0.2f sec for valid file in %s: try %02d ...' % (self.delay, path, nTries+1)
                    time.sleep( self.delay )
                    doypath, file, year, doy, set = self.__searchFilesOnLine(path=path, expLabel=expLabel, ext=exp)        
                    if doypath:
                        break
            
            if not(doypath):
                print "There 'isn't valied files in %s" % path
                return None
        
            self.year = year
            self.doy  = doy
            self.set  = set - 1
            self.path = path

        else: # offline
            print "Searching files in offline mode..."
            pathList, filenameList = self.__searchFilesOffLine(path, startDate, endDate, startTime, endTime, set, expLabel, ext)
            if not(pathList):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
                return None

            self.fileIndex = -1 
            self.pathList = pathList
            self.filenameList = filenameList
             
        self.online = online
        self.ext = ext

        ext = ext.lower()

        if not( self.setNextFile() ):
            if (startDate != None) and (endDate != None):
                print "No files in range: %s - %s" %(datetime.datetime.combine(startDate,startTime).ctime(), datetime.datetime.combine(endDate,endTime).ctime())
                
            elif startDate != None:
                print "No files in : %s" % datetime.datetime.combine(startDate,startTime).ctime()
            else:
                print "No files"
            return None
        
        #call fillHeaderValues() - to Data Object
        
        self.updateDataHeader()
            
        return self.dataOutObj
    
    def __rdSystemHeader(self, fp=None):
        
        if fp == None:
            fp = self.fp
            
        self.systemHeaderObj.read(fp)

    
    def __rdRadarControllerHeader(self, fp=None):
        if fp == None:
            fp = self.fp
            
        self.radarControllerHeaderObj.read(fp)

        
    def __rdProcessingHeader(self, fp=None):
        if fp == None:
            fp = self.fp
            
        self.m_ProcessingHeader.read(fp)


    def __rdBasicHeader(self, fp=None):
        
        if fp == None:
            fp = self.fp
            
        self.m_BasicHeader.read(fp)
       
    def __readFirstHeader(self):
        """ 
        Lectura del First Header, es decir el Basic Header y el Long Header
            
        Affected:
            self.m_BasicHeader
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.m_ProcessingHeader
            self.firstHeaderSize
            self.dataType
            self.fileSizeByHeader
            self.ippSeconds
            
        Return: 
            None
        """
        self.__rdBasicHeader()
        self.__rdSystemHeader()
        self.__rdRadarControllerHeader()
        self.__rdProcessingHeader()
        self.firstHeaderSize = self.m_BasicHeader.size
        
        datatype = int(numpy.log2((self.m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
        if datatype == 0:
            datatype_str = numpy.dtype([('real','<i1'),('imag','<i1')])
            
        elif datatype == 1:
            datatype_str = numpy.dtype([('real','<i2'),('imag','<i2')])
            
        elif datatype == 2:
            datatype_str = numpy.dtype([('real','<i4'),('imag','<i4')])
            
        elif datatype == 3:
            datatype_str = numpy.dtype([('real','<i8'),('imag','<i8')])
            
        elif datatype == 4:
            datatype_str = numpy.dtype([('real','<f4'),('imag','<f4')])
            
        elif datatype == 5:
            datatype_str = numpy.dtype([('real','<f8'),('imag','<f8')])
            
        else:
            raise ValueError, 'Data type was not defined'
        
        self.dataType = datatype_str
        self.ippSeconds = 2 * 1000 * self.radarControllerHeaderObj.ipp / self.c
        
        self.fileSizeByHeader = self.m_ProcessingHeader.dataBlocksPerFile * self.m_ProcessingHeader.blockSize + self.firstHeaderSize + self.basicHeaderSize*(self.m_ProcessingHeader.dataBlocksPerFile - 1)
        self.dataOutObj.channelList = numpy.arange(self.systemHeaderObj.numChannels)
        self.dataOutObj.channelIndexList = numpy.arange(self.systemHeaderObj.numChannels)
        
        self.getBlockDimension()
        
        
    def __setNewBlock(self):
        """ 
        Lee el Basic Header y posiciona le file pointer en la posicion inicial del bloque a leer

        Affected: 
            self.m_BasicHeader
            self.flagNoContinuousBlock
            self.ns

        Return: 
            0    :    Si el file no tiene un Basic Header que pueda ser leido
            1    :    Si se pudo leer el Basic Header
        """
        if self.fp == None:
            return 0
        
        if self.flagIsNewFile:
            return 1
        
        self.lastUTTime = self.m_BasicHeader.utc
        
        currentSize = self.fileSize - self.fp.tell()
        neededSize = self.m_ProcessingHeader.blockSize + self.basicHeaderSize
        
        #If there is enough data setting new data block
        if ( currentSize >= neededSize ):
            self.__rdBasicHeader()
            return 1
        
        #si es OnLine y ademas aun no se han leido un bloque completo entonces se espera por uno valido
        if self.online and (self.nReadBlocks < self.m_ProcessingHeader.dataBlocksPerFile):
            
            fpointer = self.fp.tell()
            
            for nTries in range( self.nTries ):
                #self.fp.close()

                print "\tWaiting %0.2f seconds for the next block, try %03d ..." % (self.delay, nTries+1)
                time.sleep( self.delay )

                #self.fp = open( self.filename, 'rb' )
                #self.fp.seek( fpointer )

                self.fileSize = os.path.getsize( self.filename )
                currentSize = self.fileSize - fpointer

                if ( currentSize >= neededSize ):
                    self.__rdBasicHeader()
                    return 1
                
        #Setting new file 
        if not( self.setNextFile() ):
            return 0
        
        deltaTime = self.m_BasicHeader.utc - self.lastUTTime # check this
        
        self.flagResetProcessing = 0
        
        if deltaTime > self.maxTimeStep:
            self.flagResetProcessing = 1
            
        return 1
    
    def readNextBlock(self):
        """ 
        Establece un nuevo bloque de datos a leer y los lee, si es que no existiese
        mas bloques disponibles en el archivo actual salta al siguiente.

        Affected: 
            self.lastUTTime

        Return: None
        """
        
        if not(self.__setNewBlock()):
            return 0
        
        if not(self.readBlock()):
            return 0
        
        return 1

    def __setNextFileOnline(self):
        """
        Busca el siguiente file que tenga suficiente data para ser leida, dentro de un folder especifico, si
        no encuentra un file valido espera un tiempo determinado y luego busca en los posibles n files
        siguientes.   
            
        Affected: 
            self.flagIsNewFile
            self.filename
            self.fileSize
            self.fp
            self.set
            self.flagNoMoreFiles

        Return: 
            0    : si luego de una busqueda del siguiente file valido este no pudo ser encontrado
            1    : si el file fue abierto con exito y esta listo a ser leido
        
        Excepciones: 
            Si un determinado file no puede ser abierto
        """
        nFiles = 0
        fileOk_flag = False        
        firstTime_flag = True

        self.set += 1
        
        #busca el 1er file disponible
        file, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
        if file:
            if self.__verifyFile(file, False):
                fileOk_flag = True

        #si no encuentra un file entonces espera y vuelve a buscar
        if not(fileOk_flag): 
            for nFiles in range(self.nFiles+1): #busco en los siguientes self.nFiles+1 files posibles

                if firstTime_flag: #si es la 1era vez entonces hace el for self.nTries veces  
                    tries = self.nTries
                else:
                    tries = 1 #si no es la 1era vez entonces solo lo hace una vez
                    
                for nTries in range( tries ): 
                    if firstTime_flag:
                        print "\tWaiting %0.2f sec for new \"%s\" file, try %03d ..." % ( self.delay, filename, nTries+1 ) 
                        time.sleep( self.delay )
                    else:
                        print "\tSearching next \"%s%04d%03d%03d%s\" file ..." % (self.optchar, self.year, self.doy, self.set, self.ext)
                    
                    file, filename = checkForRealPath( self.path, self.year, self.doy, self.set, self.ext )
                    if file:
                        if self.__verifyFile(file):
                            fileOk_flag = True
                            break
                    
                if fileOk_flag:
                    break

                firstTime_flag = False

                print "\tSkipping the file \"%s\" due to this file doesn't exist yet" % filename
                self.set += 1
                    
                if nFiles == (self.nFiles-1): #si no encuentro el file buscado cambio de carpeta y busco en la siguiente carpeta
                    self.set = 0
                    self.doy += 1

        if fileOk_flag:
            self.fileSize = os.path.getsize( file )
            self.filename = file
            self.flagIsNewFile = 1
            if self.fp != None: self.fp.close() 
            self.fp = open(file)
            self.flagNoMoreFiles = 0
            print 'Setting the file: %s' % file
        else:
            self.fileSize = 0
            self.filename = None
            self.flagIsNewFile = 0
            self.fp = None
            self.flagNoMoreFiles = 1
            print 'No more Files'

        return fileOk_flag


    def __setNextFileOffline(self):
        """ 
        Busca el siguiente file dentro de un folder que tenga suficiente data para ser leida
            
        Affected: 
            self.flagIsNewFile
            self.fileIndex
            self.filename
            self.fileSize
            self.fp

        Return: 
            0    : si un determinado file no puede ser abierto
            1    : si el file fue abierto con exito 
        
        Excepciones: 
            Si un determinado file no puede ser abierto
        """
        idFile = self.fileIndex
        
        while(True):
            
            idFile += 1
            
            if not(idFile < len(self.filenameList)):
                self.flagNoMoreFiles = 1
                print 'No more Files'
                return 0
            
            filename = self.filenameList[idFile]

            if not(self.__verifyFile(filename)):
                continue

            fileSize = os.path.getsize(filename)
            fp = open(filename,'rb')
            break

        self.flagIsNewFile = 1
        self.fileIndex = idFile
        self.filename = filename
        self.fileSize = fileSize
        self.fp = fp
        
        print 'Setting the file: %s'%self.filename
        
        return 1
    

    def setNextFile(self):
        """ 
        Determina el siguiente file a leer y si hay uno disponible lee el First Header
            
        Affected: 
            self.m_BasicHeader
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.m_ProcessingHeader
            self.firstHeaderSize

        Return: 
            0    :    Si no hay files disponibles
            1    :    Si hay mas files disponibles
        """
        if self.fp != None:
            self.fp.close()

        if self.online:
            newFile = self.__setNextFileOnline()
        else:
            newFile = self.__setNextFileOffline()

        if not(newFile):
            return 0
        
        self.__readFirstHeader()
        self.nReadBlocks = 0
        return 1

    def __verifyFile(self, filename, msgFlag=True):
        """
        Verifica que el filename tenga data valida, para ello leo el FirstHeader del file 
        
        Return:
            0    :    file no valido para ser leido
            1    :    file valido para ser leido
        """
        msg = None

        try:
            fp = open( filename,'rb' ) #lectura binaria
            currentPosition = fp.tell()
        except:
            if msgFlag:
                print "The file %s can't be opened" % (filename)
            return False

        neededSize = self.m_ProcessingHeader.blockSize + self.firstHeaderSize
        
        if neededSize == 0:

            m_BasicHeader = BasicHeader()
            systemHeaderObj = SystemHeader()
            radarControllerHeaderObj = RadarControllerHeader()
            m_ProcessingHeader = ProcessingHeader()
            
            try:
                if not( m_BasicHeader.read(fp) ): raise ValueError 
                if not( systemHeaderObj.read(fp) ): raise ValueError
                if not( radarControllerHeaderObj.read(fp) ): raise ValueError
                if not( m_ProcessingHeader.read(fp) ): raise ValueError
                data_type = int(numpy.log2((m_ProcessingHeader.processFlags & PROCFLAG.DATATYPE_MASK))-numpy.log2(PROCFLAG.DATATYPE_CHAR))
                
                neededSize = m_ProcessingHeader.blockSize + m_BasicHeader.size

            except:
                if msgFlag:
                    print "\tThe file %s is empty or it hasn't enough data" % filename
                
                fp.close()
                return False
        
        else:
            msg = "\tSkipping the file %s due to it hasn't enough data" %filename
                
        fp.close()
        fileSize = os.path.getsize(filename)
        currentSize = fileSize - currentPosition
        
        if currentSize < neededSize:
            if msgFlag and (msg != None):
                print msg #print"\tSkipping the file %s due to it hasn't enough data" %filename
            return False

        return True

    def updateDataHeader(self):
        
        self.dataOutObj.m_BasicHeader = self.m_BasicHeader.copy()
        self.dataOutObj.m_ProcessingHeader = self.m_ProcessingHeader.copy()
        self.dataOutObj.radarControllerHeaderObj = self.radarControllerHeaderObj.copy()
        self.dataOutObj.systemHeaderObj = self.systemHeaderObj.copy()
        
        self.dataOutObj.dataType = self.dataType
        self.dataOutObj.updateObjFromHeader()

        
class JRODataWriter(JRODataIO):

    """ 
    Esta clase permite escribir datos a archivos procesados (.r o ,pdata). La escritura
    de los datos siempre se realiza por bloques. 
    """
    
    nWriteBlocks = 0 

    setFile = None
    
    
    def __init__(self, dataOutObj=None):
        raise ValueError, "Not implemented"


    def hasAllDataInBuffer(self):
        raise ValueError, "Not implemented"


    def setBlockDimension(self):
        raise ValueError, "Not implemented"

    
    def writeBlock(self):
        raise ValueError, "No implemented"


    def putData(self):
        raise ValueError, "No implemented"

    
    def __writeFirstHeader(self):
        """
        Escribe el primer header del file es decir el Basic header y el Long header (SystemHeader, RadarControllerHeader, ProcessingHeader)
        
        Affected:
            __dataType
            
        Return:
            None
        """
        self.__writeBasicHeader()
        self.__wrSystemHeader()
        self.__wrRadarControllerHeader()
        self.__wrProcessingHeader()
        self.dataType = self.dataOutObj.dataType
            
            
    def __writeBasicHeader(self, fp=None):
        """
        Escribe solo el Basic header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.dataOutObj.m_BasicHeader.write(fp)

    
    def __wrSystemHeader(self, fp=None):
        """
        Escribe solo el System header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.dataOutObj.systemHeaderObj.write(fp)

    
    def __wrRadarControllerHeader(self, fp=None):
        """
        Escribe solo el RadarController header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
        
        self.dataOutObj.radarControllerHeaderObj.write(fp)

        
    def __wrProcessingHeader(self, fp=None):
        """
        Escribe solo el Processing header en el file creado

        Return:
            None
        """
        if fp == None:
            fp = self.fp
            
        self.dataOutObj.m_ProcessingHeader.write(fp)
    
    
    def setNextFile(self):
        """ 
        Determina el siguiente file que sera escrito

        Affected: 
            self.filename
            self.subfolder
            self.fp
            self.setFile
            self.flagIsNewFile

        Return:
            0    :    Si el archivo no puede ser escrito
            1    :    Si el archivo esta listo para ser escrito
        """
        ext = self.ext
        path = self.path
        
        if self.fp != None:
            self.fp.close()
        
        timeTuple = time.localtime( self.dataOutObj.m_BasicHeader.utc )
        subfolder = 'D%4.4d%3.3d' % (timeTuple.tm_year,timeTuple.tm_yday)

        doypath = os.path.join( path, subfolder )
        if not( os.path.exists(doypath) ):
            os.mkdir(doypath)
            self.setFile = -1 #inicializo mi contador de seteo
        else:
            filesList = os.listdir( doypath )
            if len( filesList ) > 0:
                filesList = sorted( filesList, key=str.lower )
                filen = filesList[-1]
                # el filename debera tener el siguiente formato
                # 0 1234 567 89A BCDE (hex)
                # x YYYY DDD SSS .ext
                if isNumber( filen[8:11] ):
                    self.setFile = int( filen[8:11] ) #inicializo mi contador de seteo al seteo del ultimo file
                else:    
                    self.setFile = -1
            else:
                self.setFile = -1 #inicializo mi contador de seteo
                
        setFile = self.setFile
        setFile += 1
                
        file = '%s%4.4d%3.3d%3.3d%s' % (self.optchar,
                                        timeTuple.tm_year,
                                        timeTuple.tm_yday,
                                        setFile,
                                        ext )

        filename = os.path.join( path, subfolder, file )

        fp = open( filename,'wb' )
        
        self.nWriteBlocks = 0
        
        #guardando atributos 
        self.filename = filename
        self.subfolder = subfolder
        self.fp = fp
        self.setFile = setFile
        self.flagIsNewFile = 1
        
        print 'Writing the file: %s'%self.filename
        
        self.__writeFirstHeader()
        
        return 1


    def __setNewBlock(self):
        """
        Si es un nuevo file escribe el First Header caso contrario escribe solo el Basic Header
        
        Return:
            0    :    si no pudo escribir nada
            1    :    Si escribio el Basic el First Header
        """        
        if self.fp == None:
            self.setNextFile()
        
        if self.flagIsNewFile:
            return 1
        
        if self.nWriteBlocks < self.m_ProcessingHeader.dataBlocksPerFile:
            self.__writeBasicHeader()
            return 1
        
        if not( self.setNextFile() ):
            return 0
        
        return 1


    def writeNextBlock(self):
        """
        Selecciona el bloque siguiente de datos y los escribe en un file
            
        Return: 
            0    :    Si no hizo pudo escribir el bloque de datos 
            1    :    Si no pudo escribir el bloque de datos
        """
        if not( self.__setNewBlock() ):
            return 0
        
        self.writeBlock()

        return 1
    

    def getDataHeader(self):
        """
        Obtiene una copia del First Header
         
        Affected:
            self.m_BasicHeader
            self.systemHeaderObj
            self.radarControllerHeaderObj
            self.m_ProcessingHeader
            self.dataType

        Return: 
            None
        """
        self.dataOutObj.updateHeaderFromObj()
        
        self.m_BasicHeader = self.dataOutObj.m_BasicHeader.copy()
        self.systemHeaderObj = self.dataOutObj.systemHeaderObj.copy()
        self.radarControllerHeaderObj = self.dataOutObj.radarControllerHeaderObj.copy()
        self.m_ProcessingHeader = self.dataOutObj.m_ProcessingHeader.copy()
        
        self.dataType = self.dataOutObj.dataType
        
    
    def setup(self, path, set=0, ext=None):
        """
        Setea el tipo de formato en la cual sera guardada la data y escribe el First Header 
            
        Inputs:
            path      :    el path destino en el cual se escribiran los files a crear
            format    :    formato en el cual sera salvado un file
            set       :    el setebo del file
            
        Return:
            0    :    Si no realizo un buen seteo
            1    :    Si realizo un buen seteo 
        """
        
        if ext == None:
            ext = self.ext
        
        ext = ext.lower()

        self.path = path
        self.setFile = set - 1
        self.ext = ext
        #self.format = format
        self.getDataHeader()

        self.setBlockDimension()
        
        if not( self.setNextFile() ):
            print "There isn't a next file"
            return 0

        return 1
