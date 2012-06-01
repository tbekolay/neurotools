"""
Tests for the optimize module. 

$Id: test_optimize.py 365 2008-12-23 21:47:50Z mschmucker $
"""
import unittest
from neurotools.optimize import optimizers

class TestGridSearcher(unittest.TestCase):
    """
    Test the GridSearcher.
    """
    def test_gridsearcher(self):
        def func(param_dict):
            x,y = param_dict['x'], param_dict['y']
            return x*x + y*y
        from neurotools.parameters import ParameterSpace, ParameterRange
        grid = ParameterSpace({'x':ParameterRange([-2., -1., 0., 1., 2.]),
                               'y':ParameterRange([-2., -1., 0., 1., 2.])})
        gs = optimizers.GridSearcher(grid, func)    
        retdict = gs.search()
        self.failUnlessEqual(retdict['min_value'], 0.)
        self.failUnlessEqual(retdict['min_params'], {'x':0., 'y':0.})


#from neurotools.optimize.parameter_search import *
#
#class TestParameterSearch(unittest.TestCase):
#    """
#    Parent class for parameter search, defining functions to be available in all
#    paramter search tests.
#    """
#    def parametersearch(self, searcher, **kwargs):
#        def func(param = None):
#            """
#            just return the input argument.
#            """
#            return param
#        dict_iterable = [{'lala':1, 'lulu':2},
#                    {'lala':3, 'lulu':4},
#                    {'lala':5, 'lulu':6}]
#        ps = searcher(dict_iterable = dict_iterable, func = func, **kwargs)
#        ps.search()
#        result = ps.harvest()
#        return (dict_iterable,result)
#
#class TestPlainParameterSearcher(TestParameterSearch):
#    def test_ParameterSearcher(self):
#        (dict_iterable, result) = self.parametersearch(ParameterSearcher)
#        self.assertEqual(dict_iterable, result)
#
#    def test_ParameterSearcher_harvestException(self):
#        ps = ParameterSearcher()
#        self.failUnlessRaises(Exception, ps.harvest)
#
#class TestIPythonUtilities(unittest.TestCase):
#    """
#    Test the utility functions provided by the parameter searcher.
#    """
#    def test_make_controller(self):
#        contr_dict = IPythonParameterSearcher.make_controller()
#        pobj = contr_dict['contr_obj']
#        controller_returned = pobj.poll()
#        from os.path import exists
#        task_furl_exists = exists(contr_dict['task_furl'])
#        multiengine_furl_exists = exists(contr_dict['multiengine_furl'])
#        engine_furl_exists = exists(contr_dict['engine_furl'])
#
#        # clean up: kill controller and remove furl files
#        import os, signal
#        os.kill(pobj.pid, signal.SIGINT)
#        pobj.wait()
#        if task_furl_exists:
#            os.remove(contr_dict['task_furl'])
#        if multiengine_furl_exists:
#            os.remove(contr_dict['multiengine_furl'])
#        if engine_furl_exists:
#            os.remove(contr_dict['engine_furl'])
#
#        self.failUnless(controller_returned is None)
#        self.failUnless(task_furl_exists)
#        self.failUnless(multiengine_furl_exists)
#        self.failUnless(engine_furl_exists)
#
#
#
#class TestIPythonParameterSearch(TestParameterSearch):
#    def get_mec(self):
#        """
#        workaround for stochastic MultiEngineClient failure.
#        """
#        from IPython.kernel import client
#        import time
##        try:
##            return self.mec
##        except AttributeError:
#        i = 10
#        while i > 0:
#            try:
#                self.mec = client.MultiEngineClient(furl_or_file =
#                                               self.multiengine_furl)
#                return self.mec
#            except Exception, e:
#                print "Couldn't create MultiEngineClient," +\
#                       """ retrying %d times"""%i
#                i = i-1
#                time.sleep(0.33)
#                if i == 0:
#                    raise e
#
#    def setUp(self):
#        print '--- setting it up'
#        import subprocess, tempfile
#        (fd, engine_furl) = tempfile.mkstemp(prefix='engine-furl')
#        (fd, multiengine_furl) = tempfile.mkstemp(prefix='multiengine-furl')
#        (fd, task_furl) = tempfile.mkstemp(prefix='task-furl')
#        self.contr = subprocess.Popen(args = ['ipcontroller',
#                              '--engine-furl-file=%s'%engine_furl,
#                              '--multiengine-furl-file=%s'%multiengine_furl,
#                              '--task-furl-file=%s'%task_furl])
#        self.engine_furl = engine_furl
#        self.multiengine_furl = multiengine_furl
#        self.task_furl = task_furl
#
#        max_wait = 10. # sec
#        import time
#        t = time.time()
#        from IPython.kernel import client
#        while True:
#            try:
#                mec = client.MultiEngineClient(furl_or_file = multiengine_furl)
#                time.sleep(0.5)
#                break
#            except Exception, e:
#                if (time.time() - t) < max_wait:
#                    print "can't connect to controller yet. Retrying..."
#                    time.sleep(0.33)
#                else:
#                    print "No connection after %f seconds. Giving up..."
#                    raise e
##        import time
##        time.sleep(2) # wait two seconds for ipcontroller to come up
#        eng = subprocess.Popen(args = ['ipengine',
#                                       '--furl-file=%s'%engine_furl])
#        mec = self.get_mec()
#        while len(mec.get_ids()) < 1:
#            time.sleep(0.33)
#        print '--- setup complete'
#
#    def tearDown(self):
#        print '--- beginning tear-down'
#        mec = self.get_mec()
#        mec.kill(controller=True, block=True)
#        import os, signal
#        # kill controller again to make sure it's down
#        os.kill(self.contr.pid, signal.SIGINT)
#        for f in [self.multiengine_furl, self.task_furl, self.engine_furl]:
#            os.remove(f)
#        import time
#        time.sleep(2.5) # wait for socket to free
#        print '---- tore it down'
#
##class TestIPythonParameterSearcher(TestIPythonParameterSearch):
##    def test_IPythonParameterSearcher(self):
##        mec = self.get_mec()
##        while len(mec.get_ids()) < 1:
##            time.sleep(0.33)
##        (dict_iterable, result) = self.parametersearch(IPythonParameterSearcher,
##                                    task_furl = self.task_furl,
##                                    multiengine_furl = self.multiengine_furl,
##                                    engine_furl = self.engine_furl)
##        self.assertEqual(dict_iterable, result)
##
##class TestFailingTasks(TestIPythonParameterSearch):
##    def parametersearch(self, searcher, **kwargs):
##        def will_fail(param):
##            raise(Exception(param['str']))
##        dict_iterable = [{'str':'failure'},
##                    {'str':'failure'},
##                    {'str':'failure'}]
##        ps = searcher(dict_iterable = dict_iterable, func = will_fail, **kwargs)
##        ps.search()
##        result = ps.harvest()
##        return (dict_iterable, result, ps)
##
##    def test_failingIPythonParameterSearcher(self):
##        """
##        tests if failing tasks are kept track of correctly.
##        """
##        (dict_iterable, result, ps) = self.parametersearch(IPythonParameterSearcher,
##                                    task_furl = self.task_furl,
##                                    multiengine_furl = self.multiengine_furl,
##                                    engine_furl = self.engine_furl)
##        for i in range(len(ps.failed_tasks)):
##            exception= ps.failed_tasks[i]['exception']
##            self.assertEqual(type(exception), Exception)
##            self.assertEqual(ps.failed_tasks[i]['taskid'], i)
#
#
#class TestRestartingIPythonParameterSearch(TestIPythonParameterSearch):
#    """
#    Test cases for IPython-specific features which involve process control.
#    """
##    def test_failIfIpenginesExist(self):
##        """
##        tests exception generation if existing Ipengines are encountered.
##
##        """
##        print '--- test_failIfIpenginesExist'
##        self.failUnlessRaises(Exception,
##                              RestartingIPythonParameterSearcher,
##                              {'take_down': False,
##                               'task_furl': self.task_furl,
##                               'multiengine_furl': self.multiengine_furl,
##                               'engine_furl': self.engine_furl})
##
##    def test_RestartingIPythonParameterSearcher(self):
##        """
##        tests plain parameter searching.
##        """
##        print '--- test_RestartingIPythonParameterSearcher'
##        (dict_iterable, result) = self.parametersearch(
##                                    RestartingIPythonParameterSearcher,
##                                    take_down = True,
##                                    task_furl = self.task_furl,
##                                    multiengine_furl = self.multiengine_furl,
##                                    engine_furl = self.engine_furl)
###        print result
##        self.assertEqual(dict_iterable, result)
#
#    def test_KillIPythonEngines(self):
#        """
#        tests if existing IPengines are indeed taken down.
#        """
#        print '--- test_KillIPythonEngines'
#        from IPython.kernel import client
#        mec = self.get_mec()
#        ids = mec.get_ids()
#        mec.execute('test_beacon = 1234')
#        ps = RestartingIPythonParameterSearcher(take_down = True,
#                            task_furl = self.task_furl,
#                            multiengine_furl = self.multiengine_furl,
#                            engine_furl = self.engine_furl)
##        import time
##        time.sleep(2)
##        mec = self.get_mec()
#        mec = self.get_mec()
#        import IPython.kernel.error as er
#        try:
#            mec.pull('test_beacon')
#        except Exception, e:
#            if type(e) == er.NoEnginesRegistered:
#                pass
#            else:
#                print 'Trying to retrieve data raised an exception'+\
#                        'as it should, but not the one we expected.'+\
#                        'Exception was:'+ '\n' + '%s \n%s'%(type(e), e)
#        print '--- test_KillIPythonEngines_afterFail'
#
#
#class TestMPIRestartingIPythonParameterSearch(TestIPythonParameterSearch):
#    """
#    Test cases for IPython-specific features which involve process control.
#    """
##    def test_failIfIpenginesExist(self):
##        """
##        tests exception generation if existing Ipengines are encountered.
##        """
##        print '--- test_failIfIpenginesExist'
##        self.failUnlessRaises(Exception,
##                              MPIRestartingIPythonParameterSearcher,
##                              {'take_down':False,
##                               'task_furl': self.task_furl,
##                               'multiengine_furl': self.multiengine_furl,
##                               'engine_furl': self.engine_furl})
##
##    def test_MPIRestartingIPythonParameterSearcher(self):
##        """
##        tests plain parameter searching.
##        """
##        print '--- test_MPIRestartingIPythonParameterSearcher'
##        (dict_iterable, result) = self.parametersearch(
##                                MPIRestartingIPythonParameterSearcher,
##                                task_furl = self.task_furl,
##                                multiengine_furl = self.multiengine_furl,
##                                engine_furl = self.engine_furl,
##                                take_down = True)
###        print result
##        self.assertEqual(dict_iterable, result)
#
#    def test_KillIPythonEngines(self):
#        """
#        tests if existing IPengines are indeed taken down.
#        """
#        print '--- test_KillIPythonEngines'
#        mec = self.get_mec()
#        ids = mec.get_ids()
#        mec.execute('test_beacon = 1234')
#        ps = MPIRestartingIPythonParameterSearcher(
#                                task_furl = self.task_furl,
#                                multiengine_furl = self.multiengine_furl,
#                                engine_furl = self.engine_furl,
#                                take_down=True)
##        import time
##        time.sleep(2)
#        mec = self.get_mec()
#        import IPython.kernel.error as er
#        try:
#            mec.pull('test_beacon')
#        except Exception, e:
#            if type(e) == er.NoEnginesRegistered:
#                pass
#            else:
#                import pdb
#                pdb.set_trace()
#                print 'Trying to retrieve data raised an exception'+\
#                        'as it should, but not the one we expected.\n' +\
#                        'Exception was:'+ '\n' + '%s \n%s'%(type(e),e)
#        print '--- test_KillIPythonEngines_afterFail'
#
if __name__ == '__main__':
    unittest.main()
