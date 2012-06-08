"""
Unit tests for the neurotools.signals module
"""

import matplotlib
matplotlib.use('Agg')

from neurotools import io
import neurotools.signals.spikes as spikes
import neurotools.signals.analogs as analogs
from neurotools.signals.pairs import *

import numpy, unittest, os
from neurotools.__init__ import check_numpy_version, check_dependency
newnum = check_numpy_version()

ENABLE_PLOTS = check_dependency('pylab')
if ENABLE_PLOTS:
    import pylab


def arrays_are_equal(a, b):
    a.sort()
    b.sort()
    eq = a==b
    if isinstance(eq, bool):
        return eq
    else: # array
        return eq.all()

class SpikeTrainTest(unittest.TestCase):
    
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def testCreateSpikeTrain(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10))
        assert (spk.t_start == 0) and (spk.t_stop == 100)
        self.assert_( arrays_are_equal(spk.spike_times, numpy.arange(0,110,10)) )
    
    def testCreateSpikeTrainFromList(self):
        spk = spikes.SpikeTrain(range(0,110,10))
        assert (spk.t_start == 0) and (spk.t_stop == 100)
        self.assert_( arrays_are_equal(spk.spike_times, numpy.arange(0,110,10)) )
    
    def testCreateSpikeTrainFull(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10), 0, 100)
        assert (spk.t_start == 0) and (spk.t_stop == 100)
    
    def testCreateWithTStartOnly(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10), t_start=20)
        assert (spk.t_start == 20) and (spk.t_stop == 100)
        assert arrays_are_equal( spk.spike_times, numpy.arange(20, 110, 10) )
        
    def testCreateWithTStopOnly(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10), t_stop=70)
        assert (spk.t_start == 0) and (spk.t_stop == 70)
        assert arrays_are_equal( spk.spike_times, numpy.arange(0, 80, 10) )
    
    def testCreateSpikeSmallWrongTimes(self):
        self.assertRaises(Exception, spikes.SpikeTrain, numpy.arange(0,110,10), 20, 10)
    
    def testCreateSpikeTrainNegativeTstart(self):
        self.assertRaises(ValueError, spikes.SpikeTrain, numpy.arange(0,110,10), -20, 10)
    
    def testCreateSpikeTrainNegativeSpikeTime(self):
        self.assertRaises(ValueError, spikes.SpikeTrain, numpy.arange(-100,110,10))
    
    def testCreateWithInvalidValuesInList(self):
        self.assertRaises(ValueError, spikes.SpikeTrain, [0.0, "elephant", 0.3, -0.6, 0.15])
    
    def testCopy(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10), 0, 100)
        spk2 = spk.copy()
        assert spk.is_equal(spk2)
    
    def testDuration(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10), 0, 100)
        assert spk.duration() == 100
    
    def testMerge(self):
        spk = spikes.SpikeTrain(numpy.arange(0,110,10))
        spk2 = spikes.SpikeTrain(numpy.arange(100,210,10))
        spk.merge(spk2)
        assert (spk.t_stop == 200) and (len(spk) == 22)
    
    def testTimeAxis(self):
        spk = spikes.SpikeTrain(numpy.arange(0,1010,10))
        if newnum:
            assert len(spk.time_axis(100)) == 11
        else:
            assert len(spk.time_axis(100)) == 10
    
    def testAddOffset(self):
        spk = spikes.SpikeTrain(numpy.arange(0,1010,10))
        spk.time_offset(50)
        assert (spk.t_start == 50) and (spk.t_stop == 1050) and numpy.all(spk.spike_times == numpy.arange(50,1060,10))
    
    def testTime_Slice(self):
        spk1 = spikes.SpikeTrain(numpy.arange(0,1010,10))
        spk1 = spk1.time_slice(250, 750)
        assert len(numpy.extract((spk1.spike_times < 250) | (spk1.spike_times > 750), spk1.spike_times)) == 0
        spk2 = spikes.SpikeTrain([0.0, 0.1, 0.3, 0.6, 0.15])
        self.assert_( arrays_are_equal(spikes.SpikeTrain([0.15, 0.3]).spike_times,
                                       spk2.time_slice(0.11,0.4).spike_times) ) # should not include 0.1
        self.assert_( arrays_are_equal(spikes.SpikeTrain([0.1, 0.15, 0.3]).spike_times,
                                       spk2.time_slice(0.10,0.4).spike_times) ) # should include 0.1
        
    def testIsi(self):
        spk = spikes.SpikeTrain(numpy.arange(0,200,10))
        assert numpy.all(spk.isi() == 10)
    
    def testMeanRate(self):
        poisson_param = 1./40
        isi           = numpy.random.exponential(poisson_param, 1000)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk = spikes.SpikeTrain(poisson_times)
        assert   35 < spk.mean_rate() < 45
    
    # def testMeanRateParams(self):
    #     # TODO: Failing
    #     poisson_param = 1./40
    #     isi           = numpy.random.exponential(poisson_param, 1000)
    #     poisson_times = numpy.cumsum(isi)*1000.  # To convert the spikes_time in ms
    #     spk1 = spikes.SpikeTrain(poisson_times,t_start=0,t_stop=5000)
    #     spk2 = spikes.SpikeTrain(range(10), t_stop=10)
    #     assert   30 < spk1.mean_rate() < 50
    #     self.assertEqual(spk2.mean_rate(), 1000.0)
    #     self.assertAlmostEqual(spk2.mean_rate(t_stop=4.99999999999), 1000.0, 6)
    #     self.assertEqual(spk2.mean_rate(t_stop=5.0), 1200.0)
    
    def testCvIsi(self):
        poisson_param = 1./40
        isi           = numpy.random.exponential(poisson_param, 1000)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk1 = spikes.SpikeTrain(poisson_times)
        spk2 = spikes.SpikeTrain(range(10), t_stop=10)
        assert 0.9 < spk1.cv_isi() < 1.1
        self.assertEqual(spk2.cv_isi(), 0)


    # def testCvKL(self):
    #     # TODO: failing
    #     poisson_param = 1./10 # 1 / firing_frequency
    #     isi           = numpy.random.exponential(poisson_param, 1000)
    #     poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
    #     spk1 = spikes.SpikeTrain(poisson_times)
    #     assert 0.9 < spk1.cv_kl(bins = 1000) < 1.1
    #     # does not depend on bin size
    #     assert 0.9 < spk1.cv_kl(bins = 100) < 1.1
    #     # does not depend on time
    #     poisson_param = 1./4
    #     isi           = numpy.random.exponential(poisson_param, 1000)
    #     poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
    #     spk1 = spikes.SpikeTrain(poisson_times)
    #     assert 0.9 < spk1.cv_kl() < 1.1
    #     spk2 = spikes.SpikeTrain(range(10), t_stop=10)
    #     self.assertEqual(spk2.cv_isi(), 0)
    
    def testHistogram(self):
        poisson_param = 1./40
        isi           = numpy.random.exponential(poisson_param, 1000)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk = spikes.SpikeTrain(poisson_times)
        hist = spk.time_histogram(5000)
        N = len(hist) - 1
        assert numpy.all((30 < hist[0:N]) & (hist[0:N] < 60))
    
    def testVictorPurpuraDistance(self):
        poisson_param = 1./40
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk = spikes.SpikeTrain(poisson_times)
        
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk2 = spikes.SpikeTrain(poisson_times)
        
        poisson_param = 1./5
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk3 = spikes.SpikeTrain(poisson_times)
        
        assert (spk.distance_victorpurpura(spk2,0.1) < spk.distance_victorpurpura(spk3,0.1)) \
                and (spk.distance_victorpurpura(spk, 0.1) == 0)
    
    def testKreuzDistance(self):
        poisson_param = 1./40
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk = spikes.SpikeTrain(poisson_times)
        
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk2 = spikes.SpikeTrain(poisson_times)
        
        poisson_param = 1./5
        isi           = numpy.random.exponential(poisson_param, 20)
        poisson_times = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
        spk3 = spikes.SpikeTrain(poisson_times)
        
        assert (spk.distance_kreuz(spk2) < spk.distance_kreuz(spk3)) and (spk.distance_kreuz(spk) == 0)

    def testFanoFactorIsi(self):
        spk = spikes.SpikeTrain(numpy.arange(0,1010,10))
        assert spk.fano_factor_isi() == 0.


