"""
Unit tests for the neurotools.parameters module

Also see the doctests in doc/parameters.txt
"""

from neurotools.parameters import *
from neurotools.random import GammaDist, UniformDist, NormalDist, ParameterDist
import os
import sys
import unittest
import types
from copy import deepcopy
import pickle

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

import matplotlib
matplotlib.use('Agg')

class ParameterRangeTest(unittest.TestCase):
    
    def test_simple_create(self):
        pr = ParameterRange([1,3,5,7,9], units="mV", name="test")
        values = []
        for x in pr:
            values.append(x)
        self.assertEqual(values, [1,3,5,7,9])
        
    def test_shuffle_create(self):
        input_values = [1,3,5,7,9,11,13,15,17,19]
        pr = ParameterRange(input_values, units="mV", name="test", shuffle=True)
        values = []
        for x in pr:
            values.append(x)
        self.assertNotEqual(values, input_values) # will occasionally, by chance, fail
        self.assertEqual(set(values), set(input_values))
        
    def test_str_and_repr(self):
        pr = ParameterRange([1,3,5,7,9], units="mV", name="pr")
        self.assertEqual(repr(pr), 'ParameterRange([1, 3, 5, 7, 9], units="mV")')
        first_value = pr.next()
        self.assertEqual(str(first_value), '1')
        
    def test_invalid_create(self):
        self.assertRaises(TypeError, ParameterRange, 555, name="invalid")

