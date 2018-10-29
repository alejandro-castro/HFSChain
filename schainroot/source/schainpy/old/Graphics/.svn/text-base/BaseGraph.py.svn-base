"""
Created on Feb 7, 2012

@autor $Author: dsuarez $
@version $Id: BaseGraph.py 117 2012-09-04 21:16:59Z dsuarez $

"""
import os
import numpy
import sys
import time 
import datetime
import time
import plplot


def cmap1_init(colormap="gray"):
    
    if colormap == None:
        return
        
    ncolor = None
    rgb_lvl = None
    
    # Routine for defining a specific color map 1 in HLS space.
    # if gray is true, use basic grayscale variation from half-dark to light.
    # otherwise use false color variation from blue (240 deg) to red (360 deg).

    # Independent variable of control points.
    i = numpy.array((0., 1.))
    if colormap=="gray":
        ncolor = 256
        # Hue for control points.  Doesn't matter since saturation is zero.
        h = numpy.array((0., 0.))
        # Lightness ranging from half-dark (for interest) to light.
        l = numpy.array((0.5, 1.))
        # Gray scale has zero saturation
        s = numpy.array((0., 0.))
        
        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
    
    if colormap == 'jet':
        ncolor = 256          
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        
        for i in range(ncolor):
            if(i <= 35.0/100*(ncolor-1)): rf = 0.0
            elif (i <= 66.0/100*(ncolor-1)): rf = (100.0/31)*i/(ncolor-1) - 35.0/31
            elif (i <= 89.0/100*(ncolor-1)): rf = 1.0
            else: rf = (-100.0/22)*i/(ncolor-1) + 111.0/22
    
            if(i <= 12.0/100*(ncolor-1)): gf = 0.0
            elif(i <= 38.0/100*(ncolor-1)): gf = (100.0/26)*i/(ncolor-1) - 12.0/26
            elif(i <= 64.0/100*(ncolor-1)): gf = 1.0
            elif(i <= 91.0/100*(ncolor-1)): gf = (-100.0/27)*i/(ncolor-1) + 91.0/27
            else: gf = 0.0
    
            if(i <= 11.0/100*(ncolor-1)): bf = (50.0/11)*i/(ncolor-1) + 0.5
            elif(i <= 34.0/100*(ncolor-1)): bf = 1.0
            elif(i <= 65.0/100*(ncolor-1)): bf = (-100.0/31)*i/(ncolor-1) + 65.0/31
            else: bf = 0           
            
            r[i] = rf
            g[i] = gf
            b[i] = bf
        
            pos[i] = float(i)/float(ncolor-1)
        

        plplot.plscmap1n(ncolor)
        plplot.plscmap1l(1, pos, r, g, b)
    
    
    
    if colormap=="br_green":
        ncolor = 256
        # Hue ranges from blue (240 deg) to red (0 or 360 deg)
        h = numpy.array((240., 0.))
        # Lightness and saturation are constant (values taken from C example).
        l = numpy.array((0.6, 0.6))
        s = numpy.array((0.8, 0.8))

        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
    
    if colormap=="tricolor":
        ncolor = 3
        # Hue ranges from blue (240 deg) to red (0 or 360 deg)
        h = numpy.array((240., 0.))
        # Lightness and saturation are constant (values taken from C example).
        l = numpy.array((0.6, 0.6))
        s = numpy.array((0.8, 0.8))

        # number of cmap1 colours is 256 in this case.
        plplot.plscmap1n(ncolor)
        # Interpolate between control points to set up cmap1.
        plplot.plscmap1l(0, i, h, l, s)
        
        return None
    
    if colormap == 'rgb' or colormap == 'rgb666':
        
        color_sz = 6
        ncolor = color_sz*color_sz*color_sz
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(color_sz):
            for gi in range(color_sz):
                for bi in range(color_sz):
                    r[ind] = ri/(color_sz-1.0)
                    g[ind] = gi/(color_sz-1.0)
                    b[ind] = bi/(color_sz-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,6,6]  #Levels for RGB colors
        
    if colormap == 'rgb676':
        ncolor = 6*7*6
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(6-1.0)
                    g[ind] = gi/(7-1.0)
                    b[ind] = bi/(6-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,7,6]  #Levels for RGB colors
    
    if colormap == 'rgb685':
        ncolor = 6*8*5
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(6-1.0)
                    g[ind] = gi/(8-1.0)
                    b[ind] = bi/(5-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [6,8,5]  #Levels for RGB colors
                    
    if colormap == 'rgb884':
        ncolor = 8*8*4
        pos = numpy.zeros((ncolor))
        r = numpy.zeros((ncolor))
        g = numpy.zeros((ncolor))
        b = numpy.zeros((ncolor))
        ind = 0
        for ri in range(8):
            for gi in range(8):
                for bi in range(4):
                    r[ind] = ri/(8-1.0)
                    g[ind] = gi/(8-1.0)
                    b[ind] = bi/(4-1.0)
                    pos[ind] = ind/(ncolor-1.0)
                    ind += 1
        rgb_lvl = [8,8,4]  #Levels for RGB colors
    
    if ncolor == None:
        raise ValueError, "The colormap selected is not valid"
    
    plplot.plscmap1n(ncolor)
    plplot.plscmap1l(1, pos, r, g, b)
    
    return rgb_lvl

def setColormap(colormap="jet"):
    cmap1_init(colormap)

def savePlplot(filename,width,height):
    curr_strm = plplot.plgstrm()
    save_strm = plplot.plmkstrm()
    plplot.plsetopt("geometry", "%dx%d"%(width,height))
    plplot.plsdev("png")
    plplot.plsfnam(filename)
    plplot.plcpstrm(curr_strm,0)
    plplot.plreplot()
    plplot.plend1()
    plplot.plsstrm(curr_strm)
    

def initPlplot(indexPlot,ncol,nrow,winTitle,width,height):
    plplot.plsstrm(indexPlot)
    plplot.plparseopts([winTitle],plplot.PL_PARSE_FULL)
    plplot.plsetopt("geometry", "%dx%d"%(width*ncol,height*nrow))
    plplot.plsdev("xwin")
    plplot.plscolbg(255,255,255)
    plplot.plscol0(1,0,0,0)
    plplot.plinit()
    plplot.plspause(False)
    plplot.plssub(ncol,nrow)

def setNewPage():
    plplot.plbop()
    plplot.pladv(0)

def closePage():
    plplot.pleop()
    
def clearData(objGraph):
    objGraph.plotBox(objGraph.xrange[0], objGraph.xrange[1], objGraph.yrange[0], objGraph.yrange[1], "bc", "bc")
    
    objGraph.setColor(15) #Setting Line Color to White
    
    if objGraph.datatype == "complex":        
        objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata.real)
        objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata.imag)

    if objGraph.datatype == "real":
        objGraph.basicXYPlot(objGraph.xdata,objGraph.ydata)
    
    objGraph.setColor(1) #Setting Line Color to Black