class SpikeListTest(unittest.TestCase):

    def setUp(self):
        self.spikes = []
        nb_cells = 10
        frequencies = [nb_cells for _ in xrange(10)]
        for idx in xrange(nb_cells):
            param = 1. / frequencies[idx]
            isi = numpy.random.exponential(param, 1000)
            pspikes = numpy.cumsum(isi) * 1000.  # convert to ms
            for spike in pspikes:
                self.spikes.append((idx, spike))
        self.spk = spikes.SpikeList(self.spikes, range(10))

    def tearDown(self):
        pass

    def testCreateSpikeList(self):
        assert len(self.spk) == 10
        assert numpy.all(self.spk.id_list == numpy.arange(10))

    def testGetItem(self):
        assert isinstance(self.spk[0], spikes.SpikeTrain)

    def testSetItemWrongType(self):
        self.assertRaises(Exception, self.spk.__setitem__,
                          0, numpy.arange(100))

    def testSetItem(self):
        spktrain = spikes.SpikeTrain(numpy.arange(10))
        self.spk[11] = spktrain
        assert len(self.spk) == 11

    def testGetSlice(self):
        assert len(self.spk[0:5]) == 5

    def testAppend(self):
        spktrain = spikes.SpikeTrain(numpy.arange(10))
        self.assertRaises(Exception, self.spk.append, 0, spktrain)

    def testConcatenate(self):
        self.assertRaises(Exception, self.spk.concatenate, self.spk)

    def testMerge(self):
        spk2 = spikes.SpikeList(self.spikes, range(50,60))
        self.spk.merge(spk2)
        assert len(self.spk) == 20

    def testId_SliceInt(self):
        assert len(self.spk.id_slice(5)) == 5

    def testCopy(self):
        spk2 = self.spk.copy()
        assert len(spk2) == len(self.spk) and (spk2[0].is_equal(self.spk[0]))

    def testId_SliceList(self):
        assert numpy.all(self.spk.id_slice([0,1,2,3]).id_list == [0,1,2,3])

    def testTime_Slice(self):
        spk = spikes.SpikeList(self.spikes,range(10), t_start=0)
        new_spk = spk.time_slice(0, 1000.)
        assert (new_spk.t_start == spk.t_start) and (new_spk.t_stop == 1000.)

    def testAddOffset(self):
        spk2 = self.spk.time_slice(0,1000)
        spk2.time_offset(100)
        assert (spk2.t_start == 100) and (spk2.t_stop == 1100)

    def testFirstSpikeTime(self):
        assert self.spk.first_spike_time() >= self.spk.t_start

    def testLastSpikeTime(self):
        assert self.spk.last_spike_time() <= self.spk.t_stop

    def testSelect_Ids(self):
        spks = []
        nb_cells = 3
        frequencies = [5, 40, 40]
        for idx in xrange(nb_cells):
            param = 1. / frequencies[idx]
            isi = numpy.random.exponential(param, 100)
            pspikes = numpy.cumsum(isi) * 1000.  # convert to ms
            for spike in pspikes:
                spks.append((idx, spike))
        spk = spikes.SpikeList(spks,range(3),0,1000)
        assert len(spk.select_ids("cell.mean_rate() < 20")) == 1

    def testIsis(self):
        pass

    def testCV_Isis(self):
        assert 0.8 < numpy.mean(self.spk.cv_isi()) < 1.2

    def testCVKL(self):
        assert 0.8 < numpy.mean(self.spk.cv_kl()) < 1.2

    def testCVLocal(self):
        assert 0.8 < self.spk.cv_local() < 1.2

    def testMeanRate(self):
        assert 5 < self.spk.mean_rate() < 15

    def testMeanRates(self):
        correct = True
        rates = self.spk.mean_rates()
        for idx in xrange(len(self.spk.id_list)):
            if not(5 < rates[idx] < 15):
                correct = False
        assert correct

    def testMeanRateStd(self):
        assert self.spk.mean_rate_std() >= 0

    def testMeanRateVarianceAndCovariance(self):
        assert (abs(self.spk.mean_rate_variance(10) - self.spk.mean_rate_covariance(self.spk, 10)) < 0.01)

    def testSaveWrongFormat(self):
        self.assertRaises(Exception, self.spk.save, 2.3)

    def testSaveAndLoadTxt(self):
        self.spk.save("tmp.txt")
        spk2 = spikes.load_spikelist("tmp.txt")
        assert len(spk2) == len(self.spk)
    
    def testSaveAndLoadTxtTimePart(self):
        self.spk.save("tmp.txt")
        spk2 = spikes.load_spikelist("tmp.txt", t_start = 0, t_stop= 50)
        assert (spk2.t_start == 0) and (spk2.t_stop == 50)

    def testSaveAndLoadTxtIdsPart(self):
        self.spk.save("tmp.txt")
        spk2 = spikes.load_spikelist("tmp.txt", id_list=[1,2,3])
        assert numpy.all(spk2.id_list == [1,2,3])
    
    def testSaveAndLoadTxtIdsPartInt(self):
        file = io.StandardTextFile("tmp.txt")
        self.spk.save(file)
        spk2 = spikes.load_spikelist(file, id_list=5)
        assert numpy.all(spk2.id_list == [0,1,2,3,4])

    def testSaveAndLoadPickle(self):
        file = io.StandardPickleFile("tmp.pickle")
        self.spk.save(file)
        spk2 = spikes.load_spikelist(file)
        assert len(spk2) == len(self.spk)

    def testSaveAndLoadPickleTimePart(self):
        file = io.StandardPickleFile("tmp.pickle")
        self.spk.save(file)
        spk2 = spikes.load_spikelist(file, t_start = 0, t_stop= 50)
        assert (spk2.t_start == 0) and (spk2.t_stop == 50)

    # def testSaveAndLoadPickleIdsPart(self):
    #     file = io.StandardPickleFile("tmp.pickle")
    #     self.spk.save(file)
    #     spk2 = spikes.load_spikelist(file, id_list=[1,2,3])
    #     assert numpy.all(spk2.id_list == [1,2,3])
    
    # def testSaveAndLoadPickleIdsPartInt(self):
    #     file = io.StandardPickleFile("tmp.pickle")
    #     self.spk.save(file)
    #     spk2 = spikes.load_spikelist(file, id_list=5)
    #     assert numpy.all(spk2.id_list == [0,1,2,3,4])

    def testPairwise_Pearson_CorrCoeff(self):
        x1,y1 = self.spk.pairwise_pearson_corrcoeff(10, time_bin=1.)
        assert x1 < y1

    def testRawData(self):
        data = self.spk.raw_data()
        assert (data.shape[0] > 0) and (data.shape[1] == 2)

    # def testVictorPurpuraDistance(self):
    #     # TODO: failing
    #     d_spike = self.spk.distance_victorpurpura(5, cost=0.2)
    #     d_rate  = self.spk.distance_victorpurpura(5, cost=0.8)
    #     d_self  = self.spk.distance_victorpurpura(10, cost = 0.5)
    #     assert (d_rate != d_spike) and d_self == 0
    
    # def testKreuzDistance(self):
    #     # TODO: failing
    #     d_self = self.spk.distance_kreuz(10)
    #     assert d_self == 0
    
    def testCrossCorrZero(self):
        cc1 = self.spk.pairwise_cc_zero(5, AutoPairs(self.spk, self.spk), time_bin=0.1)
        cc2 = self.spk.pairwise_cc_zero(5, RandomPairs(self.spk, self.spk), time_bin=0.1)
        assert (0 <= cc1 <= 1) and (cc1 > cc2)

    # def testFanoFactor(self):
    #     # TODO: failing
    #     assert 0.9 < self.spk.fano_factor(5) < 1.1

    def testIdOffset(self):
        self.spk.id_offset(100)
        assert numpy.all(self.spk.id_list == numpy.arange(100,110))


