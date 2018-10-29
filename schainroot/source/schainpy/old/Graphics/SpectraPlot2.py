import numpy
import sys
import schainPlot

class RTIFigure(schainPlot.Figure):
    
    __driverObj = None
    __isDriverOpen = False
    __isFigureOpen = False
    __isConfig = False
    __xw = None
    __yw = None
    
    xmin = None
    xmax = None
    minvalue = None
    maxvalue = None
    
    id = None
    nframes = None
    wintitle = wintitle
    colormap = None
    driver = None
    overplot = None
        
    frameObjList = []
    
    def __init__(self, id, wintitle, xw=600, yw=800, overplot=0, driver=None, colormap='br_green', *showGraphs):
        
        self.id = id
        self.wintitle = wintitle
        self.colormap = colormap
        self.driver = driver
        self.overplot = overplot
        
        self.showGraphs = showGraphs
        
        showColorbar = showGraphs[0]
        showPowerprofile = showGraphs[1]
        self.__driverObj = Driver(id, wintitle,xw,yw,overplot,driver,colormap,showColorbar,showPowerprofile)
        
    
            
    def __openDriver(self):
        
        self.__driverObj.openDriver(self.id, self.wintitle, self.xw, self.yw)
    
    def __openFigure(self):
        
        nrows, ncolumns = self.getSubplots()
        
        self.__driverObj.openFigure()
        self.__driverObj.setSubPlots(nrows, ncolumns)
        
        
    def __isOutOfXRange(self, x):
        pass
    
    def __changeXRange(self, x):
        pass

    def __createFrames(self):
        
        for frame in range(self.nframes):
            frameObj = Frame(idframe = frame,
                             showGraph1 = self.showGraph1,
                             showGraph2 = self.showGraph2
                             )
            
            self.frameObjList.append(frameObj)
            
    def plot1DArray(self, data1D, x=None, channelList=None, xmin=None, xmax=None, minvalue=None, maxvlaue=None, save=False, gpath='./'):
        
        nx, ny  = data1D.shape
        
        if channelList == None:
            chanellList = range(nx)
            
        if x == None:
            x = numpy.arange(data1D.size)
            
            
            
            
        if not(self.__isDriverOpen):
            self.__openDriver()
            self.__isDriverOpen = True
        
        if not(self.__isConfig):
            if self.xmin == None: xmin = numpy.min(x)
            if self.xmax == None: xmax = numpy.max(x)
            if self.minvalue == None: minvalue = numpy.min(data1D)
            if self.maxvalue == None: maxvalue = numpy.max(data1D)
            
            self.__createFrames()
            self.__isConfig = True
        
        
        if not(self.__isOutOfXRange(x)):
            self.__changeXRange(x)
            
            if self.__isFigureOpen:
                self.__driverObj.closePage()
                self.__isFigureOpen = False
        
        if not(self.__isFigureOpen):
            self.__openFigure()
            
            for channel in channelList:
                frameObj = self.frameObjList[channel]
                frameObj.init(xmin=xmin,
                              xmax=xmax,
                              minvalue=minvalue,
                              maxvalue=maxvalue)
                
            self.__isFigureOpen = True
            
        
        for channel in channelList:
            dataCh = data1D[channel]
            frameObj = self.frameObjList[channel]
            
            frameObj.clearData()
            frameObj.plot(dataCh)
            
            frameObj.refresh()
        
        if not(self.overplot):
            self.__driverObj.closeFigure()
            self.__isFigureOpen = False
        
            
    def plot2DArray(self, x, y, data2D, xmin=None, xmax=None, ymin=None, ymax=None, minvalue=None, maxvalue=None, save=False, gpath='./'):
        
        if not(self.__isCOpen):
            self.__createFrames()
            self.__openFigure()
            self.__isOpen = True
        
        if not(self.__isConfig):
            self.setRange(xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax, minvalue=minvalue, maxvalue=maxvalue)
            
            self.__isConfig = True
            
        for channel in channelList:
            dataCh = dataArray[channel]
            frameObj = frameObjList[channel]
            frameObj.plot(dataCh)
    
    def saveFigure(self, filename):
        pass
    
    
    def getSubplots(self):
        
        raise ValueError, ''
    
class RTIFrame(schainPlot.Frame):
    
    def __init__(self):
        pass
    
    def setup(self):
        pass

class RTIPlot(schainPlot.Plot):
    
    def __init__(self):
        pass
    
    def setup(self):
        pass