#    objGraph.setLineStyle(2)
#    objGraph.plotBox(objGraph.xrange[0], objGraph.xrange[1], objGraph.yrange[0], objGraph.yrange[1], "bcntg", "bc")
#    objGraph.setLineStyle(1)

def setStrm(indexPlot):
    plplot.plsstrm(indexPlot)

def plFlush():
    plplot.plflush()

def plShow():
    plplot.plspause(True)
    plplot.plend()
    
def setPlTitle(pltitle,color, szchar=0.7):
    setSubpages(1, 0)
    plplot.pladv(0)
    plplot.plvpor(0., 1., 0., 1.)
    
    if color == "black":
        plplot.plcol0(1)
    if color == "white":
        plplot.plcol0(15)
    
    plplot.plschr(0.0,szchar)
    plplot.plmtex("t",-1., 0.5, 0.5, pltitle)
    
def setSubpages(ncol,nrow):
    plplot.plssub(ncol,nrow)

class BaseGraph:
    
    __name = None
    __xpos = None
    __ypos = None
    __subplot = None
    __xg = None
    __yg = None
    xdata = None
    ydata = None
    getGrid = True
    xaxisIsTime = False
    deltax = None
    xmin = None
    xmax = None
    
    def __init__(self,name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange=None,deltax=1.0):
        
        self.setName(name)
        self.setScreenPos(xpos, ypos)
        self.setLabels(xlabel,ylabel,title)
        self.setSubPlot(subplot)
        self.setSizeOfChar(szchar)
        self.setXYZrange(xrange,yrange,zrange)
        self.getGrid = True
        self.xaxisIsTime = False
        self.deltax = deltax
    
    def setXYZrange(self,xrange,yrange,zrange):
        self.xrange = xrange
        self.yrange = yrange
        self.zrange = zrange
        
    def setName(self, name):
        self.__name = name
    
    def setScreenPos(self,xpos,ypos):
        self.__xpos = xpos
        self.__ypos = ypos
    
    def setXYData(self,xdata=None,ydata=None,datatype="real"):
        if((xdata != None) and (ydata != None)):
            self.xdata = xdata
            self.ydata = ydata
            self.datatype = datatype
            
        if((self.xdata == None) and (self.ydata == None)):
            return None
        
        return 1
    
    
    def setLabels(self,xlabel=None,ylabel=None,title=None):
        if xlabel != None: self.xlabel = xlabel
        if ylabel != None: self.ylabel = ylabel
        if title != None: self.title = title
    
    def setSubPlot(self,subplot):
        self.__subplot = subplot
    
    def setSizeOfChar(self,szchar):
        self.__szchar = szchar
        
    def setLineStyle(self,style):
        plplot.pllsty(style)
    
    def setColor(self,color):
        plplot.plcol0(color)
    
    def setXAxisAsTime(self,value=False):
        self.xaxisIsTime = value
    
    def basicLineTimePlot(self, x, y, xmin=None, xmax=None, ymin=None, ymax=None, colline=1):
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        plplot.plcol0(colline)
        plplot.plline(x, y)
        plplot.plcol0(1)
    
    def basicXYPlot(self, x, y, xmin=None, xmax=None, ymin=None, ymax=None):
        
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        
        plplot.plline(x, y)
    
    def basicPcolorPlot(self, data, x, y, xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None):
        """
        """
        if xmin == None: xmin = x[0]
        if xmax == None: xmax = x[-1]
        if ymin == None: ymin = y[0]
        if ymax == None: ymax = y[-1]
        if zmin == None: zmin = numpy.nanmin(data)
        if zmax == None: zmax = numpy.nanmax(data)
        
        plplot.plimage(data,
                       float(x[0]),
                       float(x[-1]),
                       float(y[0]),
                       float(y[-1]),
                       float(zmin),
                       float(zmax),
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax)
                       )
    
    def __getBoxpltr(self, x, y, deltax=None, deltay=None):        
        
        if not(len(x)>0 and len(y)>0):
            raise ValueError, "x axis and y axis are empty"
        
        if deltax == None: deltax = x[-1] - x[-2]
        if deltay == None: deltay = y[-1] - y[-2]
        
        x1 = numpy.append(x, x[-1] + deltax)
        y1 = numpy.append(y, y[-1] + deltay)
        
        xg = (numpy.multiply.outer(x1, numpy.ones(len(y1))))
        yg = (numpy.multiply.outer(numpy.ones(len(x1)), y1))
        
        self.__xg = xg
        self.__yg = yg
        
        return xg, yg
    
    
    def advPcolorPlot(self, data, x, y, xmin=None, xmax=None, ymin=None, ymax=None, zmin=0., zmax=0., deltax=1.0, deltay=None, getGrid = True):
        if getGrid:
            xg, yg = self.__getBoxpltr(x, y, deltax, deltay)
        else:
            xg = self.__xg
            yg = self.__yg    
        
        plplot.plimagefr(data, 
                         float(xmin), 
                         float(xmax), 
                         float(ymin), 
                         float(ymax), 
                         0., 
                         0., 
                         float(zmin), 
                         float(zmax), 
                         plplot.pltr2, 
                         xg, 
                         yg)


    def colorbarPlot(self, xmin=0., xmax=1., ymin=0., ymax=1.):
        data = numpy.arange(256)
        data = numpy.reshape(data, (1,-1))
        
        plplot.plimage(data,
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax),
                       0.,
                       255.,
                       float(xmin),
                       float(xmax),
                       float(ymin),
                       float(ymax))

    def plotBox(self, xmin, xmax, ymin, ymax, xopt, yopt, nolabels=False):
        
        plplot.plschr(0.0,self.__szchar-0.05)
        plplot.pladv(self.__subplot)
        plplot.plvpor(self.__xpos[0], self.__xpos[1], self.__ypos[0], self.__ypos[1])
        plplot.plwind(float(xmin), # self.xrange[0]
                      float(xmax), # self.xrange[1]
                      float(ymin), # self.yrange[0]
                      float(ymax) # self.yrange[1]
                      )
        
        
        
        if self.xaxisIsTime:
            plplot.pltimefmt("%H:%M")
            timedelta = (xmax - xmin + 1)/8.
            plplot.plbox(xopt, timedelta, 3, yopt, 0.0, 0)
        else:
            plplot.plbox(xopt, 0.0, 0, yopt, 0.0, 0)
        
        
        if not(nolabels):
            plplot.pllab(self.xlabel, self.ylabel, self.title)


    def delLabels(self):
        self.setColor(15) #Setting Line Color to White
        plplot.pllab(self.xlabel, self.ylabel, self.title)
        self.setColor(1) #Setting Line Color to Black
        
        
    
    def plotImage(self,x,y,z,xrange,yrange,zrange):
        xi = x[0]
        xf = x[-1]
        yi = y[0]
        yf = y[-1]
        
        plplot.plimage(z, 
                       float(xi), 
                       float(xf), 
                       float(yi), 
                       float(yf), 
                       float(zrange[0]), 
                       float(zrange[1]), 
                       float(xi), 
                       float(xf), 
                       float(yrange[0]), 
                       yrange[1])