class LoadSpikeListTest(unittest.TestCase):
    
    def setUp(self):
        self.spikes=[]
        nb_cells = 50
        frequencies = numpy.random.uniform(0, 50, nb_cells)
        for idx in xrange(nb_cells):
            param   = 1./frequencies[idx]
            isi     = numpy.random.exponential(param, 100)
            pspikes = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
            for spike in pspikes: 
                self.spikes.append((idx, spike))
        self.spk = spikes.SpikeList(self.spikes, range(nb_cells), 0, 4000)
        self.spk.save("tmp2.txt")
    
    def testLoadSpikeList(self):
        spk = spikes.load_spikelist("tmp2.txt")
        assert (len(spk) == 50) and (spk.mean_rate() > 0)
    
    def testLoadSpikeListWithIds(self):
        spk = spikes.load_spikelist("tmp2.txt", id_list=range(30,40))
        assert (len(spk) == 10) and (spk.mean_rate() > 0)
    
    def testLoadSpikeListWithTime(self):
        spk = spikes.load_spikelist("tmp2.txt", id_list=range(30,40), t_start=0, t_stop=100)
        assert (len(spk) == 10) and (spk.mean_rate() > 0) and (spk.time_parameters() == (0,100))

    def testLoadForSpikeList(self):
        spk = spikes.load("tmp2.txt",'s')
        assert (len(spk) == 50) and (spk.mean_rate() > 0)


