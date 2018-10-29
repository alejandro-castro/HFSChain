# -*- coding: utf-8 -*-
"""
Module implementing MainWindow.
#+++++++++++++++++++++INTERFAZ DE USUARIO V1.1++++++++++++++++++++++++#
"""
from PyQt4.QtGui import QMainWindow
from PyQt4.QtCore import pyqtSignature
from PyQt4.QtCore import pyqtSignal
from PyQt4 import QtCore
from PyQt4 import QtGui
from timeconversions import  Doy2Date
from modelProperties import treeModel

from viewer.ui_unitprocess import Ui_UnitProcess
from viewer.ui_window import Ui_window
from viewer.ui_mainwindow import Ui_MainWindow


from controller import Project,ReadUnitConf,ProcUnitConf,OperationConf,ParameterConf
import os


class BodyMainWindow(QMainWindow, Ui_MainWindow):
    __projObjDict = {}
    __arbolDict = {}
    __upObjDict = {}
    
    """
    Class documentation goes here.
    #*##################VENTANA CUERPO  DEL PROGRAMA####################
    """
    def __init__(self, parent = None):  
        """
        Constructor
        """   
        print "Inicio de Programa Interfaz Gráfica"
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        
        self.indexclick=None
               
        self.online=0
        self.datatype=0
        self.variableList=[]
        
        self.proObjList=[]      
        self.idp=0
        self.namep=0
        self.description=0
        self.namepTree=0
        self.valuep=0

        self.upObjList= []     
        self.upn=0
        self.upName=0
        self.upType=0
        self.uporProObjRecover=0
        
        self.readUnitConfObjList=[]
        
        self.upObjVolList=[]
        self.upobjSpecList=[] 
        
        self.operObjList=[]
        
        self.configProject=None
        self.configUP=None
    
        self.readUnitConfObj=None
        self.procUnitConfObj0=None
        self.opObj10=None
        self.opObj12=None
        
        self.setParam()

  #-----------------------------------NEW PROPERTIES------------------------------------------------#
        QtGui.QToolTip.setFont(QtGui.QFont('SansSerif', 10))
        self.addprojectBtn.setToolTip('Add_New_Project')    
        self.addUnitProces.setToolTip('Add_New_Processing_Unit')  

  #-----------------------------------NEW PROPERTIES------------------------------------------------#
        self.model = QtGui.QStandardItemModel()
        self.treeView.setModel(self.model)
        self.treeView.clicked.connect(self.clickFunctiontree)
        self.treeView.expandAll()
        #self.treeView.clicked.connect(self.treefunction1)

 #-----------------------------------BARRA DE MENU-------------------------------------------------#
 
 #----------------------------------- MENU_PROJECT--------------------------------------------------#  
        
    @pyqtSignature("")
    def on_menuFileAbrirObj_triggered(self):
        """
        Abre un archivo de configuracion seleccionado, lee los parametros y
        actualiza los atributos de esta clase; creando los objetos necesarios
        con los parametros leidos desde el archivo.
        """
        print "Leer un archivo xml y extraer sus atributos Not implemented yet"
        
    @pyqtSignature("")
    def on_menuFileCrearObj_triggered(self):
        """
        Crea un proyecto nuevo y lo anade a mi diccionario de proyectos
        y habilita la ventana de configuracion del proyecto.
        
        """
        self.addProject()
             
    @pyqtSignature("")
    def on_menuFileGuardarObj_triggered(self):
        """
        METODO  EJECUTADO CUANDO OCURRE EL EVENTO GUARDAR PROJECTO
        
        Llama al metodo saveProject.
        """ 