class LinearPlot:
    linearObjDic = {}
    __xpos = None
    __ypos = None
    def __init__(self,indexPlot,nsubplot,winTitle):
        self.width = 700
        self.height = 150
        ncol = 1
        nrow = nsubplot
        initPlplot(indexPlot,ncol,nrow,winTitle,self.width,self.height)
    
    
    def setFigure(self,indexPlot):
        setStrm(indexPlot)
        
    def setPosition(self): 
        
        xi = 0.07; xf = 0.9 #0.8,0.7,0.5 
        yi = 0.15; yf = 0.8
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__xpos = xpos
        self.__ypos = ypos
        
        return xpos,ypos
    
    def show(self):
        plShow()
        
    def refresh(self):
        plFlush()
        
    def setup(self,subplot,xmin,xmax,ymin,ymax,title,xlabel,ylabel):
        szchar = 1.10
        name = "linear"
        key = name + "%d"%subplot
        xrange = [xmin,xmax]
        yrange = [ymin,ymax]
        
        xpos,ypos = self.setPosition()
        linearObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange)
        linearObj.plotBox(linearObj.xrange[0], linearObj.xrange[1], linearObj.yrange[0], linearObj.yrange[1], "bcnst", "bcnstv")
        self.linearObjDic[key] = linearObj
    
    def plot(self,subplot,x,y,type="power"):
        name = "linear"
        key = name + "%d"%subplot
        
        linearObj = self.linearObjDic[key]
        linearObj.plotBox(linearObj.xrange[0], linearObj.xrange[1], linearObj.yrange[0], linearObj.yrange[1], "bcst", "bcst")
        
        if linearObj.setXYData() != None:
                clearData(linearObj)
                
        else:
            if type.lower() == 'simple':
                linearObj.setXYData(x,y,"real")
            if type.lower() == 'power':
                linearObj.setXYData(x,abs(y),"real")
            if type.lower() == 'iq':
                linearObj.setXYData(x,y,"complex")
        
        if type.lower() == 'simple':
            colline = 9
            linearObj.basicLineTimePlot(x, y, xmin, xmax, ymin, ymax, colline)
            linearObj.setXYData(x,y,"real")
        
        if type.lower() == 'power':
            colline = 9
            linearObj.basicLineTimePlot(x, abs(y), xmin, xmax, ymin, ymax, colline)
            linearObj.setXYData(x,abs(y),"real")
        
        if type.lower() == 'iq':
            colline = 9
            linearObj.basicLineTimePlot(x=x, y=y.real, colline=colline)
            colline = 13
            linearObj.basicLineTimePlot(x=x, y=y.imag, colline=colline)
            
            linearObj.setXYData(x,y,"complex")
        
        linearObj.plotBox(linearObj.xrange[0], linearObj.xrange[1], linearObj.yrange[0], linearObj.yrange[1], "bcst", "bcst")
        
        