# TODO: Evaluate if pyNN should be integrated, and how
# class PyNNInterface(unittest.TestCase):
#     def setUp(self):
#         if not os.path.exists("Simulation"):
#             os.mkdir("Simulation")
#         else:
#             os.system("rm -rf Simulation/*.*")
#         import pyNN.nest2 as pynn
#         import pyNN.recording as rec
#         pynn.setup()
#         p1 = pynn.Population(10, pynn.IF_cond_exp)
#         pynn.Projection(p1,p1, pynn.AllToAllConnector(weights=0.1))
#         stim = pynn.Population(1, pynn.SpikeSourcePoisson)
#         pynn.Projection(stim, p1, pynn.AllToAllConnector(weights=0.1))
#         p2 = pynn.Population(10, pynn.IF_cond_exp)
#         pynn.Projection(p1,p2, pynn.AllToAllConnector(weights=0.1))
#         p1.record_v()
#         p1.record()
#         p1.record_c()
#         p2.record_v()
#         p2.record()
#         p2.record_c()
#         pynn.run(100)
#         p1.printSpikes("Simulation/p1.spikes")
#         p1.print_v("Simulation/p1.v")
#         p1.print_c("Simulation/p1.c")
#         p2.printSpikes("Simulation/p2.spikes")
#         p2.print_v("Simulation/p2.v")
#         p2.print_c("Simulation/p2.c")
#     def testLoadFirstPopulationData(self):
#         spks   = spikes.load("Simulation/p1.spikes",'s')
#         vm     = spikes.load("Simulation/p1.v",'v')
#         ge, gi = spikes.load("Simulation/p1.c",'g')
#         assert len(spks) == 10 and len(vm) == 10 and len(ge) == 10 and len(gi) == 10
#     def testLoadSecondPopulationData(self):
#         spks   = spikes.load("Simulation/p2.spikes",'s')
#         vm     = spikes.load("Simulation/p2.v",'v')
#         ge, gi = spikes.load("Simulation/p2.c",'g')
#         assert len(spks) == 10 and len(vm) == 10 and len(ge) == 10 and len(gi) == 10



