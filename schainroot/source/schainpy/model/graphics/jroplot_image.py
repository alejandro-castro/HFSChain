'''
Created on Jul 9, 2014

@author: roj-idl71
'''
import os
import datetime
import numpy
#import plplot
import matplotlib.pyplot as plt
from model.proc.jroproc_base import Operation
#from figure import Figure, isRealtime, isTimeInHourRange
#from plotting_codes import *



class RTDIPlot(Operation):

    __isConfig = None
    __nsubplots = None

    WIDTHPROF = None
    HEIGHTPROF = None
    PREFIX = 'rtdi'
    WSCREEN_SPEC = 400
    HSCREEN_SPEC = 620
    ID_RTI=1

    def __init__(self):

        self.timerange = None
        self.isConfig = False
        self.__nsubplots = 1

        self.WIDTH = 800
        self.HEIGHT = 180
        self.WIDTHPROF = 120
        self.HEIGHTPROF = 0
        self.counter_imagwr = 0


        self.PLOT_CODE =3

        self.FTP_WEI = None
        self.EXP_CODE = None
        self.SUB_EXP_CODE = None
        self.PLOT_POS = None
        self.tmin = None
        self.tmax = None

        self.xmin = None
        self.xmax = None

        self.figfile = None
        #######################
        self.NRANGE=1000
        self.dr=1.5
        self.dt=20/3600.
        self.rango=range(self.NRANGE)
        for i in range(self.NRANGE):
            self.rango[i]=float(i*self.dr)
