"""
Unit tests for the neurotools.parameters module

Also see the doctests in doc/parameters.txt
"""

import neurotools.parameters
from neurotools.random import GammaDist, UniformDist, NormalDist, ParameterDist
import os
import sys
import unittest
import types
from copy import deepcopy
import pickle

import neurotools.parameters.validators 
from neurotools.parameters.validators import congruent_dicts 
from neurotools.parameters import *

import yaml

#class DependenciesTest(unittest.TestCase):
#    """
#    Uncomment this class and comment-out "from neurotools.parameters import *"
#    above to run this test."""
#    
#    def setUp(self):
#        self.orig_path = sys.path[:]
#        for path in sys.path:
#            if 'scipy' in path:
#                sys.path.remove(path)
#        
#    def tearDown(self):
#        sys.path = self.orig_path[:]
#
#    def test_with_empty_path(self):
#        import neurotools.parameters
#        self.assertFalse(neurotools.parameters.have_scipy)

ps = ParameterSet({'a':1, 'b':2}, label="PS1")
ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
ps3 = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                    'true': False, 'mylist': [1,2,3,4],
                    'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                    }, label="PS3")

schema3 = ParameterSchema({'mylist': neurotools.parameters.validators.Subclass(type=list), 
                           'true': neurotools.parameters.validators.Subclass(type=bool), 
                           'yourlist': neurotools.parameters.validators.Subclass(type=list), 
                           'ps2': {'ps': {'a':neurotools.parameters.validators.Subclass(type=int),
                                          'b':neurotools.parameters.validators.Subclass(type=int)},
                                   'c': neurotools.parameters.validators.Subclass(type=int)}, 
                           'null': neurotools.parameters.validators.Subclass(type=type(None)),
                           'mydict': {'c': neurotools.parameters.validators.Subclass(type=int),
                                      'd': neurotools.parameters.validators.Subclass(type=int)},
                           'hello': neurotools.parameters.validators.Subclass(type=str)})


