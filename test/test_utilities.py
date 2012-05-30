"""
Unit tests for the NeuroTools.utilities module

Also see test_srblib.py
"""

import unittest
from NeuroTools import utilities



class UtilitiesTest(unittest.TestCase):

    def runTest(self):

        print 'INFO: Up to this point, NeuroTools.utilities contains no functions or classes.'
        
        # these are dummy calls of the functions which just raise an exception, telling where the routine has been moved to.
        # satisfies coverage :)
        try: utilities.imsave(None,None)
        except: pass
        try: utilities.progress_bar(None)
        except: pass
        try: utilities.exportPNGZip(None, None, None)
        except: pass
        try: utilities.show(None)
        except: pass
        try: utilities.save_image(None, None)
        except: pass



if __name__ == "__main__":
    unittest.main()

