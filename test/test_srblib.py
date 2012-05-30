"""
Unit tests for the NeuroTools.utilities.srblib module
"""

import sys
import unittest
import numpy
import os
import time
from NeuroTools.utilities import srblib

default_connection = srblib.get_MdasEnv()
default_server = default_connection.copy()
default_connection.pop('default_resource')
default_server['root'] = "/INRIA/home/INRIA"

# ==============================================================================
class FileSystemTest(unittest.TestCase):

    def setUp(self):
        self.filesystem = srblib.SRBFileSystem(**default_server)

    def test_ls(self):
        self.filesystem.cd("WP5")
        print self.filesystem.ls()

# ==============================================================================
class WriteReadTest(unittest.TestCase):
    """Write files and then read them again and check the contents match."""

    def setUp(self):
        self.connection = srblib.SRBConnection(**default_connection)
   
    def tearDown(self):
        pass # connection should automatically be closed on end of test    
    
    def writeread(self, n, filename):
        input_data = "\n".join(map(str, numpy.random.rand(n)))
        start_time = time.time()
        path = "/INRIA/home/INRIA/WP5"
        f = srblib.SRBFile(self.connection, "%s/%s" % (path, filename), default_server['default_resource'], mode='w')
        f.write(input_data)
        f.close()
        f = srblib.SRBFile(self.connection, "%s/%s" % (path, filename), default_server['default_resource'], mode='r')
        output_data = f.read()
        f.close()
        status = srblib.srb.obj_delete(self.connection.id, filename, 0, path)
        if status < 0:
            raise srblib.SRBFileError(path, filename, 'delete', status)
        print "time to write/read %d numbers = %g" % (n, time.time() - start_time)
        return input_data, output_data
    
    def testSmallFileSingleWrite(self):
        input_data, output_data = self.writeread(100, "testSmallFileSingleWrite.dat")
        self.assertEqual(input_data, output_data)
    
    def testLargeFileSingleWrite(self):
        input_data, output_data = self.writeread(100000, "testLargeFileSingleWrite.dat")
        self.assertEqual(input_data, output_data)


class URLTest(unittest.TestCase):
    
    def setUp(self):
        self.content = "Mate, this bird wouldn't 'voom' if you put four million volts through it!\n"
        self.s = srblib.SRBFileSystem(**default_server)
        self.s.cd("WP5")
        f = self.s.open("urltestfile.dat", mode='w')
        f.write(self.content)
        f.close()
    
    def tearDown(self):
        filename = "urltestfile.dat"
        self.s.rm(filename)
    
    def test_urlopen(self):
        f = srblib.urlopen("srb://facets.inria.fr/INRIA/home/INRIA/WP5/urltestfile.dat")
        txt = f.read()
        f.close()
        print txt
        self.assertEqual(txt, self.content)
        return False

# ==============================================================================    
if __name__ == "__main__":
    unittest.main()