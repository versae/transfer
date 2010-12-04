'''
Copyright (c) 2010 Lee Seongjoo

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

USAGE:
img_path = path of the image in the file system in string format 
gf = GaborFilter(img_path) 
gb = gf.gabor2DFunction(frequency=6, rotation=4)
'''

import numpy as np
from numpy import cos, sin, pi
import scipy.stsci.convolve as convolve
from scipy import signal
from ImageUtils import utils
#from psyco.classes import __metaclass__


class GaborFilter(object):
    '''
    GaborFilter
    '''

    def __init__(self, image):
        '''
        Constructor
        '''
        self.image = utils.im2array(image) 
        
    def gabor2DFunction(self, frequency, rotation, gamma=1, etha=1):
        '''
        Implementation of normalized 2-D Gabor filter function
        defined by Kyrki V, 2002
        '''
        fmax = 1 / 14.0
        a = 0.5
        flist = [(a ** k) * fmax for k in xrange(frequency)]        
        thetalist = [2 * pi * angle / rotation for angle in xrange(rotation)]
        
        set = [(f, theta) for f in flist for theta in thetalist] 
        xy_index = np.transpose(np.nonzero(self.image)) # Get x,y index of image
        
        # Image coordinates are centered to origin
        x = xy_index[:, 0]
        x = x - (max(x)+min(x))/2
        y = xy_index[:, 1]
        y = y - (max(y)+min(y))/2
                
        # Get Gabor function for all frequencies and rotations
        # then superpositioning for all rotations
        gb = 0
        for f, theta in set:        
            x_new = x * cos(theta) + y * sin(theta)
            x_new = np.ceil(x_new)         
            
            y_new = -1 * x * sin(theta) + y * cos(theta)
            y_new = np.ceil(y_new)        
            
            N = float(f ** 2) / float(pi * gamma * etha)
            term2d = -1 * f ** 2 * (x_new ** 2 / gamma ** 2 + y_new ** 2 / etha ** 2)
            gb += N * np.exp(term2d) * np.exp((2 * pi * f * x_new) * 1j)
        
        return gb
    
    def response(self, frequency, rotation, gamma=1, etha=1):
        gb = self.gabor2DFunction(frequency, rotation, gamma, etha) 
        gb = gb.reshape(self.image.shape)
        # Get magnitude of Gabor function?
#        gb_magnitude = np.abs(gb)                
        response = convolve.convolve2d(self.image, gb.real)        
        return response

    def outputImage(self, response):
        output, imOutput = utils.formatimage(response)  
        return [output, imOutput]      
        
    def gaborwavelet(self, img):
        '''
        Gabor wavelet (GW) filter
        (Is this working?) 
        '''
        imArray = utils.im2array(img)
        
        row_size, col_size = imArray.shape
        x = np.array(range(1, row_size + 1), dtype='float')
        x = x.reshape((row_size, 1))
        y = np.array(range(1, col_size + 1), dtype='float')
        y = y.reshape((1, col_size))
    
        orientations = []
        for i in range(8):
            orientations.append(i * pi / 8)
    
        w = signal.freqz()# spatial frequency
        G = np.exp(-(x ** 2 + y ** 2) / (2 * imArray.std()**2))
        GList = [] # image edge container for different directions
        for theta in orientations:
            wave_vector = x * np.cos(theta) + y * np.sin(theta)
            G *= np.cos(w * wave_vector) + 1j * np.sin(w * wave_vector)
        
            # Apply Gabor filter to image    
            sigma = convolve.convolve2d(imArray, G)
            GList.append(sigma)
            # Get the imaginary part of GW
    
        # format the output image    
        sigma, output_image = utils.formatimage(sigma)
        return output_image
        