#        my_id = arbol_selected()
#        filename = savefindow.show()
#        self.saveProject(id, filename)
        print "probsave"
        self.saveProject()
        
    @pyqtSignature("")
    def on_menuFileCerrarObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO CERRAR
        Llama al metodo close.
        """ 
        self.close()
        
   #-----------------------------------MENU_RUN----------------------------------------------------#   
    
    @pyqtSignature("")
    def on_menuRUNStartObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO RUN 
        Llama al metodo RUN.
        """ 
        print "Not implemented yet"
        
    @pyqtSignature("") 
    def on_menuRUNPausaObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Not implemented yet"
    
   #-----------------------------------MENU_OPTION-------------------------------------------------#   
    
    @pyqtSignature("") 
    def on_menuOptConfigLogfileObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO ConfigLog
        Llama al metodo close.
        """ 
        print "Not implemented yet"
   
    @pyqtSignature("") 
    def on_menuOptConfigserverObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO Config Server
        Llama al metodo close.
        """ 
        print "Not implemented yet"   
    #-----------------------------------MENU_HELP-------------------------------------------------------#   
    
    @pyqtSignature("") 
    def on_menuHELPAboutObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO HELP
        Llama al metodo close.
        """ 
        print "Not implemented yet"
    
    @pyqtSignature("") 
    def on_menuHELPPrfObj_clicked(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO HElp
        Llama al metodo close.
        """ 
        print "Not implemented yet"    
        
  #-----------------------------------BARRA DE HERRAMIENTAS----------------------------------------#
    
    @pyqtSignature("")
    def on_actOpenObj_triggered(self):
        """
        METODO CARGA UN ARCHIVO DE CONFIGURACION ANTERIOR
        """
        print "Leer un archivo xml y extraer sus atributos Not implemented yet"
       
    @pyqtSignature("")
    def on_actCreateObj_triggered(self):
        """
        CREAR PROJECT ,ANADE UN NUEVO PROYECTO, LLAMA AL MÉTODO QUE CONTIENE LAS OPERACION DE CREACION DE PROYECTOS
        Llama al metodo addProject.
        """
        self.addProject()
                    
    @pyqtSignature("")
    def on_actStopObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Not implemented yet"

    @pyqtSignature("")
    def on_actPlayObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO PAUSA
        Llama al metodo PAUSA.
        """ 
        print "Not implemented yet"
   
    @pyqtSignature("")
    def on_actSaveObj_triggered(self):
        """
        METODO EJECUTADO CUANDO OCURRE EL EVENTO SAVE
        Llama al metodo SAVE.
        """ 
        self.saveProject()
      
   #-----------------------------------PUSHBUTTON_CREATE PROJECT----------------------------------#      
         
    @pyqtSignature("")
    def on_addprojectBtn_clicked(self):
        """
        CREAR PROJECT ,ANADE UN NUEVO PROYECTO, LLAMA AL MÉTODO QUE CONTIENE LAS OPERACION DE CREACION DE PROYECTOS
        Llama al metodo addProject.
        """ 
        self.addProject()
    
   #------------------------------------VENTANA CONFIGURACION PROJECT----------------------------#     
    
    @pyqtSignature("int")
    def on_dataTypeCmbBox_activated(self,index):
        """
        Metodo que identifica que tipo de dato se va a trabajar VOLTAGE O ESPECTRA
        """
        self.dataFormatTxt.setReadOnly(True)
        if index==0:
           self.datatype='Voltage'
        elif index==1:
            self.datatype='Spectra'
        else :
              self.datatype=''
              self.dataFormatTxt.setReadOnly(False)
        self.dataFormatTxt.setText(self.datatype)
        
    @pyqtSignature("")
    def on_dataPathBrowse_clicked(self):
        """
        OBTENCION DE LA RUTA DE DATOS
        """
        self.dataPath = str(QtGui.QFileDialog.getExistingDirectory(self, 'Open Directory', './',  QtGui.QFileDialog.ShowDirsOnly))
        self.dataPathTxt.setText(self.dataPath)
        self.statusDpath=self.existDir(self.dataPath)
        self.loadDays()   
        
    @pyqtSignature("int")
    def on_starDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS -START DATE
        """
        var_StopDay_index=self.endDateCmbBox.count() - self.endDateCmbBox.currentIndex()
        self.endDateCmbBox.clear()
        for i in self.variableList[index:]:
            self.endDateCmbBox.addItem(i)
        self.endDateCmbBox.setCurrentIndex(self.endDateCmbBox.count() - var_StopDay_index)
        self.getsubList()

    @pyqtSignature("int")
    def on_endDateCmbBox_activated(self, index):
        """
        SELECCION DEL RANGO DE FECHAS-END DATE
        """
        var_StartDay_index=self.starDateCmbBox.currentIndex()
        var_end_index = self.endDateCmbBox.count() - index
        self.starDateCmbBox.clear()
        for i in self.variableList[:len(self.variableList) - var_end_index + 1]:
            self.starDateCmbBox.addItem(i)
        self.starDateCmbBox.setCurrentIndex(var_StartDay_index)
        self.getsubList() #Se carga var_sublist[] con el rango de las fechas seleccionadas
    
    @pyqtSignature("int")
    def on_readModeCmBox_activated(self, p0):
        """
        SELECCION DEL MODO DE LECTURA ON=1, OFF=0
        """
        if p0==0:
           self.online=0
        elif p0==1:
            self.online=1  
        
    #---------------PUSHBUTTON_DATA    "      OKBUTTON    "_CONFIGURATION PROJECT--------------------------#    
    
    @pyqtSignature("")
    def on_dataOkBtn_clicked(self):
        """
        Añade al Obj XML de Projecto, name,datatype,date,time,readmode,wait,etc, crea el readUnitProcess del archivo xml.
        Prepara la configuración del diágrama del Arbol del treeView numero 2
        """     
        print "En este nivel se pasa el tipo de dato con el que se trabaja,path,startDate,endDate,startTime,endTime,online"
       
        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
               self.projectObj=self.__projObjDict[int(i)]  
