'''
Created on September , 2012
@author:
'''
from xml.etree.ElementTree import Element, SubElement, ElementTree
from xml.etree import ElementTree as ET
from xml.dom import minidom
from model import *
import datetime

import ast

def prettify(elem):
	"""Return a pretty-printed XML string for the Element.
	"""
	rough_string = ET.tostring(elem, 'utf-8')
	reparsed = minidom.parseString(rough_string)
	return reparsed.toprettyxml(indent="  ")

############################################################################################
############################################################################################
#ParameterConf Definition
############################################################################################
############################################################################################

class ParameterConf(object):

	ELEMENTNAME = 'Parameter'

	def __init__(self):
		self.format = 'str'
		self.id = None
		self.name = None
		self.value = None
		self.format = None
		self.__formated_value = None


	def getElementName(self):
		return self.ELEMENTNAME


	def getValue(self):

		if self.__formated_value != None:
			return self.__formated_value

		value = self.value

		if self.format == 'bool':
			value = int(value)

		if self.format == 'list':
			strList = value.split(',')

			self.__formated_value = strList

			return self.__formated_value

		if self.format == 'intlist':
			"""
			Example:
				value = (0,1,2)
			"""
			strList = value.split(',')
			intList = [int(x) for x in strList]

			self.__formated_value = intList

			return self.__formated_value

		if self.format == 'floatlist':
			"""
			Example:
				value = (0.5, 1.4, 2.7)
			"""
			strList = value.split(',')
			floatList = [float(x) for x in strList]

			self.__formated_value = floatList

			return self.__formated_value

		if self.format == 'date':
			strList = value.split('/')
			intList = [int(x) for x in strList]
			date = datetime.date(intList[0], intList[1], intList[2])

			self.__formated_value = date

			return self.__formated_value

		if self.format == 'time':
			strList = value.split(':')
			intList = [int(x) for x in strList]
			time = datetime.time(intList[0], intList[1], intList[2])

			self.__formated_value = time

			return self.__formated_value

		if self.format == 'pairslist':
			"""
			Example:
				value = (0,1),(1,2)
			"""

			value = value.replace('(', '')
			value = value.replace(')', '')

			strList = value.split(',')
			intList = [int(item) for item in strList]
			pairList = []
			for i in range(len(intList)/2):
				pairList.append((intList[i*2], intList[i*2 + 1]))

			self.__formated_value = pairList

			return self.__formated_value

		if self.format == 'multilist':
			"""
			Example:
				value = (0,1,2),(3,4,5)
			"""
			multiList = ast.literal_eval(value)

			self.__formated_value = multiList

			return self.__formated_value

		format_func = eval(self.format)

		self.__formated_value = format_func(value)

		return self.__formated_value


	def setup(self, id, name, value, format='str'):
		self.id = id
		self.name = name
		self.value = str(value)
		self.format = str.lower(format)


	def makeXml(self, opElement):
		parmElement = SubElement(opElement, self.ELEMENTNAME)
		parmElement.set('id', str(self.id))
		parmElement.set('name', self.name)
		parmElement.set('value', self.value)
		parmElement.set('format', self.format)


	def readXml(self, parmElement):
		self.id = parmElement.get('id')
		self.name = parmElement.get('name')
		self.value = parmElement.get('value')
		self.format = parmElement.get('format')


	def __str__(self):
		return "Parameter[%s]: name = %s, value = %s, format = %s" %(self.id, self.name, self.value, self.format)


############################################################################################
############################################################################################
#OperationConf Definition
############################################################################################
############################################################################################

class OperationConf(object):
	ELEMENTNAME = 'Operation'

	def __init__(self):
		self.id = 0
		self.name = None
		self.priority = None
		self.type = 'self'


	def __getNewId(self):
		return int(self.id)*10 + len(self.parmConfObjList) + 1


	def getElementName(self):
		return self.ELEMENTNAME


	def getParameterObjList(self):
		return self.parmConfObjList


	def setup(self, id, name, priority, type):
		self.id = id
		self.name = name
		self.type = type
		self.priority = priority
		self.parmConfObjList = []


	def addParameter(self, name, value, format='str'):
		id = self.__getNewId()
		parmConfObj = ParameterConf()
		parmConfObj.setup(id, name, value, format)
		self.parmConfObjList.append(parmConfObj)

		return parmConfObj


	def makeXml(self, upElement):
		opElement = SubElement(upElement, self.ELEMENTNAME)
		opElement.set('id', str(self.id))
		opElement.set('name', self.name)
		opElement.set('type', self.type)
		opElement.set('priority', str(self.priority))

		for parmConfObj in self.parmConfObjList:
			parmConfObj.makeXml(opElement)


	def readXml(self, opElement):
		self.id = opElement.get('id')
		self.name = opElement.get('name')
		self.type = opElement.get('type')
		self.priority = opElement.get('priority')

		self.parmConfObjList = []

		parmElementList = opElement.getiterator(ParameterConf().getElementName())

		for parmElement in parmElementList:
			parmConfObj = ParameterConf()
			parmConfObj.readXml(parmElement)
			self.parmConfObjList.append(parmConfObj)


	def __str__(self):
		return "%s[%s]: name = %s, type = %s, priority = %s" %(self.ELEMENTNAME,
															self.id,
															self.name,
															self.type,
															self.priority) + "\n"+\
		"\n".join([parmConfObj.__str__() for parmConfObj in self.parmConfObjList ])


	def createObject(self):
		if self.type == 'self':
			raise ValueError, "This operation type cannot be created"

		if self.type == 'external' or self.type == 'other':
			className = eval(self.name)
			opObj = className()

		return opObj


