'''
@author: Daniel Suarez
'''

import datetime
import numpy

from figure import Figure

class Scope(Figure):
    
    isConfig = None
    
    def __init__(self):
        
        self.isConfig = False
        self.WIDTH = 300
        self.HEIGHT = 200
        self.counter_imagwr = 0
    
    def getSubplots(self):
        
        nrow = self.nplots
        ncol = 3
        return nrow, ncol
    
    def setup(self, id, nplots, wintitle, show):
        
        self.nplots = nplots
        
        self.createFigure(id=id, 
                          wintitle=wintitle, 
                          show=show)
        
        nrow,ncol = self.getSubplots()
        colspan = 3
        rowspan = 1
        
        for i in range(nplots):
            self.addAxes(nrow, ncol, i, 0, colspan, rowspan)
    
    def plot_iq(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        yreal = y[channelIndexList,:].real
        yimag = y[channelIndexList,:].imag
        
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity - IQ"
        
        if not self.isConfig:
            nplots = len(channelIndexList)
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = min(numpy.nanmin(yreal),numpy.nanmin(yimag))
            if ymax == None: ymax = max(numpy.nanmax(yreal),numpy.nanmax(yimag))
                
            self.isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]

            axes.pline(x, yreal[i,:],
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

            axes.addpline(x, yimag[i,:], idline=1, color="red", linestyle="solid", lw=2)
            
    def plot_power(self, x, y, id, channelIndexList, thisDatetime, wintitle, show, xmin, xmax, ymin, ymax):
        y = y[channelIndexList,:] * numpy.conjugate(y[channelIndexList,:])
        yreal = y.real
        
        title = wintitle + " Scope: %s" %(thisDatetime.strftime("%d-%b-%Y %H:%M:%S"))
        xlabel = "Range (Km)"
        ylabel = "Intensity"
        
        if not self.isConfig:
            nplots = len(channelIndexList)
            
            self.setup(id=id,
                       nplots=nplots,
                       wintitle='',
                       show=show)
            
            if xmin == None: xmin = numpy.nanmin(x)
            if xmax == None: xmax = numpy.nanmax(x)
            if ymin == None: ymin = numpy.nanmin(yreal)
            if ymax == None: ymax = numpy.nanmax(yreal)
                
            self.isConfig = True
        
        self.setWinTitle(title)
        
        for i in range(len(self.axesList)):
            title = "Channel %d" %(i)
            axes = self.axesList[i]
            ychannel = yreal[i,:]
            axes.pline(x, ychannel,
                        xmin=xmin, xmax=xmax, ymin=ymin, ymax=ymax,
                        xlabel=xlabel, ylabel=ylabel, title=title)

    
    def run(self, dataOut, id, wintitle="", channelList=None,
            xmin=None, xmax=None, ymin=None, ymax=None, save=False,
            figpath='./', figfile=None, show=True, wr_period=1,
            server=None, folder=None, username=None, password=None, type='power'):
        
        """
        
        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
        """
        if dataOut.flagNoData:
            return None
        
        if channelList == None:
            channelIndexList = dataOut.channelIndexList
        else:
            channelIndexList = []
            for channel in channelList:
                if channel not in dataOut.channelList:
                    raise ValueError, "Channel %d is not in dataOut.channelList"
                channelIndexList.append(dataOut.channelList.index(channel))
        
        x = dataOut.heightList
        y = dataOut.data[channelIndexList,:] * numpy.conjugate(dataOut.data[channelIndexList,:])
        y = y.real
        
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        
        if type == "power":
            self.plot_power(dataOut.heightList, 
                            dataOut.data,
                            id, 
                            channelIndexList, 
                            thisDatetime,
                            wintitle,
                            show,
                            xmin,
                            xmax,
                            ymin,
                            ymax)
        
        if type == "iq":
            self.plot_iq(dataOut.heightList, 
                         dataOut.data,
                         id, 
                         channelIndexList, 
                         thisDatetime,
                         wintitle,
                         show,
                         xmin,
                         xmax,
                         ymin,
                         ymax)
        
        
        self.draw()
            
        if save:
            date = thisDatetime.strftime("%Y%m%d_%H%M%S")
            if figfile == None:
                figfile = self.getFilename(name = date)
            
            self.saveFigure(figpath, figfile)
            
            self.counter_imagwr += 1
            if (ftp and (self.counter_imagwr==wr_period)):
                ftp_filename = os.path.join(figpath,figfile)
                self.sendByFTP_Thread(ftp_filename, server, folder, username, password)
                self.counter_imagwr = 0