class SpikeListGraphicTest(unittest.TestCase):
    
    def setUp(self):
        self.spikes=[]
        nb_cells = 50
        frequencies = numpy.random.uniform(0, 50, 50)
        for idx in xrange(nb_cells):
            param   = 1./frequencies[idx]
            isi     = numpy.random.exponential(param, 100)
            pspikes = numpy.cumsum(isi)*1000. # To convert the spikes_time in ms
            for spike in pspikes: 
                self.spikes.append((idx, spike))
        self.spk = spikes.SpikeList(self.spikes, range(50), 0, 4000)
        try:
            os.mkdir("Plots")
        except Exception:
            pass
     
    def testGraphics(self):
        self.spk.isi_hist(display=pylab.subplot(221), kwargs={'color':'red'})
        self.spk.cv_isi_hist(10, display=pylab.subplot(222))
        self.spk.rate_distribution(20, normalize=True, display=pylab.subplot(223), kwargs={})
        self.spk.firing_rate(100, display=pylab.subplot(224),kwargs={'linewidth':2})
        pylab.savefig("Plots/SpikeList_various.png")
        pylab.close()
    
    def testRasterPlots(self):
        self.spk.raster_plot(id_list = 30, display=pylab.subplot(221), kwargs={'color':'red'})
        self.spk.raster_plot(id_list = range(50), display=pylab.subplot(222))
        self.spk.raster_plot(t_start = 200, display=pylab.subplot(223), kwargs={})
        self.spk.raster_plot(t_stop  = 1000,display=pylab.subplot(224),kwargs={'marker':'+'})
        pylab.savefig("Plots/SpikeList_rasters.png")
        pylab.close()
    
    def testActivityMap(self):
        self.spk.dimensions = [5, 10]
        self.spk.activity_map(t_start = 1000, t_stop = 2000, display=pylab.subplot(211), kwargs={'interpolation':'bicubic'})
        positions = pylab.rand(2, 50)
        self.spk.activity_map(float_positions = positions, display=pylab.subplot(212))
        pylab.savefig("Plots/SpikeList_activitymaps.png")
        pylab.close()
        
    def testPairwiseCC(self):
        self.spk.pairwise_cc(50, time_bin=10., average=True, display=pylab.subplot(221))
        self.spk.pairwise_cc(50, time_bin=10., average=False, display=pylab.subplot(222))
        self.spk.pairwise_cc(50, RandomPairs(self.spk, self.spk), time_bin=10., average=True, display=pylab.subplot(223))
        self.spk.pairwise_cc(50, AutoPairs(self.spk, self.spk), time_bin=10., display=pylab.subplot(224))
        pylab.savefig("Plots/SpikeList_pairwise_cc.png")
        pylab.close() 
    
    def testPairwiseCCZero(self):
        self.spk.pairwise_cc_zero(50, time_bin=10., time_window=100, display=pylab.subplot(311))
        self.spk.pairwise_cc_zero(50, RandomPairs(self.spk, self.spk), time_bin=10., time_window=200, display=pylab.subplot(312))
        self.spk.pairwise_cc_zero(50, AutoPairs(self.spk, self.spk), time_bin=10., time_window=200, display=pylab.subplot(313))
        pylab.savefig("Plots/SpikeList_pairwise_cc_zero.png")
        pylab.close() 
   
    def testActivityMovie(self):
        self.spk.dimensions = [5, 10]
        self.spk.activity_movie(t_start = 1000, t_stop = 2000, time_bin = 100, kwargs={'interpolation':'bicubic'},
                                output="Plots/SpikeList_activitymovie.mpg")

if __name__ == "__main__":
    unittest.main()
