#!/usr/bin/env python
#
# File: $Id$
#
"""
Simple test our HDC1000 class
"""

# system imports
#
import time

# 3rd party imports
#
from HDC100x import HDC100x


#############################################################################
#
def main():
    """
    Initialize the device.. dry it.. and then consecutively read data from it.
    """
    hdc = HDC100x()
    temp, humid = hdc.data()
    print "Temp: {}, humidity: {}".format(temp, humid)
    hdc.dry_sensor()
    while True:
        temp, humid = hdc.data()
        print "Temp: {}, humidity: {}".format(temp, humid)
        time.sleep(5)

############################################################################
############################################################################
#
# Here is where it all starts
#
if __name__ == '__main__':
    main()
#
############################################################################
############################################################################