class ParameterSetCreateTest(unittest.TestCase):

    def test_create_from_dict(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        ps3 = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")
        ps4 = ParameterSet(ps)
        ps5 = ParameterSet(ps, label="PS5")
        ps6 = ParameterSet(ps3)
        assert isinstance(ps3, ParameterSet)
        assert isinstance(ps3.ps2, ParameterSet)
        assert isinstance(ps3['ps2'].ps, ParameterSet)
        assert isinstance(ps3.ps2.ps.a, int)
        assert isinstance(ps3.mydict, ParameterSet)
        assert ps3.ps2.label == "PS2"
        assert ps3.mydict.label == 'mydict'
        assert isinstance(ps4, ParameterSet)
        assert ps4.label == ps.label, "%s != %s" % (ps4.label, ps.label)
        assert ps5.label == "PS5"
    
    def test_create_from_string(self):
        ps1 = ParameterSet("{'a': 1, 'b':2}")
        ps2 = ParameterSet({'a': 1, 'b':2})
        self.assertEqual(ps1, ps2)

    def test_create_from_flat_iterator(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        ps3 = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")
        ps4 = ParameterSet({})
        for x in ps3.flat():
            ps4.flat_add(x[0],x[1])
        self.assertEqual(ps4, ps3)

        
    def test_create_with_syntax_error(self):
        self.assertRaises(SyntaxError, ParameterSet, "{'a': 1, 'b':2")
        
    def test_create_with_NameError(self):
        self.assertRaises(NameError, ParameterSet, "{a: 1, b:2}")
        
    def test_create_with_invalid_initialiser(self):
        self.assertRaises(TypeError, ParameterSet, object)

    def test_create_yaml_url(self):
        import tempfile, yaml

        conf1_str = """
        # user info
        username: joe
        email:  joe@example.com

        # recipes
        recipes:
           all: /somewhere1/file1.xml
           specific: /somewhere2/file2.xml
        """

        ps = ParameterSet
        
        tf = tempfile.NamedTemporaryFile(suffix='.yaml')
        tf.file.writelines(conf1_str)
        
        tf.file.flush()
        tf.file.seek(0)

        ps = ParameterSet("file://"+tf.name)

        tf.close()

        ps1 = ParameterSet(yaml.load(conf1_str))
        assert ps1 == ps
        
        
        

    
class ParameterSetSaveLoadTest(unittest.TestCase):
    
    def setUp(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        self.ps = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")
    
    def tearDown(self):
        if os.path.exists('test.param'):
            os.remove('test.param')
    
    def test_save_and_load(self):
        my_url = "file://%s/test.param" % os.getcwd()
        self.ps.save(my_url)
        new_ps = ParameterSet(my_url)
        self.assertEqual(self.ps, new_ps)
        self.assertEqual(self.ps.ps2.ps.b, new_ps.ps2.ps.b)
        #self.assertEqual(self.ps.label, new_ps.label) # for now, labels are not preserved on saving

    def test_pickle(self):
        pkl = pickle.dumps(self.ps)
        new_ps = pickle.loads(pkl)
        self.assertEqual(self.ps, new_ps)
        self.assertEqual(self.ps.ps2.ps.b, new_ps.ps2.ps.b)
        #self.assertEqual(self.ps.label, new_ps.label) # or on pickling

class ParameterSetFlattenTest(unittest.TestCase):

    def setUp(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        self.ps = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")
        
    def test_flatten(self):
        assert isinstance(self.ps.flatten(), dict)
        self.assertEqual(self.ps.flatten(), {'null': None, 'mylist': [1, 2, 3, 4],
            'ps2.ps.b': 2, 'mydict.c': 3, 'mydict.d': 4, 'yourlist': [1, 2, {'e': 5, 'f': 6}],
            'ps2.c': 19, 'true': False, 'hello': 'world', 'ps2.ps.a': 1})
        
    def test_flat(self):
        self.assertEqual(types.GeneratorType, type(self.ps.flat()))
        D = {}
        for k,v in self.ps.flat():
            D[k] = v
        self.assertEqual(D, self.ps.flatten())

class ParameterSetMiscTest(unittest.TestCase):
    
    def setUp(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        self.ps = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")
        
    def test_as_dict(self):
        self.assertEqual(self.ps.as_dict(),
                         {'hello': 'world',
                          'ps2': {'ps':{'a':1, 'b':2}, 'c':19},
                          'null': None,
                          'true': False,
                          'mylist': [1,2,3,4],
                          'mydict': {'c': 3, 'd':4},
                          'yourlist': [1,2,{'e':5, 'f':6}],
                         })
    
    
class ParameterSetDiffTest(unittest.TestCase):
    
    def setUp(self):
        ps = ParameterSet({'a':1, 'b':2}, label="PS1")
        ps2 = ParameterSet({'ps':ps, 'c':19}, label="PS2")
        self.ps = ParameterSet({'hello': 'world', 'ps2': ps2, 'null': None,
                            'true': False, 'mylist': [1,2,3,4],
                            'mydict': {'c': 3, 'd':4}, 'yourlist': [1,2,{'e':5, 'f':6}],
                            }, label="PS3")

    def test_diff_self_is_zero(self):
        self.assertEqual(self.ps - self.ps, ({},{}))
        
    def test_diff_at_top_level(self):
        ps2 = ParameterSet(self.ps.as_dict())
        ps2.hello = 'universe'
        self.assertEqual(ps2 - self.ps, ({'hello': 'universe'},{'hello': 'world'}))
        self.assertEqual(self.ps - ps2, ({'hello': 'world'},{'hello': 'universe'}))

    def test_diff_as_bottom_level(self):
        ps2 = ParameterSet(self.ps.as_dict())
        ps2.ps2.ps.b = 3
        self.assertEqual(ps2 - self.ps, ({'ps2': {'ps': {'b': 3}}},
                                         {'ps2': {'ps': {'b': 2}}}))

    def test_diff_inside_list(self):
        ps2 = ParameterSet(self.ps.as_dict())
        ps2.yourlist = [100, 2, {'e': 55, 'f': 6}]
        self.assertEqual(ps2 - self.ps, ({'yourlist': [100, 2, {'e': 55, 'f': 6}]},
                                         {'yourlist': [1, 2, {'e': 5, 'f': 6}]}))


class ParameterSpaceDotAccess(unittest.TestCase):

    def setUp(self):
        ps7 = ParameterSpace({})
        ps7.name = ParameterSpace({})
        ps7.x = ParameterRange([1,2])
        self.yrange = [1.1,2.2]
        ps7.name.y = ParameterRange(self.yrange)
        ps7.foo = ParameterSet({})
       
        self.ps7 = ps7

    def test_valid_access(self):
        ps7 = self.ps7
        self.assertEqual(ps7.name.y, ps7['name.y'])
        ps7['foo.bar'] = 10.0
        assert ps7['foo'].bar == ps7.foo.bar == ps7.foo['bar']

    def test_invalid_access(self):
        # names cannot have a dot in them unless the name
        # before the dot is already defined.
        # Another functionality possibility would be to
        # automagically and implicitly do ps7.foo = ParameterSet({}) here
        # but that doesn't warn the user of typos.
        ps7 = self.ps7
        def f(k,v):
            ps7[k] = v
        self.assertRaises(KeyError, f, 'bar.foo', 10.0)
    
    
class ParameterSpaceIterationTest(unittest.TestCase):
    
    def setUp(self):
        ps7 = ParameterSpace({})
        ps7.name = ParameterSpace({})
        ps7.x = ParameterRange([1,2])
        self.yrange = [1.1,2.2]
        ps7.name.y = ParameterRange(self.yrange)
        ps7.foo = ParameterSet({})
        self.ps7 = ps7
        
    def test_iter_inner(self):
        ps7 = self.ps7
        assert [ x.name.y for x in ps7.iter_range_key('name.y')] == self.yrange
        out = [(1, 1.1000000000000001),(1, 2.2000000000000002),
               (2, 1.1000000000000001), (2, 2.2000000000000002)]
        out1 = [(1, 1.1000000000000001), (2, 1.1000000000000001),
                (1, 2.2000000000000002), (2, 2.2000000000000002)]
        out2 = [ (ps.x,ps.name.y) for ps in ps7.iter_inner()]
        assert out2 in (out,out1)

    def test_is_ref_by_default(self):
        # check that we're returning only many version of the same
        # object by default
        ps7 = self.ps7
        out = [x for x in ps7.iter_inner()]
        assert numpy.alltrue([x==out[0] for x in out])
    
    def test_returns_ParameterSet(self):
        ps7 = self.ps7
        out = [x for x in ps7.iter_inner()]
        assert isinstance(ps7, ParameterSpace)
        assert isinstance(out[0], ParameterSet)
        assert not isinstance(out[0], ParameterSpace), "%s %s %s" % (out[0].pretty(), out[0]._is_space(), type(out[0]))
    
    def test_copy(self):
        ps7 = self.ps7
        out = [x for x in ps7.iter_inner(copy=True)]
        # now check that there are no duplicate objects
        assert numpy.alltrue([out[x-1] not in out[x:] for x in range(1,len(out))])

    def test_tree_copy(self):
        ps7 = self.ps7
        ps8 = ps7.tree_copy()
        ps8.x._values[0] = 2
        self.assertEqual(ps8.x, ps7.x)

    def test_num_conditions(self):
        ps7 = self.ps7
        self.assertEqual(ps7.num_conditions(), 4)
        self.assertEqual(ps7.num_conditions(), len([x for x in ps7.iter_inner()]))

    def test_parameter_space_index(self):
        ps7 = self.ps7
        results_dim, results_label = ps7.parameter_space_dimension_labels()
        self.assertEqual(results_dim, [2,2])
        self.assertEqual(results_label, ['name.y', 'x'])
        indices = [ps7.parameter_space_index(experiment) for experiment in ps7.iter_inner()]
        self.assertEqual(indices, [(0,0), (0,1), (1,0), (1,1)])
        self.assertEqual(ps7.parameter_space_index(ParameterSet({'x': 2, 'foo': {}, 'name': {'y': 1.1}})), (0,1))
        self.assertRaises(ValueError, ps7.parameter_space_index, ParameterSet({'x': 3, 'foo': {}, 'name': {'y': 1.1}}))


class ParameterSpaceWithDistributionsTest(unittest.TestCase):
    
    def setUp(self):
        ps = ParameterSpace({})
        ps.g = GammaDist()
        ps.l = [NormalDist(), UniformDist(), 'a string']
        ps.d = ParameterSpace({'g2': UniformDist(),
                               'x': 0})
        self.ps = ps
        
    def test_dist_keys(self):
        self.assertEqual(set(self.ps.dist_keys()), set(['g', 'l', 'd.g2']))

    def test_realize_dists_with_copy_True(self):
        gen = self.ps.realize_dists(n=2, copy=True)
        assert type(gen) == types.GeneratorType
        output = list(gen)
        #for item in output:
        #    print item.pretty()
        self.assertEqual(len(output), 2)
        self.assertNotEqual(output[0].g, output[1].g)
        self.assertEqual(output[0].d.x, output[1].d.x)
        self.assertNotEqual(output[0].l[0], output[1].l[0])
        self.assertNotEqual(output[0].l[1], output[1].l[1])
        self.assertEqual(output[0].l[2], output[1].l[2])

    def test_realize_dists_with_copy_False(self):
        gen = self.ps.realize_dists(n=2, copy=False)
        assert type(gen) == types.GeneratorType
        output = []
        for item in gen:
            output.append(deepcopy(item))
        self.assertEqual(len(output), 2)
        self.assertNotEqual(output[0].g, output[1].g)
        self.assertEqual(output[0].d.x, output[1].d.x)
        self.assertNotEqual(output[0].l[0], output[1].l[0])
        self.assertNotEqual(output[0].l[1], output[1].l[1])
        self.assertEqual(output[0].l[2], output[1].l[2])


class ParameterSpaceSaveLoadTest(unittest.TestCase):
    
    def setUp(self):
        psp = ParameterSpace({})
        psp.g = GammaDist()
        psp.l = [NormalDist(), UniformDist(), 'a string']
        psp.d = ParameterSpace({'g2': UniformDist(),
                               'x': 0})
        psp.name = ParameterSpace({})
        psp.x = ParameterRange([1,2])
        self.yrange = [1.1,2.2]
        psp.name.y = ParameterRange(self.yrange)
        psp.foo = ParameterSet({})
        self.psp = psp
    
    def tearDown(self):
        if os.path.exists('test.param'):
            os.remove('test.param')
    
    def test_save_and_load(self):
        my_url = "file://%s/test.param" % os.getcwd()
        self.psp.save(my_url)
        new_psp = ParameterSpace(my_url)
        self.assertEqual(self.psp, new_psp)
        self.assertEqual(self.psp.g, new_psp.g)


#class ParameterSpaceWithBothRangesAndDists(unittest.TestCase):
#    
#    def setUp(self):
#        psp = ParameterSpace({})
#        psp.g = GammaDist()
#        psp.l = [NormalDist(), UniformDist(), 'a string']
#        psp.d = ParameterSpace({'g2': UniformDist(),
#                               'x': 0})
#        psp.name = ParameterSpace({})
#        psp.x = ParameterRange([1,2])
#        self.yrange = [1.1,2.2]
#        psp.name.y = ParameterRange(self.yrange)
#        psp.foo = ParameterSet({})
#        self.psp = psp
#
#    def test_iter_inner(self):
#        psp = self.psp
#        for pst in psp.iter_inner():
#            print pst.pretty()
        
        
class ParameterTableTest(unittest.TestCase):
    
    def test_create_from_string(self):
        pt = ParameterTable('''
            #       col1    col2    col3
            row1     1       2       3    
            row2     4       5       6
            row3     7       8       9
        ''')
        assert isinstance(pt, ParameterSet)
        self.assertEqual(pt.row2.col3, 6.0)
        self.assertEqual(pt.column('col1'), {'row1': 1.0, 'row2': 4.0, 'row3': 7.0})
        self.assertEqual(pt.row('row2'), {'col1': 4.0, 'col2': 5.0, 'col3': 6.0})
        self.assertEqual(pt.transpose().col3.row2, 6.0)
        
    def test_table_string(self):
        pt = ParameterTable('''
            #       col1    col2    col3
            row1     1       2       3    
            row2     4       5       6
            row3     7       8       9
        ''')
        ts = pt.table_string()
        self.assertEqual(pt, ParameterTable(ts))
        self.assertNotEqual(pt, ParameterTable(ts.replace('7', '8')))
        

if __name__ == '__main__':
    unittest.main()
