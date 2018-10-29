'''
Created on Feb 7, 2012

@author $Author: murco $
@version $Id: SpectraPlot.py 119 2012-09-05 17:06:09Z murco $
'''

import numpy
import os
import sys
import plplot
import datetime

path = os.path.split(os.getcwd())[0]
sys.path.append(path)

from Graphics.BaseGraph import *
from Model.Spectra import Spectra

class Spectrum:
    colorplotObj = None
    
    def __init__(self, spectraObj, index):
        self.__isPlotConfig = False
        self.__isPlotIni = False
        self.__xrange = None
        self.__yrange = None
        self.nsubplots = 0
        self.indexPlot = index
        self.spectraObj = spectraObj
    
    def setup(self,indexPlot, nsubplots, winTitle='', colormap="br_green", showColorbar=False, showPowerProfile=False, XAxisAsTime=False):
        """
        Crea un objeto colorPlot con las opciones seleccinoadas
        """
        
        self.nsubplots = nsubplots
        self.colorplotObj = PcolorPlot(indexPlot,
                                        nsubplots,
                                        winTitle,
                                        colormap,
                                        showColorbar,
                                        showPowerProfile,
                                        XAxisAsTime)
        
    def createObjects(self,xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList):
        """
        Configura cada subplot con los valores maximos y minimos incluyendo los subtitulos
        """
        
        for index in range(self.nsubplots):
            title = titleList[index]
            xlabel = xlabelList[index]
            ylabel = ylabelList[index]
            subplot = index
            self.colorplotObj.createObjects(subplot+1,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel)
    
    def initPlot(self):
        """
        Configura cada subplot con los valores maximos y minimos incluyendo los subtitulos
        """
        
        
        for index in range(self.nsubplots):
            subplot = index
            self.colorplotObj.iniPlot(subplot+1)

    
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
                 colormap = "br_green",
                 showColorbar = True,
                 showPowerProfile = True,
                 XAxisAsTime = False,
                 save = False,
                 channelList=[]):
        
        if channelList == []:
            channelList = numpy.arange(self.spectraObj.nChannels)
        
        
        nsubplots = len(channelList)
        nX = self.spectraObj.nFFTPoints
        nY = self.spectraObj.nHeights
        
        if self.spectraObj.noise == None:
            noise = numpy.ones(nsubplots)
        else:
            noise = 10.*numpy.log10(self.spectraObj.noise[channelList])
        
        datadB = 10.*numpy.log10(self.spectraObj.data_spc[channelList,:,:])    
        noisedB = 10.*numpy.log10(noise)
        
        x = numpy.arange(nX)        
        y = self.spectraObj.heightList
        
        indexPlot = self.indexPlot
        
        if not(self.__isPlotConfig):
            self.setup(indexPlot,
                       nsubplots,
                       winTitle,
                       colormap,
                       showColorbar,
                       showPowerProfile,
                       XAxisAsTime)
            
            
            self.__isPlotConfig = True
            
        if not(self.__isPlotIni):
            if titleList == None:
                titleList = []
                for i in range(nsubplots):
                    titleList.append("Channel: %d - Noise: %.2f" %(i, noise[i]))

            if xlabelList == None:
                xlabelList = []
                for i in range(nsubplots):
                    xlabelList.append("")

            if ylabelList == None:
                ylabelList = []
                for i in range(nsubplots):
                    ylabelList.append("Range (Km)")

            if xmin == None: xmin = x[0]
            if xmax == None: xmax = x[-1] 
            if ymin == None: ymin = y[0]
            if ymax == None: ymax = y[-1]                
            if zmin == None: zmin = datadB.min()
            if zmax == None: zmax = datadB.max()
            
            self.createObjects(xmin,xmax,ymin,ymax,zmin,zmax,titleList,xlabelList,ylabelList)
            self.__isPlotIni = True
        
        thisDatetime = datetime.datetime.fromtimestamp(self.spectraObj.m_BasicHeader.utc)
        pltitle = "Self Spectra - Date: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        
        self.colorplotObj.setFigure(indexPlot)
        self.colorplotObj.setNewPage(pltitle)
        self.initPlot()
        
        for channel in range(nsubplots):
            data = datadB[channel,:,:]
            subtitle = "Channel: %d - Noise: %.2f" %(channel, noise[channel])
            self.colorplotObj.plot(channel+1, x, y, data, subtitle)
        
        self.colorplotObj.refresh()
        
        if save:
            self.colorplotObj.setFigure(indexPlot)
            path = "/home/roj-idl71/tmp/"
            now = datetime.datetime.now().timetuple()
            file = "spc_img%02d_%03d_%02d%02d%02d.png"%(indexPlot,now[7],now[3],now[4],now[5])
            filename = os.path.join(path,file)
            self.colorplotObj.savePlot(indexPlot, filename)
        
        self.colorplotObj.closePage()


