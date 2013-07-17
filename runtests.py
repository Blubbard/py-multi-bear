#!/usr/bin/python

import sys, os
import traceback
import math
import time
import threading
import random
#import enjin.test.test_enjin
from enjin.test.test_enjin import *

try:
    unittest.main()
except Exception, e:
    tb = sys.exc_info()[2]
    traceback.print_exception(e.__class__, e, tb)
        