class ParameterSchemeTest(unittest.TestCase):
    
    def test_simple_create(self):
        s1 = ParameterSchema({'age': 0, 'height': Subclass(float)})
        # is equivalent to 
        s2 = ParameterSchema({'age': Subclass(int), 'height': Subclass(float)})

        
        assert s1 == s2


    def test_validate_generated_schema(self):
        s1 = ParameterSchema(ps3)

        v = CongruencyValidator()
        assert v.validate(ps3,s1)==True

    def test_eval(self):

        s1 = ParameterSchema(ps3)

        v = CongruencyValidator()
        # test Eval which checks for isinstance(x,list)
        s1.mylist = neurotools.parameters.validators.Eval('isinstance(x,list)',var='x')
        assert v.validate(ps3,s1)==True

        # test default var 'leaf'
        s1.hello = neurotools.parameters.validators.Eval('isinstance(leaf,str)')
        assert v.validate(ps3,s1)==True

        # test failure and var as non-kwarg
        s1.mylist = neurotools.parameters.validators.Eval('isinstance(x,str)','x')

        r = False
        try:
            r = v.validate(ps3,s1)
        except Exception as e:
            assert isinstance(e,ValidationError)
            assert e.path=='mylist'
            assert e.parameter==ps3.mylist
            assert e.schema_base==s1.mylist
        assert r == False

    def test_complex_eval(self):

        p_str = """
        list: [1,2,3,4]
        flist: [1.0,2.0,3.0,4.0]
        """

        s_str = """
        list: !!python/object:neurotools.parameters.validators.Eval { expr: 'isinstance(x,list) and all([isinstance(elem,int) for elem in x])', var: 'x'}
        flist: !!python/object:neurotools.parameters.validators.Eval { expr: 'isinstance(x,list) and all([isinstance(elem,float) for elem in x])', var: 'x'}
        """
        
        
        s1 = ParameterSchema(yaml.load(s_str))
        p1 = ParameterSet(yaml.load(p_str))

        v = CongruencyValidator()
        # test Eval which checks for isinstance(x,list)
        #s1.mylist = neurotools.parameters.validators.Eval('isinstance(x,list) and all([isinstance(elem,int) for elem in x])',var='x')
        assert v.validate(p1,s1)==True



    def test_simple_validate(self):
        v = CongruencyValidator()
        assert v.validate(ps3,schema3)==True

    def test_validation_failure_info(self):
        """ Test the error output for an failed validation against a schema"""

        s1 = ParameterSchema(ps3)
        
        s1.ps2.ps.a = Subclass(type=float)
        v = CongruencyValidator()
        r = False
        try:
            r = v.validate(ps3,s1)
        except Exception as e:
            assert isinstance(e,ValidationError)
            assert e.path=='ps2.ps.a'
            assert e.parameter==ps3.ps2.ps.a
            assert e.schema_base==s1.ps2.ps.a
        assert r == False


    def test_yaml_schema(self):
        import yaml

        conf1_str = """
        # user info
        username: joe
        email:  joe@example.com

        # recipes
        recipes:
           all: /somewhere1/path1.xml
           specific: /somewhere2/path2.xml
        numbers:
           float: 1.0
        """

        schema_str = """
        # user info
        username: ''
        email:  ''

        # recipes
        recipes:
           all: ''
           specific: ''
        numbers:
           float: !!python/object:neurotools.parameters.validators.Subclass { type: !!python/name:float }
        """

        schema = ParameterSchema(yaml.load(schema_str))
        conf = ParameterSet(yaml.load(conf1_str))

        v = CongruencyValidator()
        assert v.validate(conf,schema)

        del conf.recipes['all']
        r = False
        try:
            r = v.validate(conf,schema)
        except Exception as e:
            assert isinstance(e,ValidationError)
            assert e.path=='recipes.all'
            assert e.parameter=='<MISSING>'
            assert e.schema_base==schema.recipes.all

        assert r == False


    def test_yaml_file_schema(self):
        import yaml, tempfile

        conf1_str = """
        # user info
        username: joe
        email:  joe@example.com

        # recipes
        recipes:
           all: /somewhere1/path1.xml
           specific: /somewhere2/path2.xml
        numbers:
           float: 1.0
        """

        schema_str = """
        # user info
        username: ''
        email: ''

        # recipes
        recipes:
           all: ''
           specific: ''
        numbers:
           float: !!python/object:neurotools.parameters.validators.Subclass { type: !!python/name:float }
        """

        def write_to_yaml_tf(s):
            tf = tempfile.NamedTemporaryFile(suffix='.yaml')
            tf.writelines(s)
            tf.flush()
            tf.seek(0)
            return tf

        schema_tf = write_to_yaml_tf(schema_str)
        conf1_tf = write_to_yaml_tf(conf1_str)

        with schema_tf:
            with conf1_tf:

                schema = ParameterSchema(schema_tf.name)
                conf = ParameterSet(conf1_tf.name)

                v = CongruencyValidator()
                assert v.validate(conf,schema)

                del conf.recipes['all']
                r = False
                try:
                    r = v.validate(conf,schema)
                except Exception as e:
                    assert isinstance(e,ValidationError)
                    assert e.path=='recipes.all'
                    assert e.parameter=='<MISSING>'
                    assert e.schema_base==schema.recipes.all

                assert r == False


    def test_congruent_dicts(self):
        assert congruent_dicts({},{})
        assert congruent_dicts(None,1)
        assert congruent_dicts({},{'hello':10})==False
        assert congruent_dicts({'hello':False},{'hello':10})
        assert congruent_dicts({'hello':{'a':False}},{'hello':{'a':10}})
        assert congruent_dicts({'hello':{'a':False}},{'hello':{'b':10}})==False

        conf1_str = """
        # user info
        username: joe
        email:  joe@example.com

        # executables
        builder_path: /bgscratch/bbp/bin/sgi/
        detector_path: /bgscratch/bbp/bin/sgi/

        # recipes
        recipes:
           all: /somewhere/builderRecipeAllPathways.xml
           specific: /somewhere/builderRecipeSpecificPathways.xml
        """

        conf2_str = """
        # user info
        username: null
        email:  null

        # executables
        builder_path: null
        detector_path: null

        # recipes
        recipes:
           all: null
           specific: null
        """

        conf3_str = """

        # executables
        builder_path: null
        detector_path: null

        # recipes
        recipes:
           all: null
        """

        conf1 = yaml.load(conf1_str)
        conf2 = yaml.load(conf2_str)
        conf3 = yaml.load(conf3_str)

        assert congruent_dicts(conf1,conf2)
        # conf3 is subset of conf1 heirarchy, should return false
        assert congruent_dicts(conf1,conf3)==False

        # check subset==True
        assert congruent_dicts(conf1,conf3,subset=True)

        # check that additional field not in conf1 returns False
        conf3['recipes']['something'] = 1

        assert congruent_dicts(conf1,conf3,subset=True)==False
    



if __name__ == '__main__':
    unittest.main()