#        linearObj.plotBox(linearObj.xrange[0], linearObj.xrange[1], linearObj.yrange[0], linearObj.yrange[1], "bc", "bc")
#        linearObj.basicXYPlot(data,y)
#        linearObj.setXYData(data,y)
        
    

class PcolorPlot:
    pcolorObjDic = {}
    colorbarObjDic = {}
    pwprofileObjDic = {}
    showColorbar = None
    showPowerProfile = None
    XAxisAsTime = None
    width = None
    height = None
    __spcxpos = None
    __spcypos = None
    __cmapxpos = None
    __cmapypos = None
    __profxpos = None
    __profypos = None
    __lastTitle = None
    
    def __init__(self,indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime):
        self.width = 460
        self.height = 300
        self.showColorbar = showColorbar
        self.showPowerProfile = showPowerProfile
        self.XAxisAsTime = XAxisAsTime
        
        
        ncol = int(numpy.sqrt(nsubplot)+0.9)
        nrow = int(nsubplot*1./ncol + 0.9)
        
        initPlplot(indexPlot,ncol,nrow,winTitle,self.width,self.height)
        setColormap(colormap)
        self.ncol = ncol
        self.nrow = nrow

    def setFigure(self,indexPlot):
        setStrm(indexPlot)

    def setSpectraPos(self): #modificar valores de acuerdo al colorbar y pwprofile
        if self.showPowerProfile: xi = 0.09; xf = 0.6 #0.075
        else:   xi = 0.15; xf = 0.8 #0.8,0.7,0.5 
        yi = 0.15; yf = 0.80
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__spcxpos = xpos
        self.__spcypos = ypos
        
        return xpos,ypos
    
    def setColorbarScreenPos(self):
                        
        xi = self.__spcxpos[1] + 0.03; xf = xi + 0.03
        yi = self.__spcypos[0]; yf = self.__spcypos[1]
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__cmapxpos = xpos
        self.__cmapypos = ypos

        return xpos,ypos
    
    def setPowerprofileScreenPos(self):
        
        xi = self.__cmapxpos[1] + 0.07; xf = xi + 0.25
        yi = self.__spcypos[0]; yf = self.__spcypos[1]
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__profxpos = [xi,xf]
        self.__profypos = [yi,yf]

        return xpos,ypos
    
    def createObjects(self,subplot,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel):
        """
        Crea los objetos necesarios para un subplot
        """
        
        # Config Spectra plot
        
        szchar = 0.7
        name = "spc"
        key = name + "%d"%subplot
        xrange = [xmin,xmax]
        yrange = [ymin,ymax]
        zrange = [zmin,zmax]
        
        xpos,ypos = self.setSpectraPos()
        pcolorObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange)
        self.pcolorObjDic[key] = pcolorObj
        
        # Config Colorbar
        if self.showColorbar:
            szchar = 0.65
            name = "colorbar"
            key = name + "%d"%subplot
            
            xpos,ypos = self.setColorbarScreenPos()
            xrange = [0.,1.]
            yrange = [zmin,zmax]
            cmapObj = BaseGraph(name,subplot,xpos,ypos,"","","dB",szchar,xrange,yrange)
            self.colorbarObjDic[key] = cmapObj
        
        # Config Power profile
        if self.showPowerProfile:
            szchar = 0.55
            name = "pwprofile"
            key = name + "%d"%subplot
            
            xpos,ypos = self.setPowerprofileScreenPos()
            xrange = [zmin,zmax]
            yrange = [ymin,ymax]
            powObj = BaseGraph(name,subplot,xpos,ypos,"dB","","Power Profile",szchar,xrange,yrange)
            self.pwprofileObjDic[key] = powObj
    
    def setNewPage(self, pltitle='No title'):
        szchar = 0.7
        setNewPage()
        setPlTitle(pltitle,"black", szchar=szchar)
        setSubpages(self.ncol, self.nrow)
        
    def closePage(self):
        closePage()
        
    def iniPlot(self,subplot):
        """
        Inicializa los subplots con su frame, titulo, etc
        """
        
        # Config Spectra plot
        name = "spc"
        key = name + "%d"%subplot
        
        pcolorObj = self.pcolorObjDic[key]
        pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], "bcnst", "bcnstv")
        
        # Config Colorbar
        if self.showColorbar:
            name = "colorbar"
            key = name + "%d"%subplot
            
            cmapObj = self.colorbarObjDic[key]
            cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], "bc", "bcmtsv")
            cmapObj.colorbarPlot(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1])
