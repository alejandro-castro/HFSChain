import numpy
from schainPlot import *


class RTIFigure(Figure):
    
    overplot = 1 # igual a 1 porque el grafico es RTI, para el caso de Spectra(Spc,CrossSpc) overplot = 0
    xw = 700
    yw = 150
    nframes = None
    
    def __init__(self, idfigure, nframes, wintitle, colormap, driver, showColorbar, showPowerProfile):
        
        showGraphs = (showColorbar, showPowerProfile)
        
        Figure.__init__(self, 
                        idfigure=idfigure, 
                        nframes = nframes,
                        wintitle=wintitle, 
                        xw=self.xw, 
                        yw=self.yw, 
                        overplot=self.overplot, 
                        driver=driver, 
                        colormap=colormap, 
                        *showGraphs)
        
        self.nframes = nframes
        self.showColorbar = showColorbar 
        self.showPowerProfile = showPowerProfile
    
    def getSubplots(self):
        nrows = self.nframes 
        ncolumns = 1
        
        return nrows, ncolumns
        
    def __createFrames(self):
        for frame in range(self.nframes):
            frameObj = RTIFrame(idFrame = frame,
                             showGraph1 = self.showColorbar,
                             showGraph2 = self.showPowerProfile
                             )
            
            self.frameObjList.append(frameObj)

    
class RTIFrame(Frame):
    def __init__(self,idFrame, showColorbar, showPowerProfile):
        self.idFrame = idFrame
        self.showGraph1 = showColorbar
        self.showGraph2 = showPowerProfile
    
    def setXYPos(self):
        pass

class SelfSpcFigure(Figure):
    def __init__(self):
        pass
    
class SelfSpcFrame(Frame):
    def __init__(self):
        pass

class CrossSpcFigure(Figure):
    def __init__(self):
        pass

class CrossSpcFrame(Frame):
    def __init__(self):
        pass

class ScopeFigure(Figure):
    def __init__(self):
        pass

class ScopeFrame(Frame):
    def __init__(self):
        pass
    
