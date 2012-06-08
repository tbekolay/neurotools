"""
Unit tests for the neurotools.signals module
"""

from neurotools import io
import neurotools.signals.analogs as analogs

import numpy as np
import os
import unittest
from neurotools.__init__ import check_numpy_version, check_dependency
newnum = check_numpy_version()

ENABLE_PLOTS = check_dependency('pylab')
if ENABLE_PLOTS:
    import pylab


class AnalogSignal(unittest.TestCase):

    def setUp(self):
        pass

    def testCreateAnalogSignal(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1)
        assert len(sig) == 10000

    def testCreateAnalogSignalWithTstart(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1, 10)
        self.assertEqual(len(sig), 10000)
        self.assertEqual(sig.t_start, 10.0)
        self.assertEqual(sig.t_stop, 10.0 + 10000 * 0.1)

    def testCreateAnalogSignalWithTstartTstop(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1, 10, 1010)
        self.assertEqual(len(sig), 10000)
        self.assertEqual(sig.t_start, 10.0)
        self.assertEqual(sig.t_stop, 1010.0)

    def testCreateAnalogSignalWrongTimes(self):
        self.assertRaises(Exception, analogs.AnalogSignal,
                          np.arange(10000), 0.1, 100, 70)

    def testTimeAxis(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1)
        assert len(sig.time_axis() == len(sig)+1)

    def testTimeSlice(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1)
        res = sig.time_slice(0,500)
        self.assertEqual(len(res), 5000)
        res = sig.time_slice(250,750)
        self.assertEqual(len(res), 5000)

    def testSliceByEvents(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1)
        res1 = sig.slice_by_events([0, 50, 100],t_min=0, t_max=50)
        res2 = sig.slice_by_events(analogs.SpikeTrain([0, 50, 100]),t_min=0, t_max=50)
        assert len(res1) == 3 and len(res2) == 3

    def testSliceExcludeEvents(self):
        sig = analogs.AnalogSignal(np.sin(np.arange(10000.)), 0.1)
        # check something in the middle splits in 2
        res0 = list(sig.slice_exclude_events([500.0],t_min=0., t_max=0.))
        assert len(res0)==2
        assert res0[0].t_stop == res0[1].t_start
        assert res0[0].t_start == sig.t_start
        assert res0[1].t_stop == sig.t_stop

        # check that event at t_start yields only one slice, removing t_max
        res1 = list(sig.slice_exclude_events([0.0],t_min=10., t_max=10.))
        assert len(res1)==1
        assert res1[0].t_start == sig.t_start+10.0
        assert res1[0].duration() == 990.0      


        # check something in the middle splits in 2
        res2 = list(sig.slice_exclude_events([250.0, 750.0], t_min=50., t_max=50.))
        assert len(res2)==3
        assert res2[0].duration() == 200.0
        assert res2[1].duration() == 400.0
        assert res2[2].duration() == 200.0

        # check behaviour at the end (t_stop)
        res3 = list(sig.slice_exclude_events([1000.0], t_min=50., t_max=50.))
        assert len(res3)==1
        assert res3[0].duration() == 950.0

    def testCovariance(self):
        a1 = analogs.AnalogSignal(np.random.normal(size=10000),dt=0.1)
        a2 = analogs.AnalogSignal(np.random.normal(size=10000),dt=0.1)
        assert a1.cov(a2) < 0.5
        assert a1.cov(a1) > 0.5
        
        
    def testThresholdDetection(self):
        sig = np.zeros(10000)
        for idx in xrange(10):
            sig[100*idx:100*idx+50] = 0.5
        sig = analogs.AnalogSignal(sig, 0.1)
        res = sig.threshold_detection(0.1)
        assert len(res) == 10
        
        
        