#            cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], "bc", "bcmtsv")
            
        # Config Power profile
        if self.showPowerProfile:
            name = "pwprofile"
            key = name + "%d"%subplot
            
            powObj = self.pwprofileObjDic[key]
            powObj.setLineStyle(2)
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bcntg", "bc")
            powObj.setLineStyle(1)
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bc", "bc")
    
    def printTitle(self,pltitle):
#        if self.__lastTitle != None:
#            setPlTitle(self.__lastTitle,"white")
#            
#        self.__lastTitle = pltitle
        
        setPlTitle(pltitle,"black")
        
#        setSubpages(self.ncol,self.nrow)
        
    def plot(self,subplot,x,y,z,subtitle):
        # Spectra plot
        
        name = "spc"
        key = name + "%d"%subplot
        
#        newx = [x[0],x[-1]]
        pcolorObj = self.pcolorObjDic[key]
        
        pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], "bcst", "bcst")
        
        #pcolorObj.delLabels()
        pcolorObj.setLabels(title=subtitle)

        deltax = None; deltay = None
        
        pcolorObj.advPcolorPlot(z, 
                                x,
                                y, 
                                xmin=pcolorObj.xrange[0], 
                                xmax=pcolorObj.xrange[1], 
                                ymin=pcolorObj.yrange[0], 
                                ymax=pcolorObj.yrange[1], 
                                zmin=pcolorObj.zrange[0], 
                                zmax=pcolorObj.zrange[1],
                                deltax=deltax, 
                                deltay=deltay, 
                                getGrid=pcolorObj.getGrid)
        
        #Solo se calcula la primera vez que se ingresa a la funcion
        pcolorObj.getGrid = False
        
        pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], "bcst", "bcst", nolabels=True)
        
        # Power Profile
        if self.showPowerProfile:
            power = numpy.average(z, axis=0)
            name = "pwprofile"
            key = name + "%d"%subplot
            powObj = self.pwprofileObjDic[key]
            
            if powObj.setXYData() != None:
                #clearData(powObj)
                powObj.setLineStyle(2)
                powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bcntg", "bc")
                powObj.setLineStyle(1)
            else:
                powObj.setXYData(power,y)
            
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bc", "bc")
            powObj.basicXYPlot(power,y)
            powObj.setXYData(power,y)
    
    def savePlot(self,indexPlot,filename):
        
        width = self.width*self.ncol
        hei = self.height*self.nrow
        savePlplot(filename,width,hei)
    
    def refresh(self):
        plFlush()