#               print self.projectObj
#               print i
#               print "get",self.__arbolDict.items()
#               print "keys",self.__arbolDict.keys()
               self.description="Think"          
               id=i
               name=str(self.nameProjectTxt.text())
               desc=str(self.description)
                
               self.projectObj.setup(id = id, name=name, description=desc)
               print self.projectObj.id
#               print self.projectObj.name
#               print self.projectObj.description
        
               datatype=str(self.dataTypeCmbBox.currentText())
               path=str(self.dataPathTxt.text())
               online=int(self.online)
               starDate=str(self.starDateCmbBox.currentText())
               endDate=str(self.endDateCmbBox.currentText())
   
        
               self.readUnitConfObj = self.projectObj.addReadUnit(datatype=datatype,
                                                        path=path,
                                                        startDate=starDate,
                                                        endDate=endDate,
                                                        startTime='06:10:00',
                                                        endTime='23:59:59',
                                                        online=online)
                
               self.readUnitConfObjList.append(self.readUnitConfObj)
               print "self.readUnitConfObj.getId",self.readUnitConfObj.getId(),datatype,path,starDate,endDate,online            
              
               self.model_2=treeModel()        
               self.model_2.setParams(name=self.projectObj.name+str(self.projectObj.id),
                                      directorio=path,
                                        workspace="C:\\WorkspaceGUI",
                                          remode=str(self.readModeCmBox.currentText()), 
                                           dataformat=datatype, 
                                            date=str(starDate)+"-"+str(endDate),
                                             initTime='06:10:00',
                                               endTime='23:59:59',
                                                timezone="Local" ,
                                                 Summary="test de prueba")                                            
               self.model_2.arbol()
               self.treeView_2.setModel(self.model_2)
               self.treeView_2.expandAll()         
                
#    
   #-----------------PUSHBUTTON_ADD_PROCESSING UNIT PROJECT------------------#    
    @pyqtSignature("")
    def on_addUnitProces_clicked(self):
        """
        CREAR PROCESSING UNI ,ANADE UNA UNIDAD DE PROCESAMIENTO, LLAMA AL MÉTODO addUP QUE CONTIENE LAS OPERACION DE CREACION DE UNIDADES DE PROCESAMIENTO
        Llama al metodo addUP.
        """
#        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
        self.addUP()
        
      #----------------------------BASICO-----------------------------------#  
                
    def getNumberofProject(self):
#        for i in self.proObjList:
#            print i
        return self.proObjList
#        for  i in self.proObjList:
#            print i
        
    def setParam(self):
        
        self.tabWidgetProject.setEnabled(False)
        self.dataPathTxt.setText('C:\data')
        self.nameProjectTxt.setText("Test")
        self.numberChannelopVol.setEnabled(False)
        self.lineHeighProfileTxtopVol.setEnabled(False)
        self.numberIntegration.setEnabled(False)
        self.valuenFFTPointOpSpec.setEnabled(False)
        self.lineProfileSelecopVolCEB.setEnabled(False)
        
    def clickFunctiontree(self,index):
        self.indexclick= index.model().itemFromIndex(index)
        print self.indexclick
        return self.indexclick
