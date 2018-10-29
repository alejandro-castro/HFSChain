import numpy

def hildebrand_sekhon(data, navg):
    """
    This method is for the objective determination of de noise level in Doppler spectra. This 
    implementation technique is based on the fact that the standard deviation of the spectral 
    densities is equal to the mean spectral density for white Gaussian noise
    
    Inputs:
        Data    :    heights
        navg    :    numbers of averages
        
    Return:
        -1        :    any error
        anoise    :    noise's level
    """
    
    dataflat = data.reshape(-1)
    dataflat.sort()
    npts = dataflat.size #numbers of points of the data
    
    if npts < 32:
        print "error in noise - requires at least 32 points"
        return -1.0
    
    dataflat2 = numpy.power(dataflat,2)
    
    cs = numpy.cumsum(dataflat)
    cs2 = numpy.cumsum(dataflat2)
    
    # data sorted in ascending order
    nmin = int((npts + 7.)/8)
    
    for i in range(nmin, npts):
        s = cs[i]
        s2 = cs2[i]
        p  = s / float(i);
        p2 = p**2;
        q  = s2 / float(i) - p2;
        leftc = p2;
        rightc = q * float(navg);
        R2 = leftc/rightc
        
        # Signal detect: R2 < 1 (R2 = leftc/rightc)
        if R2 < 1: 
            npts_noise = i
            break
        
            
    anoise = numpy.average(dataflat[0:npts_noise])

    return anoise;

def sorting_bruce(Data, navg):
    sortdata = numpy.sort(Data)
    lenOfData = len(Data)
    nums_min = lenOfData/10
    
    if (lenOfData/10) > 0:
        nums_min = lenOfData/10
    else:
        nums_min = 0
        
    rtest = 1.0 + 1.0/navg
    
    sum = 0.
    
    sumq = 0.
    
    j = 0
    
    cont = 1
    
    while((cont==1)and(j<lenOfData)):
        
        sum += sortdata[j]
        
        sumq += sortdata[j]**2
        
        j += 1
        
        if j > nums_min:
            if ((sumq*j) <= (rtest*sum**2)):
                lnoise = sum / j
            else:
                j = j - 1
                sum  = sum - sordata[j]
                sumq =  sumq - sordata[j]**2
                cont = 0
                
        if j == nums_min:
            lnoise = sum /j
    
    return lnoise            

class Noise:
    """
    Clase que implementa los metodos necesarios para deternimar el nivel de ruido en un Spectro Doppler
    """
    data = None
    noise = None
    dim = None

    def __init__(self, data=None):
        """
        Inicializador de la clase Noise para la la determinacion del nivel de ruido en un Spectro Doppler.

        Inputs:
            data: Numpy array de la forma nChan x nHeis x nProfiles
            
        Affected:
            self.noise
        
        Return:
            None
        """
        
        self.data = data
        self.dim = None
        self.nChannels = None
        self.noise = None

    def setNoise(self, data):
        """
        Inicializador de la clase Noise para la la determinacion del nivel de ruido en un Spectro Doppler.

        Inputs:
            data: Numpy array de la forma nChan x nHeis x nProfiles
            
        Affected:
            self.noise
        
        Return:
            None
        """
        
        if data == None:
            raise ValueError, "The data value is not defined"
        
        shape = data.shape
        self.dim = len(shape)
        if self.dim == 3:
            nChan, nProfiles, nHeis = shape
        elif self.dim == 2:
            nChan, nHeis = shape
        else:
            raise ValueError, "" 
        
        self.nChannels = nChan
        self.data = data.copy()
        self.noise = numpy.zeros(nChan)
        
        return 1
            
        
    def byHildebrand(self, navg=1):
        """
        Determino el nivel de ruido usando el metodo Hildebrand-Sekhon
        
        Return:
            noiselevel
        """
        
        daux = None

        for channel in range(self.nChannels):
            daux = self.data[channel,:,:]
            self.noise[channel] = hildebrand_sekhon(daux, navg)
        return self.noise 
    
    def byWindow(self, heiIndexMin, heiIndexMax, freqIndexMin, freqIndexMax):
        """
        Determina el ruido del canal utilizando la ventana indicada con las coordenadas: 
        (heiIndexMIn, freqIndexMin) hasta (heiIndexMax, freqIndexMAx)
        
        Inputs:
            heiIndexMin: Limite inferior del eje de alturas
            heiIndexMax: Limite superior del eje de alturas
            freqIndexMin: Limite inferior del eje de frecuencia
            freqIndexMax: Limite supoerior del eje de frecuencia
        """
        
        data = self.data[:, heiIndexMin:heiIndexMax, freqIndexMin:freqIndexMax]
        
        for channel in range(self.nChannels):
            daux = data[channel,:,:]
            self.noise[channel] = numpy.average(daux)
        
        return self.noise
    
    def bySort(self,navg = 1):
        daux = None

        for channel in range(self.nChannels):
            daux = self.data[channel,:,:]
            self.noise[channel] = sorting_bruce(daux, navg)
            
        return self.noise 

        