class RtiPlot:
    
    pcolorObjDic = {}
    colorbarObjDic = {}
    pwprofileObjDic = {}
    showColorbar = None
    showPowerProfile = None
    XAxisAsTime = None
    widht = None
    height = None
    __rtixpos = None
    __rtiypos = None
    __cmapxpos = None
    __cmapypos = None
    __profxpos = None
    __profypos = None
    
    def __init__(self,indexPlot,nsubplot,winTitle,colormap,showColorbar,showPowerProfile,XAxisAsTime):
        self.width = 700
        self.height = 150
        self.showColorbar = showColorbar
        self.showPowerProfile = showPowerProfile
        self.XAxisAsTime = XAxisAsTime
        
        ncol = 1
        nrow = nsubplot
        initPlplot(indexPlot,ncol,nrow,winTitle,self.width,self.height)
        setColormap(colormap)
        self.ncol = ncol
        self.nrow = nrow
    
    def setFigure(self,indexPlot):
        setStrm(indexPlot)
    
    def setRtiScreenPos(self):
                    
        if self.showPowerProfile: xi = 0.07; xf = 0.65
        else:   xi = 0.07; xf = 0.9 
        yi = 0.15; yf = 0.80
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__rtixpos = xpos
        self.__rtiypos = ypos
        
        return xpos,ypos
    
    def setColorbarScreenPos(self):
                        
        xi = self.__rtixpos[1] + 0.03; xf = xi + 0.03
        
        yi = self.__rtiypos[0]; yf = self.__rtiypos[1]
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__cmapxpos = xpos
        self.__cmapypos = ypos

        return xpos,ypos
    
    def setPowerprofileScreenPos(self):
        
        xi = self.__cmapxpos[1] + 0.05; xf = xi + 0.20

        yi = self.__rtiypos[0]; yf = self.__rtiypos[1]
        
        xpos = [xi,xf]
        ypos = [yi,yf]
        
        self.__profxpos = [xi,xf]
        self.__profypos = [yi,yf]

        return xpos,ypos

    def setup(self,subplot,xmin,xmax,ymin,ymax,zmin,zmax,title,xlabel,ylabel,timedata,timezone="lt",npoints=100):
        # Config Rti plot
        szchar = 1.10
        name = "rti"
        key = name + "%d"%subplot
        
        # xmin, xmax --> minHour, max Hour : valores que definen el ejex x=[horaInicio,horaFinal]
        thisDateTime = datetime.datetime.fromtimestamp(timedata)
        startDateTime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmin,0,0)
        endDateTime = datetime.datetime(thisDateTime.year,thisDateTime.month,thisDateTime.day,xmax,59,59)
        deltaTime = 0
        if timezone == "lt":
            deltaTime = time.timezone
        startTimeInSecs = time.mktime(startDateTime.timetuple()) - deltaTime
        endTimeInSecs = time.mktime(endDateTime.timetuple()) - deltaTime
        
        xrange = [startTimeInSecs,endTimeInSecs]
        totalTimeInXrange = endTimeInSecs - startTimeInSecs + 1.
        deltax = totalTimeInXrange / npoints
        
        yrange = [ymin,ymax]
        zrange = [zmin,zmax] 
        
        xpos,ypos = self.setRtiScreenPos()
        pcolorObj = BaseGraph(name,subplot,xpos,ypos,xlabel,ylabel,title,szchar,xrange,yrange,zrange,deltax)
        if self.XAxisAsTime:
            pcolorObj.setXAxisAsTime(self.XAxisAsTime)
            xopt = "bcnstd"
            yopt = "bcnstv"
        else:
            xopt = "bcnst"
            yopt = "bcnstv"
        
        pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], xopt, yopt)
        self.pcolorObjDic[key] = pcolorObj
        

        # Config Colorbar
        if self.showColorbar:
            szchar = 0.9
            name = "colorbar"
            key = name + "%d"%subplot
            
            xpos,ypos = self.setColorbarScreenPos()
            xrange = [0.,1.]
            yrange = [zmin,zmax]
            cmapObj = BaseGraph(name,subplot,xpos,ypos,"","","dB",szchar,xrange,yrange)
            cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], "bc", "bcm")
            cmapObj.colorbarPlot(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1])
            cmapObj.plotBox(cmapObj.xrange[0], cmapObj.xrange[1], cmapObj.yrange[0], cmapObj.yrange[1], "bc", "bcmtsv")
            self.colorbarObjDic[key] = cmapObj
        
        
        # Config Power profile
        if self.showPowerProfile:
            szchar = 0.8
            name = "pwprofile"
            key = name + "%d"%subplot
            
            xpos,ypos = self.setPowerprofileScreenPos()
            xrange = [zmin,zmax]
            yrange = [ymin,ymax]
            powObj = BaseGraph(name,subplot,xpos,ypos,"dB","","Power Profile",szchar,xrange,yrange)
            powObj.setLineStyle(2)
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bcntg", "bc")
            powObj.setLineStyle(1)
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bc", "bc")
            self.pwprofileObjDic[key] = powObj

    
    def plot(self,subplot,x,y,z):
        # RTI plot
        name = "rti"
        key = name + "%d"%subplot
        
        data = numpy.reshape(z, (1,-1))
        data = numpy.abs(data)
        data = 10*numpy.log10(data)
        newx = [x,x+1]
        
        pcolorObj = self.pcolorObjDic[key]
        
        if pcolorObj.xaxisIsTime:
            xopt = "bcstd"
            yopt = "bcst"
        else:
            xopt = "bcst"
            yopt = "bcst"
            
        pcolorObj.plotBox(pcolorObj.xrange[0], pcolorObj.xrange[1], pcolorObj.yrange[0], pcolorObj.yrange[1], xopt, yopt)
        
        deltax = pcolorObj.deltax
        deltay = None
        
        if pcolorObj.xmin == None and pcolorObj.xmax == None:
            pcolorObj.xmin = x
            pcolorObj.xmax = x
        
        if x >= pcolorObj.xmax:
            xmin = x
            xmax = x + deltax
            x = [x]
            pcolorObj.advPcolorPlot(data, 
                                    x, 
                                    y, 
                                    xmin=xmin, 
                                    xmax=xmax, 
                                    ymin=pcolorObj.yrange[0], 
                                    ymax=pcolorObj.yrange[1], 
                                    zmin=pcolorObj.zrange[0], 
                                    zmax=pcolorObj.zrange[1],
                                    deltax=deltax, 
                                    deltay=deltay, 
                                    getGrid=pcolorObj.getGrid)
            
            pcolorObj.xmin = xmin
            pcolorObj.xmax = xmax
            
        
        # Power Profile
        if self.showPowerProfile:
            data = numpy.reshape(data,(numpy.size(data)))
            name = "pwprofile"
            key = name + "%d"%subplot
            powObj = self.pwprofileObjDic[key]
            
            if powObj.setXYData() != None:
                clearData(powObj)
                powObj.setLineStyle(2)
                powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bcntg", "bc")
                powObj.setLineStyle(1)
            else:
                powObj.setXYData(data,y)
            
            powObj.plotBox(powObj.xrange[0], powObj.xrange[1], powObj.yrange[0], powObj.yrange[1], "bc", "bc")
            powObj.basicXYPlot(data,y)
            powObj.setXYData(data,y)
            
    def savePlot(self,indexPlot,filename):
        
        width = self.width*self.ncol
        hei = self.height*self.nrow
        savePlplot(filename,width,hei)
        
    def refresh(self):
        plFlush()

