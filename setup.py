from ez_setup import use_setuptools
use_setuptools()
from setuptools import setup, find_packages

setup(name='HDC100x',
      version='1.0.0',
      author='Scanner Luce',
      author_email='scanner@apricot.com',
      description=('Library for accessing the HDC100x series humidty and '
                   'temperature sensors like the HDC1000/HDC1008 on a '
                   'Raspberry Pi or Beaglebone Black.'),
      license='MIT',
      url='https://github.com/scanner/HDC100X_Python/',
      dependency_links=['https://github.com/adafruit/Adafruit_Python_GPIO/tarball/master#egg=Adafruit-GPIO-0.6.5'],
      install_requires=['Adafruit-GPIO>=0.6.5'],
      packages=find_packages())
