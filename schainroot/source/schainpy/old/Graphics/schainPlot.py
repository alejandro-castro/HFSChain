
import numpy
import schainPlplotLib

class Figure:
    
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
    
    idfigure = None
    nframes = None
    wintitle = wintitle
    colormap = None
    driver = None
    overplot = None
        
    frameObjList = []
    
    def __init__(self, idfigure, nframes, wintitle, xw=600, yw=800, overplot=0, driver='plplot', colormap='br_green', *showGraphs):
        
        self.driver = driver
        self.idfigure = idfigure
        self.nframes = nframes
        self.wintitle = wintitle
        self.overplot = overplot
        self.colormap = colormap

        self.showGraph1 = showGraphs[0]
        self.showGraph2 = showGraphs[1]
        self.__xw = xw
        self.__yw = yw
        
        self.__driverObj = Driver(driver, idfigure, xw, yw, wintitle, overplot, colormap, *showGraphs)
        
        self.__driverObj.driver.configDriver()
        
            
    def __openDriver(self):
        
        self.__driverObj.driver.openDriver()
    
    def __openFigure(self):
        
        nrows, ncolumns = self.getSubplots()
        
        self.__driverObj.driver.openFigure()
        self.__driverObj.driver.setSubPlots(nrows, ncolumns)
        
        
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

        raise ValueError, "No implemented"
        
class Frame:
    
    """
        subplots
    """
    
    plotObjList = []
    
    def __init__(self, idframe, showGraph1=False, showGraph2=False):
        
        self.idframe = idframe
        self.showGraph1 = showGraph1
        self.showGraph2 = showGraph2
        
        self.nplots = 1 + showGraph1 + showGraph2
        self.__createPlots()
    
    def __createPlots(self):
        
        for nplot in range(self.nplots):
            xi, yi, xw, yw = self.__getScreenPos(nplot)
            plotObj = Plot(xi, yi, xw, yw)
            
            self.plotObjList.append(plotObj)
            
    def __getScreenPosMainPlot(self):
        
        """
        Calcula las coordenadas asociadas al plot principal.
        """
        
        xi = 1.2
        yi = 2.3
        xw = 2.0
        yw = 1.4
        
        return xi, yi, xw, yw
        
    def __getScreenPosGraph1(self):
        xi = 1.2
        yi = 2.3
        xw = 2.0
        yw = 1.4
        
        return xi, yi, xw, yw
    
    def __getScreenPosGraph2(self):
        xi = 1.2
        yi = 2.3
        xw = 2.0
        yw = 1.4
        
        return xi, yi, xw, yw
            
    def __getScreenPos(self, nplot):
        
        if nplot == 0:
            xi, yi, xw, yw = self.__getScreenPosMain()
        if nplot == 1:
            xi, yi, xw, yw = self.__getScreenPosMain()
        if nplot == 2:
            xi, yi, xw, yw = self.__getScreenPosMain()
        
        return xi, yi, xw, yw

              
    def init(self, xmin, xmax, ymin, yamx, minvalue, maxvalue):
        
        """
        """
        
        for plotObj in self.plotObjList:
            plotObj.plotBox(xmin, xmax, ymin, yamx, minvalue, maxvalue)
    
    def clearData(self):
        pass

    def plot(self, data):
        
        for plotObj in self.plotObjList:
            plotObj.plotData(data)
        
    def refresh(self):
        pass    
    


class Plot:
    
    def __init__(self, xi, yi, xw, yw):
        
        self.xi = xi
        self.yi = yi
        self.xw = xw
        self.yw = yw
    
    def __setRange(self, xrange, yrange, zrange):
        pass
    
    def __setLabels(self, xlabel, ylabel, zlabel):
        pass

    
    def plotBox(self,xmin, xmax, ymin, yamx, minvalue, maxvalue):
        pass
    
    def plotData(self):
        
        raise ValueError, ""
    