#        self.indexclick= index.model().itemFromIndex(index).text()
#        return self.indexclick
#        print self.indexclick()
#        print index.model().itemFromIndex(index)
#        print  self.indexclick
#        NumofPro=self.indexclick[8:10]
#        self.valuep=NumofPro
#        #print self.valuep
#        NameofPro=self.indexclick[0:7]
#        self.namepTree=NameofPro
#        print self.namepTree

    def addProject(self):
        self.tabWidgetProject.setEnabled(True)
        print "En este nivel se debe crear el proyecto,id,nombre,desc"
        #+++++++++++++++++++Creacion del Objeto Controller-XML+++++++++++++#
        
        self.idp += 1
        self.projectObj = Project()
        print self.projectObj
        self.__projObjDict[self.idp] = self.projectObj
        
        #++++++++++++++++++Creación del Arbol++++++++++++++++++++#
        self.parentItem = self.model.invisibleRootItem()
        name=str(self.nameProjectTxt.text())
        self.__arbolDict[self.idp] =   QtGui.QStandardItem(QtCore.QString(name+" %0").arg(self.idp))
        print self.__arbolDict[self.idp]
        self.parentItem.appendRow(self.__arbolDict[self.idp])
        self.parentItem=self.__arbolDict[self.idp]
        
        print "Porfavor ingrese los parámetros de configuracion del Proyecto"
       
    def existDir(self, var_dir):
        """
        METODO PARA VERIFICAR SI LA RUTA EXISTE-VAR_DIR
        VARIABLE DIRECCION
        """
        if os.path.isdir(var_dir): 
            return True
        else:
            self.textEdit.append("Incorrect path:" + str(var_dir))
            return False
    
    def loadDays(self):
        """
        METODO PARA CARGAR LOS DIAS
        """
        self.variableList=[]     
        self.starDateCmbBox.clear()
        self.endDateCmbBox.clear()

        Dirlist =  os.listdir(self.dataPath)
        Dirlist.sort()     
        
        for a in range(0, len(Dirlist)):
            fname= Dirlist[a]
            Doy=fname[5:8]
            fname = fname[1:5]
            print fname
            fecha=Doy2Date(int(fname),int(Doy))
            fechaList=fecha.change2date()
            #print fechaList[0]
            Dirlist[a]=fname+"/"+str(fechaList[0])+"/"+str(fechaList[1])
            #+"-"+ fechaList[0]+"-"+fechaList[1]
    
        #---------------AQUI TIENE QUE SER MODIFICADO--------#

        #Se cargan las listas para seleccionar StartDay y StopDay (QComboBox)
        for i in range(0, (len(Dirlist))):
            self.variableList.append(Dirlist[i])
        
        for i in self.variableList:
            self.starDateCmbBox.addItem(i)
            self.endDateCmbBox.addItem(i)
        self.endDateCmbBox.setCurrentIndex(self.starDateCmbBox.count()-1)
    
        self.getsubList()    
        self.dataOkBtn.setEnabled(True)    
        
    def getsubList(self):
        """
        OBTIENE EL RANDO DE LAS FECHAS SELECCIONADAS
        """
        self.subList=[]
        for i in self.variableList[self.starDateCmbBox.currentIndex():self.starDateCmbBox.currentIndex() + self.endDateCmbBox.currentIndex()+1]:
            self.subList.append(i)  
       
    def addUP(self):
        
        self.configUP=UnitProcess(self)
        for i in self.__arbolDict:       
            if self.__arbolDict[i]==self.indexclick:
               if self.__projObjDict.has_key(i)==True:
                   self.projectObj=self.__projObjDict[int(i)]
                   print self.projectObj.id
                   self.configUP.getfromWindowList.append(self.projectObj) 
                   
                   
                   for i in self.projectObj.procUnitConfObjDict:
                      if self.projectObj.procUnitConfObjDict[i].getElementName()=='ProcUnit':
                         self.upObj=self.projectObj.procUnitConfObjDict[i]
                         self.configUP.getfromWindowList.append(self.upObj)          
               

            
        self.configUP.loadTotalList()
        self.configUP.show()      
        #self.configUP.unitPsavebut.clicked.connect(self.reciveUPparameters)
        self.configUP.closed.connect(self.createUP)
    

        
    def createUP(self):
        
        print "En este nivel se adiciona una rama de procesamiento, y se le concatena con el id"
        
        if not self.configUP.create:
            return
        
        self.uporProObjRecover=self.configUP.getFromWindow
        
        self.upType = self.configUP.typeofUP
        for i in self.__arbolDict: 
             if self.__arbolDict[i]==self.indexclick:
               self.projectObj=self.__projObjDict[int(i)] 
        
        datatype=str(self.upType)
        uporprojectObj=self.uporProObjRecover
        
        if uporprojectObj.getElementName()=='ProcUnit':
             inputId=uporprojectObj.getId()
        else:
            inputId=self.readUnitConfObjList[uporprojectObj.id-1].getId()
       
        print 'uporprojectObj.id','inputId', uporprojectObj.id,inputId       
        self.procUnitConfObj1 = self.projectObj.addProcUnit(datatype=datatype, inputId=inputId)
        self.__upObjDict[inputId]= self.procUnitConfObj1    
       
        self.parentItem=self.__arbolDict[uporprojectObj.id]
        #print "i","self.__arbolDict[i]",i ,self.__arbolDict[i] 
        self.numbertree=int(self.procUnitConfObj1.getId())-1
        self.__arbolDict[self.procUnitConfObj1.id]=QtGui.QStandardItem(QtCore.QString(datatype +"%1 ").arg(self.numbertree))
        self.parentItem.appendRow(self.__arbolDict[self.procUnitConfObj1.id])        
        self.parentItem=self.__arbolDict[self.procUnitConfObj1.id]
    #   self.loadUp()
        self.treeView.expandAll()

    def resetopVolt(self):
        self.selecChannelopVolCEB.setChecked(False)
        self.selecHeighopVolCEB.setChecked(False)
        self.coherentIntegrationCEB.setChecked(False)
        self.profileSelecopVolCEB.setChecked(False)
        #self.selecChannelopVolCEB.setEnabled(False)
        self.lineHeighProfileTxtopVol.clear()
        self.lineProfileSelecopVolCEB.clear()
        self.numberChannelopVol.clear()
        self.numberIntegration.clear()
            
    
    def resetopSpec(self):
        self.nFFTPointOpSpecCEB.setChecked(False)
        
        self.valuenFFTPointOpSpec.clear()
    
    def resetgraphSpec(self):
        self.SpectraPlotGraphCEB.setChecked(False)
        self.CrossSpectraPlotGraphceb.setChecked(False)
        self.RTIPlotGraphCEB.setChecked(False)                  


    def saveProject(self):
        print "entro"
        #filename="C:\WorkspaceGUI\config1.xml"
        for i in self.__arbolDict:            
            if self.__arbolDict[i]==self.indexclick:
                self.projectObj=self.__projObjDict[int(i)] 
                print "Encontre project"
        filename="C:\WorkspaceGUI\config"+str(self.projectObj.id)+".xml"
        print "Escribo Project"
        self.projectObj.writeXml(filename)