class AnalogSignalList(unittest.TestCase):
    
    def setUp(self):
        self.values=[]
        nb_cells = 10
        frequencies = range(10,110,10)
        for idx in xrange(nb_cells):
            sig = np.sin(np.arange(1000))
            for val in sig: 
                self.values.append((idx, val))
        self.analog = analogs.AnalogSignalList(self.values, range(10), 0.1)
    
    def testAppend(self):
        analog = analogs.AnalogSignal(np.arange(10000), 0.1)
        self.assertRaises(Exception, self.analog.append, 0, analog)
    
    def testId_SliceInt(self):
        assert len(self.analog.id_slice(5)) == 5
    
    def testId_SliceList(self):
        assert np.all(self.analog.id_slice([0,1,2,3]).id_list() == [0,1,2,3])
    
    def testTime_Slice(self):
        new_analog = self.analog.time_slice(0, 50.)
        assert (new_analog.t_start == self.analog.t_start) and (new_analog.t_stop == 50.)
        new_analog = self.analog.time_slice(self.analog.t_start, self.analog.t_stop)
        self.assertEqual(len(new_analog[0]), len(self.analog[0]))
    
    def testCreateAnalogSignalList(self):
        analog = analogs.AnalogSignalList(self.values, range(10), 0.1, 0, 100)
        assert analog.t_start == 0 and analog.t_stop == 100
    
    # def testSaveAndLoadTxt(self):
    #     self.analog.save("tmp.txt")
    #     analog2 = analogs.load_vmlist("tmp.txt")
    #     assert len(analog2) == len(self.analog)
    
    # def testSaveAndLoadTxtTimePart(self):
    #     self.analog.save("tmp.txt")
    #     analog2 = analogs.load_vmlist("tmp.txt", t_start=0, t_stop=100)
    #     assert analog2.t_stop == 100
    
    # def testSaveAndLoadTxtIdsPart(self):
    #     self.analog.save("tmp.txt")
    #     analog2 = analogs.load_vmlist("tmp.txt", id_list=range(5))
    #     assert len(analog2) == 5

    def testSaveAndLoadPickle(self):
        file = io.StandardPickleFile("tmp.pickle")
        self.analog.save(file)
        analog2 = analogs.load_vmlist(file)
        assert len(analog2) == len(self.analog)
    
    def testSaveAndLoadPickleTimePart(self):
        file = io.StandardPickleFile("tmp.pickle")
        self.analog.save(file)
        analog2 = analogs.load_vmlist(file, t_start=0, t_stop=100)
        assert analog2.t_stop == 100
    
    # def testSaveAndLoadPickleIdsPart(self):
    #     file = io.StandardPickleFile("tmp.pickle")
    #     self.analog.save(file)
    #     analog2 = analogs.load_vmlist(file, id_list=range(5))
    #     assert len(analog2) == 5

    def testRawData(self):
        data = self.analog.raw_data()
        assert (data.shape[0] > 0) and (data.shape[1] == 2)

    def testMean(self):
        assert len(self.analog.mean()) == len(self.analog[0])
    
    def testStd(self):
        assert len(self.analog.std()) == len(self.analog[0])

    def testSelectIds(self):
        assert type(self.analog.select_ids("cell.mean() > 0")) == list


class VmListGraphicTest(unittest.TestCase):
    
    def setUp(self):
        self.values=[]
        nb_cells = 10
        frequencies = np.arange(0,100,10)
        for idx in xrange(nb_cells):
            sig = np.sin(2*3.14*frequencies[idx]*np.arange(1000))
            for val in sig: 
                self.values.append((idx, val))
        self.analog = analogs.VmList(self.values, range(10), 0.1)
        try:
            os.mkdir("Plots")
        except Exception:
            pass
     
    def testGraphics(self):
        self.analog.plot(2, v_thresh = 1, display=pylab.subplot(211))
        self.analog.plot(range(2), v_thresh = 1, display=pylab.subplot(212))
        pylab.savefig("Plots/VmList_plot.png")
        pylab.close()
    
    def testEventTriggeredAverage(self):
        spktrain = analogs.SpikeTrain(np.array(100*np.random.rand(10),int))
        vm = self.analog[9]
        vm.event_triggered_average(spktrain, average=False, t_max=30, display=pylab.subplot(211))
        vm.event_triggered_average(range(0,100,10), average=True, t_min=10, t_max = 30, display=pylab.subplot(212))
        pylab.savefig("Plots/EventTriggerAverage_plot.png")
        pylab.close()


if __name__ == "__main__":
    unittest.main()
# ==============================================================================