############################################################################################
############################################################################################
#ProcUnitConf Definition
############################################################################################
############################################################################################

class ProcUnitConf(object):
	ELEMENTNAME = 'ProcUnit'


	def __init__(self):
		self.id = None
		self.datatype = None
		self.name = None
		self.inputId = None
		self.opConfObjList = []
		self.procUnitObj = None


	def __getPriority(self):
		return len(self.opConfObjList)+1


	def __getNewId(self):
		return int(self.id)*10 + len(self.opConfObjList) + 1


	def getElementName(self):
		return self.ELEMENTNAME


	def getId(self):
		return str(self.id)


	def getInputId(self):
		return str(self.inputId)


	def getOperationObjList(self):
		return self.opConfObjList


	def getProcUnitObj(self):
		return self.procUnitObj


	def setup(self, id, name, datatype, inputId):
		self.id = id
		self.name = name
		self.datatype = datatype
		self.inputId = inputId

		self.opConfObjList = []

		self.addOperation(name='run', optype='self')


	def addParameter(self, **kwargs):
		opObj = self.opConfObjList[0]
		opObj.addParameter(**kwargs)
		return opObj


	def addOperation(self, name, optype='self'):
		id = self.__getNewId()
		priority = self.__getPriority()

		opConfObj = OperationConf()
		opConfObj.setup(id, name=name, priority=priority, type=optype)

		self.opConfObjList.append(opConfObj)

		return opConfObj


	def makeXml(self, procUnitElement):
		upElement = SubElement(procUnitElement, self.ELEMENTNAME)
		upElement.set('id', str(self.id))
		upElement.set('name', self.name)
		upElement.set('datatype', self.datatype)
		upElement.set('inputId', str(self.inputId))

		for opConfObj in self.opConfObjList:
			opConfObj.makeXml(upElement)


	def readXml(self, upElement):
		self.id = upElement.get('id')
		self.name = upElement.get('name')
		self.datatype = upElement.get('datatype')
		self.inputId = upElement.get('inputId')

		self.opConfObjList = []

		opElementList = upElement.getiterator(OperationConf().getElementName())

		for opElement in opElementList:
			opConfObj = OperationConf()
			opConfObj.readXml(opElement)
			self.opConfObjList.append(opConfObj)


	def __str__(self):
		return "%s[%s]: name = %s, datatype = %s, inputId = %s" %(self.ELEMENTNAME,
															self.id,
															self.name,
															self.datatype,
															self.inputId)+"\n"+\
		"\n".join([opConfObj.__str__() for opConfObj in self.opConfObjList])


	def createObjects(self):
		className = eval(self.name)
		procUnitObj = className()
		for opConfObj in self.opConfObjList:
			if opConfObj.type == 'self':
				continue

			opObj = opConfObj.createObject()
			procUnitObj.addOperation(opObj, opConfObj.id)

		self.procUnitObj = procUnitObj

		return procUnitObj


	def run(self):
		finalSts = False

		for opConfObj in self.opConfObjList:
			kwargs = {}
			for parmConfObj in opConfObj.getParameterObjList():
				kwargs[parmConfObj.name] = parmConfObj.getValue()

			# print "\tRunning the '%s' operation with %s" %(opConfObj.name, opConfObj.id)
			sts = self.procUnitObj.call(opType = opConfObj.type,
										opName = opConfObj.name,
										opId = opConfObj.id,
										 **kwargs)
			finalSts = finalSts or sts

		return finalSts

############################################################################################
############################################################################################
#ReadUnitConf Definition
############################################################################################
############################################################################################

class ReadUnitConf(ProcUnitConf):

	path = None
	startDate = None
	endDate = None
	startTime = None
	endTime = None

	ELEMENTNAME = 'ReadUnit'

	def __init__(self):
		super(ReadUnitConf, self).__init__()
		self.inputId = 0

	def getElementName(self):
		return self.ELEMENTNAME

	def setup(self, id, name, datatype, path="", startDate="", endDate="", startTime="", endTime="", **kwargs):
		self.id = id
		self.name = name
		self.datatype = datatype

		self.path = path
		self.startDate = startDate
		self.endDate = endDate
		self.startTime = startTime
		self.endTime = endTime

		self.addRunOperation(**kwargs)

	def addRunOperation(self, **kwargs):
		opObj = self.addOperation(name = 'run', optype = 'self')

		opObj.addParameter(name='path'	 , value=self.path, format='str')
		opObj.addParameter(name='startDate' , value=self.startDate, format='date')
		opObj.addParameter(name='endDate'   , value=self.endDate, format='date')
		opObj.addParameter(name='startTime' , value=self.startTime, format='time')
		opObj.addParameter(name='endTime'   , value=self.endTime, format='time')

		for key, value in kwargs.items():
			opObj.addParameter(name=key, value=value, format=type(value).__name__)

		return opObj


