import numpy
cimport numpy
 
def decoder(numpy.ndarray[numpy.complex_t, ndim=2] fft_code, numpy.ndarray[numpy.complex_t, ndim=2] data):

    fft_data = numpy.fft.fft(data, axis=1)
    conv = fft_data*fft_code
    data = numpy.fft.ifft(conv, axis=1)
    
    return data