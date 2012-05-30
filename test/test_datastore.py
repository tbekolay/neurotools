"""
Unit tests for the NeuroTools.datastore module

"""

import unittest
import os
import shutil
from NeuroTools.datastore import *
from NeuroTools.parameters import ParameterSet

class DummyComponent(object):
    
    def __init__(self, input=None):
        self.parameters = ParameterSet({'a': 1, 'b': 2})
        self.parameters._url = "http://www.example.com/parameters"
        self.version = 0.1
        self.input = input
        self.data = range(1000)

class ShelveDataStoreTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        if os.path.exists('/tmp/test_datastore'):
            shutil.rmtree("/tmp/test_datastore")
    
    def test_create_with_existing_rootdir(self):
        ds = ShelveDataStore('/tmp')
        assert os.path.exists(ds._root_dir)
        
    def test_create_with_non_existing_rootdir(self):
        assert not os.path.exists('/tmp/test_datastore')
        ds = ShelveDataStore('/tmp/test_datastore')
        assert os.path.exists(ds._root_dir)
        
    def test_store_retrieve(self):
        ds = ShelveDataStore('/tmp')
        c = DummyComponent()
        ds.store(c, 'data', c.data)
        new_data = ds.retrieve(c, 'data')
        self.assertEqual(c.data, new_data)
        
    def test_with_really_long_key(self):
        ds = ShelveDataStore('/tmp')
        c = DummyComponent()
        c.parameters._url = 'http://www.example.com/liurfsnlieugcns9g8cy4h43icpw349chgwp938gn93gcw398cgnw398gc39qcgwccg3o87cgnq48w37qgcf478gf249gvpn9347gfnc9w58gn954wgv7nwp937gvn9w34gv7nw3579gntvw9p35gntvw59pgvn5937gc5gdnergfdnw3497fgn547gcfw7np349gvnp5947cgn9ericneirscfgserciwrugniwerugnciwergcwnregc'
        self.assertRaises(Exception, ds.store, c, 'data', c.data)

    def test_hash_pickle(self):
        ds = ShelveDataStore('/tmp', keygenerators.hash_pickle)
        c = DummyComponent()
        ds.store(c, 'data', c.data)
        new_data = ds.retrieve(c, 'data')
        self.assertEqual(c.data, new_data)
        
    def test_with_component_chain(self):
        ds_jwu = ShelveDataStore('/tmp', keygenerators.join_with_underscores)
        ds_hp = ShelveDataStore('/tmp', keygenerators.hash_pickle)
        c1 = DummyComponent()
        c2 = DummyComponent(input=c1)
        for ds in ds_jwu, ds_hp:
            ds.store(c2, 'data', c2.data)
            new_data = ds.retrieve(c2, 'data')
            self.assertEqual(c2.data, new_data)
        
        
class DjangoORMDataStoreTest(unittest.TestCase):
        
    def setUp(self):
        self.ds = DjangoORMDataStore(database_parameters={'DATABASE_ENGINE': 'sqlite3',
                                                          'DATABASE_NAME': '/tmp/test_datastore.db'},
                                     data_root_dir='/tmp/test_datastore_django') 
    
    def tearDown(self):
        if os.path.exists('/tmp/test_datastore.db'):
            os.remove('/tmp/test_datastore.db')
        if os.path.exists('/tmp/test_datastore_django'):
            shutil.rmtree('/tmp/test_datastore_django')
        
    #def test_create(self):
    #    pass
    
    def test_store_retrieve(self):
        c = DummyComponent()
        self.ds.store(c, 'data', c.data)
        new_data = self.ds.retrieve(c, 'data')
        self.assertEqual(c.data, new_data)
    
        
if __name__ == '__main__':
    unittest.main()