class UnitProcess(QMainWindow, Ui_UnitProcess):
    """
    Class documentation goes here.
    """
    closed=pyqtSignal()
    create= False
    def __init__(self, parent = None):
        """
        Constructor
        """
        QMainWindow.__init__(self, parent)
        self.setupUi(self)
        self.getFromWindow=None
        self.getfromWindowList=[]
 
        self.listUP=None    
        
    @pyqtSignature("")
    def on_unitPokbut_clicked(self):
        """
        Slot documentation goes here.
        """
        self.create =True
        self.getFromWindow=self.getfromWindowList[int(self.comboInputBox.currentIndex())]
        #self.nameofUP= str(self.nameUptxt.text())
        self.typeofUP= str(self.comboTypeBox.currentText())
        self.close()

    
    @pyqtSignature("")
    def on_unitPcancelbut_clicked(self):
        """
        Slot documentation goes here.
        """
        # TODO: not implemented yet
        #raise NotImplementedError
        self.create=False
        self.close()  

    def loadTotalList(self):
        self.comboInputBox.clear()
        for i in self.getfromWindowList:
            
            name=i.getElementName()
            if name=='Project':
                id= i.id
            if name=='ProcUnit':
               id=int(i.id)-1 
            self.comboInputBox.addItem(str(name)+str(id))    

    def closeEvent(self, event):
        self.closed.emit()
        event.accept()
    
    
    

    
    
    