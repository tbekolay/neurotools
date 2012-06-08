"""
Unit tests for the neurotools.stgen module
"""

import unittest
from neurotools import stgen
from neurotools import signals
import numpy


class StatisticalError(Exception):
    pass


class StGenInitTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testCreateWithNoArgs(self):
        """
        With no arguments for the constructor, we should get a Numpy RNG.
        """
        stg = stgen.StGen()
        assert isinstance(stg.rng, numpy.random.RandomState)

    def testMethodsBasic(self):

        stg = stgen.StGen()

        rate = 100.0 #Hz
        t_stop = 1000.0 # milliseconds
        st = stg.poisson_generator(rate,0.0,t_stop)

        assert isinstance(st,signals.SpikeTrain)

        st = stg.poisson_generator(rate,0.0,t_stop,array=True)

        assert isinstance(st, numpy.ndarray)

        st = stg.poisson_generator(rate,0.0,t_stop,array=True,debug=True)

        assert isinstance(st[0], numpy.ndarray)
        assert isinstance(st[1], list)

        st = stg.poisson_generator(rate,0.0,t_stop,debug=True)

        assert isinstance(st[0], signals.SpikeTrain)
        assert isinstance(st[1], list)

    def testStatsPoisson(self):
        # TODO: failing -- do something more robust than this.
        #       e.g., multiple runs, tolerance value.

        # this is a statistical test with non-zero chance of failure

        def test_poisson(rate,t_start,t_stop):
            stg = stgen.StGen()
            dt = t_stop-t_start
            N = rate*dt/1000.0

            st = stg.poisson_generator(rate,t_start=t_start,t_stop=t_stop,array=True)

            if len(st) in (0,1,2,3):
                assert N<15
                return



            assert st[-1] < t_stop
            assert st[0] > t_start


            # last spike should not be more than 4 ISI away from t_stop
            err = """
    Last spike should not be more than 4 ISI behind t_stop.
    There is a non-zero chance for this to occur during normal operation.
    Re-run the test to see if the error persists."""

            if st[-1] < t_stop-4.0*1.0/rate*1000.0:
                raise StatisticalError(err)


            # first spike should not be more than 4 ISI away from t_start
            err = """
    First spike should not be more than 4 ISI in front of t_start.
    There is a non-zero chance for this to occur during normal operation.
    Re-run the test to see if the error persists."""

            if st[0] > t_start+4.0*1.0/rate*1000.0:
                raise StatisticalError(err)

            err = """
    Number of spikes should be within 3 standard deviations of mean.
    There is a non-zero chance for this to occur during normal operation.
    Re-run the test to see if the error persists."""


            if len(st) > N+3.0*numpy.sqrt(N) or len(st) < N-3.0*numpy.sqrt(N):
                raise StatisticalError(err)


        # high rates

        test_poisson(100.0,500.0,1500.0)

        # high rates, short time

        test_poisson(100.0,500.0,550.0)

        # low rates, short time

        test_poisson(2.0,500.0,550.0)

        # low rates, long time

        test_poisson(5.0,500.0,50500.0)




    def testStatsInhPoisson(self):

        # this is a statistical test with non-zero chance of failure

        stg = stgen.StGen()

        rate = 100.0 #Hz
        t_start = 500.0
        t_stop = 1500.0 # milliseconds

        st = stg.inh_poisson_generator(numpy.array([rate]),numpy.array([t_start]),t_stop,array=True)

        assert st[-1] < t_stop
        assert st[0] > t_start


        # last spike should not be more than 4 ISI away from t_stop
        err = """
Last spike should not be more than 4 ISI behind t_stop.
There is a non-zero chance for this to occur during normal operation.
Re-run the test to see if the error persists."""

        if st[-1] < t_stop-4.0*1.0/rate*1000.0:
            raise StatisticalError(err)


        # first spike should not be more than 4 ISI away from t_start
        err = """
First spike should not be more than 4 ISI in front of t_start.
There is a non-zero chance for this to occur during normal operation.
Re-run the test to see if the error persists."""

        if st[0] > t_start+4.0*1.0/rate*1000.0:
            raise StatisticalError(err)

        err = """
Number of spikes should be within 3 standard deviations of mean.
There is a non-zero chance for this to occur during normal operation.
Re-run the test to see if the error persists."""

        # time interval is one second

        if len(st) > rate+3.0*numpy.sqrt(rate) or len(st) < rate-3.0*numpy.sqrt(rate):
            raise StatisticalError(err)


        # step in the rate

        st = stg.inh_poisson_generator(numpy.array([100.0,200.0]),numpy.array([500.0,1500.0]),2500.0,array=True)

        n1 = len(st[st<1500.0])
        n2 = len(st[st>1500.0])

        err = """
Number of spikes should be within 3 standard deviations of mean.
There is a non-zero chance for this to occur during normal operation.
Re-run the test to see if the error persists."""

        if n2 > 200.0+3.0*numpy.sqrt(200.0) or n2 < 200.0-3.0*numpy.sqrt(200.0):
            raise StatisticalError(err)
        
        if n1 > 100.0+3.0*numpy.sqrt(100.0) or n1 < 100.0-3.0*numpy.sqrt(100.0):
            raise StatisticalError(err)



    def testInhGammaBasic(self):

        from numpy import array
        import neurotools.signals

        stg = stgen.StGen()

        st = stg.inh_gamma_generator(array([3.0,3.0]),array([1.0/100.0/3.0,1.0/200.0/3.0]),array([500.0,1500.0]),2500.0,array=True)

        assert(type(st)==numpy.ndarray)

        st = stg.inh_gamma_generator(array([3.0,3.0]),array([1.0/100.0/3.0,1.0/200.0/3.0]),array([500.0,1500.0]),2500.0,array=False)

        assert(type(st)==neurotools.signals.spikes.SpikeTrain)



    def testStatsInhGamma(self):

        # this is a statistical test with non-zero chance of failure

        from numpy import array
        import neurotools.signals

        stg = stgen.StGen()

        # gamma step rate= 100Hz -> 200Hz, a = 3.0

        st = stg.inh_gamma_generator(array([3.0,3.0]),array([1.0/100.0/3.0,1.0/200.0/3.0]),array([500.0,1500.0]),2500.0,array=True)

        assert(type(st)==numpy.ndarray)

        
        n1 = len(st[st<1500.0])
        n2 = len(st[st>1500.0])

        err = """
Number of spikes should be within 3 standard deviations of mean.
There is a non-zero chance for this to occur during normal operation.
Re-run the test to see if the error persists."""

        if n2 > 200.0+3.0*numpy.sqrt(200.0) or n2 < 200.0-3.0*numpy.sqrt(200.0):
            raise StatisticalError(err)
        
        if n1 > 100.0+3.0*numpy.sqrt(100.0) or n1 < 100.0-3.0*numpy.sqrt(100.0):
            raise StatisticalError(err)


    def testStatsOUGen(self):

        # this is a statistical test with non-zero chance of failure

        from numpy import array

        stg = stgen.StGen()

        (ou,t) = stg.OU_generator(0.1,10.0,2.0,10.0,500.0,1500.0,array=True)



    def testInhAdaptingMarkov(self):


        stg = stgen.StGen()

        from numpy import array

        t = array([0.0,5000.0])
        # using parameters from paper
        a = array([23.18,47.24])
        bq = array([0.10912,0.09794])*14.48

        # expected mean firing rates for 2D case
        alpha = array([7.60, 10.66])

        tau = 110.0
        t_stop = 10000.0

        st = stg.inh_adaptingmarkov_generator(a,bq,tau,t,t_stop)
        assert isinstance(st,signals.SpikeTrain)

        st = stg.inh_adaptingmarkov_generator(a,bq,tau,t,t_stop,array=True)
        assert isinstance(st, numpy.ndarray)

        assert st[-1] < t_stop
        assert st[0] > t[0]


    def testInh2DAdaptingMarkov(self):


        stg = stgen.StGen()

        from numpy import array

        t = array([0.0,10000.0])
        # using parameters from paper
        a = array([23.18,47.24])
        bq = array([0.10912,0.09794])*14.48

        # expected mean firing rates for 2D case
        alpha = array([7.60, 10.66])

        tau_s = 110.0
        tau_r = 1.97
        qrqs = 221.96
        t_stop = 20000.0

        st = stg.inh_2Dadaptingmarkov_generator(a,bq,tau_s,tau_r,qrqs,t,t_stop)
        assert isinstance(st,signals.SpikeTrain)

        st = stg.inh_2Dadaptingmarkov_generator(a,bq,tau_s,tau_r,qrqs,t,t_stop,array=True)
        assert isinstance(st, numpy.ndarray)

        assert st[-1] < t_stop
        assert st[0] > t[0]

        spikes1 = len(st[st<10000])
        spikes2 = len(st[st>10000])
        
        # should be approximately alpha[0]*10.0 spikes
        assert numpy.clip(spikes1,60,100)==spikes1

        # should be approximately alpha[1]*10.0 spikes
        assert numpy.clip(spikes2,80,140)==spikes2


    def testShotNoiseFromSpikes(self):


        stg = stgen.StGen()

        from numpy import array

        st = stg.poisson_generator(10.0,0.0,1000.0)
        
        ge = stgen.shotnoise_fromspikes(st,2.0,10.0,dt=0.1)

        assert ge.t_start==0.0
        assert ge.t_stop==1000.0

        st = stg.poisson_generator(10.0,0.0,1000.0)
        ge = stgen.shotnoise_fromspikes(st,2.0,10.0,dt=0.1,t_start=500.0,t_stop=1500.0)
        
        assert ge.t_start==500.0
        assert ge.t_stop==1500.0

        


        
# ==============================================================================    
if __name__ == "__main__":
    unittest.main()
