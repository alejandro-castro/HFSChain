'''
Created on Feb 7, 2012

@author $Author: dsuarez $
@version $Id: VoltagePlot.py 116 2012-09-04 18:50:23Z dsuarez $
'''
import numpy
import os
import sys

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Voltage import Voltage

class Osciloscope:
    linearplotObj = None
    
    def __init__(self, Voltage, index):
        self.__isPlotConfig = False
        self.__isPlotIni = False
        self.__xrange = None
        self.__yrange = None
        self.indexPlot = index
        self.voltageObj = Voltage
    
    def setup(self,indexPlot,nsubplot,winTitle=''):
        self.linearplotObj = LinearPlot(indexPlot,nsubplot,winTitle)
    
    def initPlot(self,xmin,xmax,ymin,ymax,titleList,xlabelList,ylabelList):
        nsubplot = self.voltageObj.nChannels
        
        for index in range(nsubplot):
            title = titleList[index]
            xlabel = xlabelList[index]
            ylabel = ylabelList[index]
            subplot = index
            self.linearplotObj.setup(subplot+1,xmin,xmax,ymin,ymax,title,xlabel,ylabel)
    
    def plotData(self,
                 xmin=None,
                 xmax=None,
                 ymin=None,
                 ymax=None,
                 titleList=None,
                 xlabelList=None,
                 ylabelList=None,
                 winTitle='',
                 type="power"):
        
        databuffer = self.voltageObj.data
        
        height = self.voltageObj.heightList
        nsubplot = self.voltageObj.nChannels
        indexPlot = self.indexPlot
        
        
        if not(self.__isPlotConfig):
            self.setup(indexPlot,nsubplot,winTitle)
            self.__isPlotConfig = True
        
        if not(self.__isPlotIni):
            if titleList == None:
                titleList = []
                thisDatetime = datetime.datetime.fromtimestamp(self.voltageObj.m_BasicHeader.utc)
                txtdate = "Date: %s" %(thisDatetime.strftime("%d-%b-%Y"))
                for i in range(nsubplot):
                    titleList.append("Channel: %d %s" %(i, txtdate))

            if xlabelList == None:
                xlabelList = []
                for i in range(nsubplot):
                    xlabelList.append("")

            if ylabelList == None:
                ylabelList = []
                for i in range(nsubplot):
                    ylabelList.append("")

            if xmin == None: xmin = height[0]
            if xmax == None: xmax = height[-1]
            if ymin == None: ymin = numpy.nanmin(abs(databuffer))
            if ymax == None: ymax = numpy.nanmax(abs(databuffer))                
            
            self.initPlot(xmin,xmax,ymin,ymax,titleList,xlabelList,ylabelList)
            self.__isPlotIni = True
        
        self.linearplotObj.setFigure(indexPlot)
        
        for index in range(nsubplot):
            data = databuffer[index,:]
            self.linearplotObj.plot(subplot=index+1,x=height,y=data,type=type)
        
        self.linearplotObj.refresh()
        
class RTI:
    colorplotObj = None
    
    def __init__(self, Voltage, index):
        self.__isPlotConfig = False
        self.__isPlotIni = False
        self.__xrange = None
        self.__yrange = None
        self.indexPlot = index
        self.voltageObj = Voltage

    def setup(self,indexPlot,nsubplot,winTitle='',colormap="br_green",showColorbar=False,showPowerProfile=False,XAxisAsTime=False):
        self.colorplotObj = RtiPlot(indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime)

    def initPlot(self,xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList,timezone,npoints):

        nsubplot = self.voltageObj.nChannels
        timedata = self.voltageObj.m_BasicHeader.utc

        for index in range(nsubplot):
            title = titleList[index]
            xlabel = xlabelList[index]
            ylabel = ylabelList[index]
            subplot = index
            self.colorplotObj.setup(subplot+1,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel,timedata,timezone,npoints)
            
    def plotData(self,
                 xmin=None,
                 xmax=None,
                 ymin=None,
                 ymax=None,
                 zmin=None,
                 zmax=None,
                 titleList=None,
                 xlabelList=None,
                 ylabelList=None,
                 winTitle='',
                 timezone='lt',
                 npoints=1000.0,
                 colormap="br_green",
                 showColorbar=True,
                 showPowerProfile=True,
                 XAxisAsTime=True,
                 save = False):
        
        databuffer = self.voltageObj.data
        timedata = self.voltageObj.m_BasicHeader.utc
        height = self.voltageObj.heightList
        nsubplot = self.voltageObj.nChannels
        indexPlot = self.indexPlot

        if not(self.__isPlotConfig):
            self.setup(indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime)
            self.__isPlotConfig = True

        if not(self.__isPlotIni):
            if titleList == None:
                titleList = []
                thisDatetime = datetime.datetime.fromtimestamp(timedata)
                txtdate = "Date: %s" %(thisDatetime.strftime("%d-%b-%Y"))
                for i in range(nsubplot):
                    titleList.append("Channel: %d %s" %(i, txtdate))

            if xlabelList == None:
                xlabelList = []
                for i in range(nsubplot):
                    xlabelList.append("")

            if ylabelList == None:
                ylabelList = []
                for i in range(nsubplot):
                    ylabelList.append("")

            if xmin == None: xmin = 0
            if xmax == None: xmax = 23
            if ymin == None: ymin = min(self.voltageObj.heightList)
            if ymax == None: ymax = max(self.voltageObj.heightList)                
            if zmin == None: zmin = 0
            if zmax == None: zmax = 50


            self.initPlot(xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList,timezone,npoints)
            self.__isPlotIni = True
        

        self.colorplotObj.setFigure(indexPlot)
        
        if timezone == 'lt':
            timedata = timedata - time.timezone
        
        for index in range(nsubplot):
            data = databuffer[index,:]
            self.colorplotObj.plot(subplot=index+1,x=timedata,y=height,z=data)
        
        self.colorplotObj.refresh()
        
        if save:
            self.colorplotObj.setFigure(indexPlot)
            path = "/Users/jro/Pictures"
            now = datetime.datetime.now().timetuple()
            file = "rti_img%02d_%03d_%02d%02d%02d.png"%(indexPlot,now[7],now[3],now[4],now[5])
            filename = os.path.join(path,file)
            self.colorplotObj.savePlot(indexPlot, filename)
