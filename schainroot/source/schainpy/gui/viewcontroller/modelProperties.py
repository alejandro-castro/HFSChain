from PyQt4 import QtCore

HORIZONTAL_HEADERS = ("Property","Value " )
    
HORIZONTAL = ("RAMA :",)
   
class treeModel(QtCore.QAbstractItemModel):
    '''
    a model to display a few names, ordered by encabezado
    '''
    name=None
    directorio=None 
    workspace=None
    remode=None
    dataformat=None
    date=None
    initTime=None
    endTime=None
    timezone=None
    Summary=None
    
    description=None
    
    def __init__(self ,parent=None):
        super(treeModel, self).__init__(parent)
        self.people = []
        
        
    def properties_projecto(self,description):
        self.caracteristica="Project_Properties"
        self.principal     ="Name"
        self.description =description
        exam_project=person_class(self.caracteristica,self.principal,self.description)
        return exam_project
        
        
        
    def arbol(self):     
            for caracteristica,principal, descripcion in   (("Properties","Name",self.name), 
                                                            ("Properties","Data Path",self.directorio),
                                                            ("Properties","Workspace",self.workspace),
                                                            ("Parameters", "Read Mode     ",self.remode),
                                                            ("Parameters", "DataType    ",self.dataformat),
                                                            ("Parameters", "Date          ",self.date),
                                                            ("Parameters", "Init Time     ",self.initTime),
                                                            ("Parameters", "Final Time    ",self.endTime),
                                                            ("Parameters", " Time zone    ",self.timezone),
                                                            ("Parameters", "Profiles      ","1"),
                                                            ("Description", "Summary      ", self.Summary),
                                                            ):
                person = person_class(caracteristica, principal, descripcion)
                self.people.append(person)
    def addProjectproperties(self,person):
         self.people.append(person)
                
       
    #def veamos(self):
    #    self.update= MainWindow(self)
    #    self.update.dataProyectTxt.text()
    #    return self.update.dataProyectTxt.text()
    
    def showtree(self):
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
        
    def setParams(self,name,directorio,workspace,remode,dataformat,date,initTime,endTime,timezone,Summary):
        self.name=name
        self.workspace=workspace
        self.directorio= directorio
        self.remode=remode
        self.dataformat=dataformat
        self.date=date
        self.initTime=initTime
        self.endTime=endTime
        self.timezone=timezone
        self.Summary=Summary
        
        
        for caracteristica,principal, descripcion in   (("Properties","Name",self.name), 
                                                            ("Properties","Data Path",self.directorio),
                                                            ("Properties","Workspace",self.workspace),
                                                            ("Parameters", "Read Mode     ",self.remode),
                                                            ("Parameters", "DataType    ",self.dataformat),
                                                            ("Parameters", "Date          ",self.date),
                                                            ("Parameters", "Init Time     ",self.initTime),
                                                            ("Parameters", "Final Time    ",self.endTime),
                                                            ("Parameters", " Time zone    ",self.timezone),
                                                            ("Parameters", "Profiles      ","1"),
                                                            ("Description", "Summary      ", self.Summary),
                                                            ):
                person = person_class(caracteristica, principal, descripcion)
                self.people.append(person)
        self.rootItem = TreeItem(None, "ALL", None)
        self.parents = {0 : self.rootItem}
        self.setupModelData()
        
    
    def columnCount(self, parent=None):
        if parent and parent.isValid():
            return parent.internalPointer().columnCount()
        else:
            return len(HORIZONTAL_HEADERS)

    def data(self, index, role):
        if not index.isValid():
            return QtCore.QVariant()

        item = index.internalPointer()
        if role == QtCore.Qt.DisplayRole:
            return item.data(index.column())
        if role == QtCore.Qt.UserRole:
            if item:
                return item.person

        return QtCore.QVariant()

    def headerData(self, column, orientation, role):
        if (orientation == QtCore.Qt.Horizontal and
        role == QtCore.Qt.DisplayRole):
            try:
                return QtCore.QVariant(HORIZONTAL_HEADERS[column])
            except IndexError:
                pass

        return QtCore.QVariant()

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QtCore.QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QtCore.QModelIndex()

    def parent(self, index):
        if not index.isValid():
            return QtCore.QModelIndex()

        childItem = index.internalPointer()
        if not childItem:
            return QtCore.QModelIndex()
        
        parentItem = childItem.parent()

        if parentItem == self.rootItem:
            return QtCore.QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.column() > 0:
            return 0
        if not parent.isValid():
            p_Item = self.rootItem
        else:
            p_Item = parent.internalPointer()
        return p_Item.childCount()
    
    def setupModelData(self):
        for person in self.people:
            if person.descripcion:
                encabezado = person.caracteristica
     
            
            if not self.parents.has_key(encabezado):                
                newparent = TreeItem(None, encabezado, self.rootItem)
                self.rootItem.appendChild(newparent)

                self.parents[encabezado] = newparent

            parentItem = self.parents[encabezado]
            newItem = TreeItem(person, "", parentItem)
            parentItem.appendChild(newItem)
        
    def searchModel(self, person):
        '''
        get the modelIndex for a given appointment
        '''
        def searchNode(node):
            '''
            a function called recursively, looking at all nodes beneath node
            '''
            for child in node.childItems:
                if person == child.person:
                    index = self.createIndex(child.row(), 0, child)
                    return index
                    
                if child.childCount() > 0:
                    result = searchNode(child)
                    if result:
                        return result
        
        retarg = searchNode(self.parents[0])
        #print retarg
        return retarg
            
    def find_GivenName(self, principal):
        app = None
        for person in self.people:
            if person.principal == principal:
                app = person
                break
        if app != None:
            index = self.searchModel(app)
            return (True, index)            
        return (False, None)

    
    
    
    


class person_class(object):
    '''
    a trivial custom data object
    '''
    def __init__(self, caracteristica, principal, descripcion):
        self.caracteristica = caracteristica
        self.principal = principal
        self.descripcion = descripcion

    def __repr__(self):
        return "PERSON - %s %s"% (self.principal, self.caracteristica)
    
class TreeItem(object):
    '''
    a python object used to return row/column data, and keep note of
    it's parents and/or children
    '''
    def __init__(self, person, header, parentItem):
        self.person = person
        self.parentItem = parentItem
        self.header = header
        self.childItems = []

    def appendChild(self, item):
        self.childItems.append(item)

    def child(self, row):
        return self.childItems[row]

    def childCount(self):
        return len(self.childItems)

    def columnCount(self):
        return 2
    
    def data(self, column):
        if self.person == None:
            if column == 0:
                return QtCore.QVariant(self.header)
            if column == 1:
                return QtCore.QVariant("")                
        else:
            if column == 0:
                return QtCore.QVariant(self.person.principal)
            if column == 1:
                return QtCore.QVariant(self.person.descripcion)
        return QtCore.QVariant()

    def parent(self):
        return self.parentItem
    
    def row(self):
        if self.parentItem:
            return self.parentItem.childItems.index(self)
        return 0
    