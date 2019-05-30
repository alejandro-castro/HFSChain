'''

Commands :

python setup.py build
python setup.py install



Created on Jul 16, 2014

@author: Miguel Urco
setup (name = 'PackageName',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
results :

running build
running build_ext
building 'cSchainNoise' extension
creating build
creating build/temp.linux-x86_64-2.7
x86_64-linux-gnu-gcc -pthread -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -fno-strict-aliasing -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -fPIC -I/usr/include/python2.7 -c extensions.c -o build/temp.linux-x86_64-2.7/extensions.o
In file included from /usr/include/python2.7/numpy/ndarraytypes.h:1777:0,
                 from /usr/include/python2.7/numpy/ndarrayobject.h:18,
                 from /usr/include/python2.7/numpy/arrayobject.h:4,
                 from extensions.c:2:
/usr/include/python2.7/numpy/npy_1_7_deprecated_api.h:15:2: warning: #warning "Using deprecated NumPy API, disable it by " "#defining NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION" [-Wcpp]
 #warning "Using deprecated NumPy API, disable it by " \
  ^
extensions.c:12:16: warning: function declaration isnt a prototype [-Wstrict-prototypes]
 PyMODINIT_FUNC initcSchain() {
                ^
creating build/lib.linux-x86_64-2.7
x86_64-linux-gnu-gcc -pthread -shared -Wl,-O1 -Wl,-Bsymbolic-functions -Wl,-Bsymbolic-functions -Wl,-z,relro -fno-strict-aliasing -DNDEBUG -g -fwrapv -O2 -Wall -Wstrict-prototypes -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security -Wl,-Bsymbolic-functions -Wl,-z,relro -Wdate-time -D_FORTIFY_SOURCE=2 -g -fstack-protector-strong -Wformat -Werror=format-security build/temp.linux-x86_64-2.7/extensions.o -o build/lib.linux-x86_64-2.7/cSchainNoise.so


running install
running bdist_egg
running egg_info
creating schainpy.egg-info
writing schainpy.egg-info/PKG-INFO
writing top-level names to schainpy.egg-info/top_level.txt
writing dependency_links to schainpy.egg-info/dependency_links.txt
writing manifest file 'schainpy.egg-info/SOURCES.txt'
reading manifest file 'schainpy.egg-info/SOURCES.txt'
writing manifest file 'schainpy.egg-info/SOURCES.txt'
installing library code to build/bdist.linux-x86_64/egg
running install_lib
running build_ext
creating build/bdist.linux-x86_64
creating build/bdist.linux-x86_64/egg
copying build/lib.linux-x86_64-2.7/cSchainNoise.so -> build/bdist.linux-x86_64/egg
creating stub loader for cSchainNoise.so
byte-compiling build/bdist.linux-x86_64/egg/cSchainNoise.py to cSchainNoise.pyc
creating build/bdist.linux-x86_64/egg/EGG-INFO
copying schainpy.egg-info/PKG-INFO -> build/bdist.linux-x86_64/egg/EGG-INFO
copying schainpy.egg-info/SOURCES.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying schainpy.egg-info/dependency_links.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
copying schainpy.egg-info/top_level.txt -> build/bdist.linux-x86_64/egg/EGG-INFO
writing build/bdist.linux-x86_64/egg/EGG-INFO/native_libs.txt
zip_safe flag not set; analyzing archive contents...
creating dist
creating 'dist/schainpy-2.2.9-py2.7-linux-x86_64.egg' and adding 'build/bdist.linux-x86_64/egg' to it
removing 'build/bdist.linux-x86_64/egg' (and everything under it)
Processing schainpy-2.2.9-py2.7-linux-x86_64.egg
Copying schainpy-2.2.9-py2.7-linux-x86_64.egg to /home/jm/virtuals/schainHF/lib/python2.7/site-packages
Removing schainpy 2.3 from easy-install.pth file
Adding schainpy 2.2.9 to easy-install.pth file

Installed /home/jm/virtuals/schainHF/lib/python2.7/site-packages/schainpy-2.2.9-py2.7-linux-x86_64.egg
Processing dependencies for schainpy==2.2.9
Finished processing dependencies for schainpy==2.2.9


'''

#from schainpy import __version__
from setuptools import setup, Extension

setup(name="schainpy",
	version='2.2.9',
	description="test for noise improvement",
	author="Alejandro Castro",
	ext_modules=[Extension("cSchainNoise", ["extensions.c"]),
	Extension("cDetectSpectrum", ["detectSpectrum.cpp"])]
)
