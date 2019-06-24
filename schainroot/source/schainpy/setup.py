'''
Created on Jul 16, 2014
@author: Miguel Urco
Modified by Alejandro: Added cDetectSpectrum extension

Commands :
python setup.py build
python setup.py install
'''

from setuptools import setup, Extension

setup(name="schainpy",
	version='2.2.9',
	description="test for noise improvement",
	author="Alejandro Castro",
	ext_modules=[Extension("cSchainNoise", ["extensions.c"]),
	Extension("cDetectSpectrum", ["detectSpectrum.cpp"])]
)