##########PLOTEO####################
        self.start=0
        self.stop=24
        self.x=range(4)
        self.y=range(4)

        self.RTDIMatrix=numpy.empty((1440,1000,3))
        ###plplot.plinit(26)#####LINEA COMENTADA

        plplot.plscolbg(255,255,255)
        #set background for imshow Method


        #plt.set_cmap('seismic')
        #plplot.plsetopt("geometry","1024x768")
        #plplot.plstart("?",1,1)
        #plplot.plsfnam("ALEX_TEST.jpeg")
        #plplot.plsdev("jpeg")
        #plplot.plinit() # nueva linea
        #plplot.plstart("",1,1)
        #plplot.plfontld(1);#JM: solo para poder escribir caracteres.
        #plplot.plfont(2)
        #plplot.plscol0(15,0,0,0) # JM : para setear el colorbar
        #plplot.plcol0(15)
        #plplot.pladv(1); #The screen is cleared (or a new piece of paper loaded)
        # #################################################
        #plplot.plschr(0,0.7)
        """ #The routine plprec is used to set the number of decimal places precision for axis labels, while
        plschr modifies the heights of characters used for the axis and graph labels
        """
        #plplot.plsmaj(0,1.0)
        """
        #The lengths of major and minor ticks on the axes are set up by the routines plsmaj and plsmin.
        """
        #plplot.plvpor(0.15,0.85,0.25,0.85)
        """
        For greater control over the size of the plots, axis labeling and tick intervals, more complex graphs
        should make use of the functions plvpor, plvasp, plvpas, plwind, plbox, and routines for manipulating
        axis labeling plgxax through plszax.
        """
        #plplot.plwind(self.start,self.stop,self.rango[0],self.rango[self.NRANGE-1])
        """
        The window must be defined after the viewport in order to map the world coordinate rectangle into the
        viewport rectangle. The routine plwind is used to specify the rectangle in world-coordinate space.
        """
        #plplot.plbox("bcinst",0.0,0,"bcinst",0.0,0)
        """
        The routine plbox is used to specify whether a frame is drawn around the viewport and to control the
        positions of the axis subdivisions and numeric labels. For our simple graph of the transistor characteristics,
        we may wish to draw a frame consisting of lines on all four sides of the viewport, and to place
        numeric labels along the bottom and left hand side. We can also tell PLplot to choose a suitable tick
        interval and the number of subticks between the major divisions based upon the data range specified to
        plwind. This is done using the following statement
                                                            plbox("bcnst", 0.0, 0, "bcnstv", 0.0, 0);
        """
        self.x[0]=self.x[3]=self.start
        self.x[1]=self.x[2]=self.stop
        # ##################################################
        self.y[0]=self.y[1]=self.rango[0]
        self.y[2]=self.y[3]=self.rango[self.NRANGE-1]
        #plplot.plpsty(0)
        #plplot.plfill(self.x,self.y)
        self.c_rgb=0

        #self.setDriver(plplotdriver)


    def saveFigure(self,figpath,figfile):
        filename = os.path.join(figpath, figfile)

        fullpath = os.path.split(filename)[0]

        if not os.path.exists(fullpath):
            subpath = os.path.split(fullpath)[0]

            if not os.path.exists(subpath):
                os.mkdir(subpath)

            os.mkdir(fullpath)
        os.system('cp %s %s'%('/home/hfuser/workspace_HF/schainroot/source/schainpy/test/ALEX_TEST.jpeg',filename))

    def getFilename(self, name, ext='.png'):

        path = '%s%03d' %(self.PREFIX, self.id)
        filename = '%s_%s%s' %(self.PREFIX, name, ext)
        return os.path.join(path, filename)

    def getNameToFtp(self, thisDatetime, FTP_WEI, EXP_CODE, SUB_EXP_CODE, PLOT_CODE, PLOT_POS,ext='.png'):
        YEAR_STR = '%4.4d'%thisDatetime.timetuple().tm_year
        DOY_STR = '%3.3d'%thisDatetime.timetuple().tm_yday
        FTP_WEI = '%2.2d'%FTP_WEI
        EXP_CODE = '%3.3d'%EXP_CODE
        SUB_EXP_CODE = '%2.2d'%SUB_EXP_CODE
        PLOT_CODE = '%2.2d'%PLOT_CODE
        PLOT_POS = '%2.2d'%PLOT_POS
        name = YEAR_STR + DOY_STR + FTP_WEI + EXP_CODE + SUB_EXP_CODE + PLOT_CODE + PLOT_POS+ ext
        return name

    def getNameToStandard(self, thisDatetime, c_station_o,c_web,c_freq,c_cod_Tx,c_ch,ext='.png'):
        YEAR_STR = '%4.4d'%thisDatetime.timetuple().tm_year
        DOY_STR = '%3.3d'%thisDatetime.timetuple().tm_yday
        c_Station_o = c_station_o
        c_web=c_web
        c_freq = c_freq
        c_cod_tx = c_cod_Tx
        c_ch = c_ch

        name = YEAR_STR + DOY_STR +c_station_o+c_web+c_freq+c_cod_Tx+c_ch+ext

        return name


    def run(self, dataOut, id, wintitle="", channelList=None, showprofile='True',
            xmin=None, xmax=None, ymin=None, ymax=None, zmin=None, zmax=None,
            timerange=None,
            save=False, figpath='./', lastone=0,figfile=None, ftp=False, wr_period=1, show=True,
            server=None, folder=None, username=None, password=None,
            ftp_wei=0, exp_code=0, sub_exp_code=0, plot_pos=0,ext='.jpeg',data_time_save=False,standard=False, c_station_o=None,c_web=None,c_freq=None,c_cod_Tx=None,c_ch=None):

        """

        Input:
            dataOut         :
            id        :
            wintitle        :
            channelList     :
            showProfile     :
            xmin            :    None,
            xmax            :    None,
            ymin            :    None,
            ymax            :    None,
            zmin            :    None,
            zmax            :    None
        """

        ##############LINEA PARA OBTENER DOPPLER PARAMETER
        #data_param = getattr(dataOut, parameterObject)
        self.standard= standard
        self.c_station_o= c_station_o
        self.c_web= c_web
        self.c_freq= c_freq
        self.c_cod_Tx= c_cod_Tx
        self.c_ch= c_ch

        #print "inicio"
        thisDatetime = datetime.datetime.utcfromtimestamp(dataOut.getTimeRange()[1])
        RGB=dataOut.data_img_snr
        time_hour=dataOut.data_time_genaro
        rango_layer=dataOut.data_img_genaro
        r2=dataOut.data_img_snr.shape[0]-1 # = 999 o 1000
        self.c_rgb=self.c_rgb+1

        self.FTP_WEI = ftp_wei
        self.EXP_CODE = exp_code
        self.SUB_EXP_CODE = sub_exp_code
        self.PLOT_POS = plot_pos
        self.figfile=figfile
        self.standard = standard
        self.data_time_save=data_time_save
        self.id =id
        #print "veamos",dataOut.last_block
        print self.c_rgb
        for i in range(r2):

            ir=max(min(int(RGB[i][0]*255),255),0)
            ig=max(min(int(RGB[i][1]*255),255),0)
            ib=max(min(int(RGB[i][2]*255),255),0)

            self.y[0]=self.y[1]=self.rango[i]
            self.y[2]=self.y[3]=self.rango[i+1]
            self.x[0]=self.x[3]=time_hour
            self.x[1]=self.x[2]=time_hour+6*self.dt
            #print id
            if (ir+ig+ib)>0:
                print ig
                #RTDIMatrix[i,self.c_rgb,:] = (ir,ig,ib)
               #plplot.plscol0(4,ir,ig,ib)
               #plplot.plcol0(4)
               #plplot.plfill(self.x,self.y)
           #plplot.plcol0(4)

        """
        Area fills are done in the currently selected color, line style, line width and pattern style.
        plfill fills a polygon. The polygon consists of n vertices which define the polygon.
        plfill (n , x , y );
        n (PLINT, input)
        The number of vertices.
        x, y (PLFLT *, input)
        Pointers to arrays with coordinates of the n vertices.

        Color map0 is most suited to coloring the background, axes, lines, and labels. Generally, the default color
        map0 palette of 16 colors is used. (examples/c/x02c.c illustrates these colors.) The default background
        color is taken from the index 0 color which is black by default. The default foreground color is red.
        There are a number of options for changing the default red on black colors. The user may set the index
        0 background color using the command-line bg parameter or by calling plscolbg (or plscol0 with a 0
        index) before plinit. During the course of the plot, the user can change the foreground color as often as
        desired using plcol0 to select the index of the desired color.

        During the course of the plot, the user can change the foreground color as often as
        desired using plcol0 to select the index of the desired color
        """
        #plplot.plssym(3.0,1.0)
        """
        The routine plssym sets up the size of all subsequent symbols drawn by calls to plpoin and plsym. It
        operates analogously to plschr as described above.
        """
        #plplot.plcol0(7)##red
        self.x[0]=time_hour
        self.y[0]=rango_layer
        #plplot.plsym(self.x,self.y,900)
        #plplot.plcol0(15)
        """
        During the course of the plot, the user can change the foreground color as often as
        desired using plcol0 to select the index of the desired color
        """
        #plt.figure()
        #plt.imshow(RTDIMatrix.astype(numpy.uint8))
        #plt.show()
        #print dataOut.last_block
        if self.c_rgb == dataOut.last_block:##automatizar este parametro1439#dataOut_lasblock ya no existe porque no guardo pdata
            #plplot.pllab("Local Time (hr)","Range(km.)",str(dataOut.datatime.date())+" "+str(dataOut.datatime.hour)+":"+str(dataOut.datatime.minute)+":"+str(dataOut.datatime.second))
            #plplot.plend()

            if self.figfile == None:
                str_datetime = thisDatetime.strftime("%Y%m%d_%H%M%S")
                self.figfile = self.getFilename(name = str_datetime,ext=ext)

            if figpath != '':
                if self.data_time_save:
                    str_doy=thisDatetime.strftime("%Y%j")
                    figpath=figpath+"/d%s"%str_doy


            self.saveFigure(figpath=figpath, figfile=self.figfile)
            filename = os.path.join(figpath, self.figfile)
            #name = self.getNameToFtp(thisDatetime, self.FTP_WEI, self.EXP_CODE, self.SUB_EXP_CODE, self.PLOT_CODE, self.PLOT_POS,ext=ext)
            #ftp_filename = os.path.join(figpath, name)
            #self.saveFigure(filename, ftp_filename)
            if self.standard ==True:
                name = self.getNameToStandard(thisDatetime,self.c_station_o,self.c_web,self.c_freq,self.c_cod_Tx,self.c_ch,ext=ext)
                Standard_filename = os.path.join(figpath, name)
                self.saveFigure(filename, Standard_filename)