if __name__ == '__main__':
    
    #Setting the signal
    fs = 8000
    f0 = 200
    f1 = 400
    T = 1./fs
    x = numpy.arange(160)
    y1 = numpy.sin(2*numpy.pi*f0*x*T)
    y2 = numpy.sin(2*numpy.pi*f1*x*T)
    signalList = [y1,y2]
    
    xmin = numpy.min(x)
    xmax = numpy.max(x)
    ymin = numpy.min(y1)
    ymax = numpy.max(y1)
    
    # Creating Object
    indexPlot = 1
    nsubplot = 2
    winTitle = "mi grafico v1"
    
    subplotTitle = "subplot - No."
    xlabel = ""
    ylabel = ""
    
    linearObj = LinearPlot(indexPlot,nsubplot,winTitle)
    
    #Config SubPlots
    for subplot in range(nsubplot):
        indexplot = subplot + 1
        title = subplotTitle + '%d'%indexplot
        linearObj.setup(indexplot, xmin, xmax, ymin, ymax, title, xlabel, ylabel)
    
    #Plotting
    type = "simple"
    for subplot in range(nsubplot):
        indexplot = subplot + 1
        y = signalList[subplot]
        linearObj.plot(indexplot, x, y, type)
        
    linearObj.refresh()
    linearObj.show()

    print "end"