############################################################################################
############################################################################################
#Project Definition
############################################################################################
############################################################################################

class Project(object):
	ELEMENTNAME = 'Project'


	def __init__(self):
		self.id = None
		self.name = None
		self.description = None
		self.procUnitConfObjDict = {}


	def __getNewId(self):
		id = int(self.id)*10 + len(self.procUnitConfObjDict) + 1
		return str(id)


	def getElementName(self):
		return self.ELEMENTNAME


	def setup(self, id, name, description):
		self.id = id
		self.name = name
		self.description = description
		print "Setup done:"
		print "Project ID: ", self.id
		print "Project Name: ", self.name
		print "Project Description: ", self.description


	def addReadUnit(self, datatype, **kwargs):
		id = self.__getNewId()
		name = str(datatype)

		readUnitConfObj = ReadUnitConf()
		readUnitConfObj.setup(id, name, datatype, **kwargs)

		self.procUnitConfObjDict[id] = readUnitConfObj

		return readUnitConfObj


	def addProcUnit(self, datatype, inputId):
		id = self.__getNewId()
		name = str(datatype)

		procUnitConfObj = ProcUnitConf()
		procUnitConfObj.setup(id, name, datatype, inputId)

		self.procUnitConfObjDict[id] = procUnitConfObj

		return procUnitConfObj


	def makeXml(self):
		projectElement = Element('Project')
		projectElement.set('id', str(self.id))
		projectElement.set('name', self.name)
		projectElement.set('description', self.description)

		for procUnitConfObj in self.procUnitConfObjDict.values():
			procUnitConfObj.makeXml(projectElement)

		self.projectElement = projectElement


	def writeXml(self, filename):
		self.makeXml()
		print prettify(self.projectElement)
		ElementTree(self.projectElement).write(filename, method='xml')


	def readXml(self, filename):

		#tree = ET.parse(filename)
		self.projectElement = None
		self.procUnitConfObjDict = {}

		self.projectElement = ElementTree().parse(filename)

		self.project = self.projectElement.tag

		self.id = self.projectElement.get('id')
		self.name = self.projectElement.get('name')
		self.description = self.projectElement.get('description')

		readUnitElementList = self.projectElement.getiterator(ReadUnitConf().getElementName())

		for readUnitElement in readUnitElementList:
			readUnitConfObj = ReadUnitConf()
			readUnitConfObj.readXml(readUnitElement)

			self.procUnitConfObjDict[readUnitConfObj.getId()] = readUnitConfObj

		procUnitElementList = self.projectElement.getiterator(ProcUnitConf().getElementName())

		for procUnitElement in procUnitElementList:
			procUnitConfObj = ProcUnitConf()
			procUnitConfObj.readXml(procUnitElement)

			self.procUnitConfObjDict[procUnitConfObj.getId()] = procUnitConfObj


	def __str__(self):
		return "Project[%s]: name = %s, description = %s" %(self.id,
															self.name,
															self.description)+"\n"+\
		"\n".join([procUnitConfObj.__str__() for procUnitConfObj in self.procUnitConfObjDict.values()])


	def createObjects(self):
		for procUnitConfObj in self.procUnitConfObjDict.values():
			procUnitConfObj.createObjects()

	def __connect(self, objIN, thisObj):
		thisObj.setInput(objIN.getOutputObj())

	def connectObjects(self):
		for thisPUConfObj in self.procUnitConfObjDict.values():
			inputId = thisPUConfObj.getInputId()

			if int(inputId) == 0:
				continue

			#Get input object
			puConfINObj = self.procUnitConfObjDict[inputId]
			puObjIN = puConfINObj.getProcUnitObj()

			#Get current object
			thisPUObj = thisPUConfObj.getProcUnitObj()

			self.__connect(puObjIN, thisPUObj)

	def run(self):
		finalSts = True
		while(finalSts):
			finalSts = False

			ordered_procUnitsIDs = self.procUnitConfObjDict.keys()
			ordered_procUnitsIDs.sort()

			for id in ordered_procUnitsIDs:
				procUnitConfObj = self.procUnitConfObjDict[id]
				# print "Running the '%s' process with %s" %(procUnitConfObj.name, procUnitConfObj.id)
				sts = procUnitConfObj.run()
				finalSts = finalSts or sts

		#If every process unit finished so end process
		print "Every process units have finished."
