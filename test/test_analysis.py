"""
Unit tests for the NeuroTools.analysis module
"""
import numpy
import scipy.io
import unittest
from numpy import pi, sin

from NeuroTools import analysis, signals

# test simple_frequency_spectrum


class AnalysisTest(unittest.TestCase):

    def setUp(self):
        #The following are used for the make_kernel testcases
        self.box = scipy.io.loadmat('analysis/make_kernel/box.mat')
        self.tri = scipy.io.loadmat('analysis/make_kernel/tri.mat')
        self.epa = scipy.io.loadmat('analysis/make_kernel/epa.mat')
        self.gau = scipy.io.loadmat('analysis/make_kernel/gau.mat')
        self.alp = scipy.io.loadmat('analysis/make_kernel/alp.mat')
        self.exp = scipy.io.loadmat('analysis/make_kernel/exp.mat')
        self.alp_reversed = scipy.io.loadmat(
            'analysis/make_kernel/alp_reversed.mat')
        self.exp_reversed = scipy.io.loadmat(
            'analysis/make_kernel/exp_reversed.mat')
        
        #Used for the testcases of the crosscorrelate function
        spk = signals.load_spikelist('analysis/crosscorrelate/spike_data')
        self.spk0 = spk[0]
        self.spk1 = spk[1]

    def testSimpleFrequencySpectrum(self):
        
        ph = [0.5*pi, 1.2*pi, 0.3*pi]
        x = lambda A, ph, f, t: A[0] + A[1]*sin(2*pi*f/1000.0*t + ph[0]) + A[2]*sin(2*pi*2*f/1000.0*t + ph[1]) + A[3]*sin(2*pi*3*f/1000.0*t + ph[2])
        durations = [10.0, 10.0, 30.0]
        binwidths = [1.0, 5.0, 10.0]
        
        for i in range(10):
            A = numpy.random.uniform(-10, 10, size=4)
            #print A
            for f in 0.5, 1.0, 2.0, 10.0, 99.0: # cycles/sec
                for duration, binwidth in zip(durations, binwidths):
                    if 3*f < 1000.0/binwidth: # binwidth limits the max frequency
                        X = x(A, ph, f, numpy.arange(0, duration*1000.0, binwidth))
                        spect = analysis.simple_frequency_spectrum(X)
                        samples = numpy.array([0, 1, 2, 3])*int(f*duration)
                        components = spect[samples]
                        #print f, duration, binwidth, components
                        assert numpy.all(abs(abs(A) - components) < 1e-13), abs(A)-components

    def testCCF(self):
        a=numpy.arange(1000)
        z=analysis.ccf(a,a)
        assert z[len(z)/2] == 1
    
    def testMakeKernelBox(self):
        true_kernel = self.box['kernel'].ravel()
        true_norm = self.box['norm'].ravel()[0]
        true_m_idx = self.box['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('BOX', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testMakeKernelTri(self):
        true_kernel = self.tri['kernel'].ravel()
        true_norm = self.tri['norm'].ravel()[0]
        true_m_idx = self.tri['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('TRI', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testMakeKernelEpa(self):
        true_kernel = self.epa['kernel'].ravel()
        true_norm = self.epa['norm'].ravel()[0]
        true_m_idx = self.epa['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('EPA', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testMakeKernelGau(self):
        true_kernel = self.gau['kernel'].ravel()
        true_norm = self.gau['norm'].ravel()[0]
        true_m_idx = self.gau['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('GAU', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testMakeKernelAlp(self):
        true_kernel = self.alp['kernel'].ravel()
        true_norm = self.alp['norm'].ravel()[0]
        true_m_idx = self.alp['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('ALP', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)

    def testMakeKernelExp(self):
        true_kernel = self.exp['kernel'].ravel()
        true_norm = self.exp['norm'].ravel()[0]
        true_m_idx = self.exp['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('EXP', 1, 0.001)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
    
    def testMakeKernelAlpReversed(self):
        """Same as testAlp but with direction = -1
        """
        true_kernel = self.alp_reversed['kernel'].ravel()
        true_norm = self.alp_reversed['norm'].ravel()[0]
        true_m_idx = self.alp_reversed['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('ALP', 1, 0.001,
                                                  direction = -1)
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testMakeKernelExpReversed(self):
        """Same as testExp but with direction = -1
        """
        true_kernel = self.exp_reversed['kernel'].ravel()
        true_norm = self.exp_reversed['norm'].ravel()[0]
        true_m_idx = self.exp_reversed['m_idx'].ravel()[0] - 1
        
        kernel, norm, m_idx = analysis.make_kernel('EXP', 1, 0.001, direction = -1)
        
        numpy.testing.assert_array_almost_equal(true_kernel, kernel, decimal = 3
                                                )
        self.assertEqual(true_norm, norm, 3)
        self.assertEqual(true_m_idx, m_idx, 3)
        
    def testCrosscorrelateNoLag(self):
            int, int_, norm = analysis.crosscorrelate(self.spk0, self.spk1)
            #The following are output was generated with the FIND MATLAB toolbox
            matlab_int = numpy.loadtxt('analysis/crosscorrelate/out_matlab_int')
            numpy.testing.assert_array_almost_equal(int, matlab_int,
                                                    decimal=3)
            #The int_ output has a random component and for this reason the test
            # cases are not as trivial
            
    def testCrosscorrelateLag100(self):
        """Test case with lag within the length of the input array
        """
        int, int_, norm, = analysis.crosscorrelate(self.spk0, self.spk1,
                                                   lag=100.0)
        matlab_int = numpy.loadtxt('analysis/crosscorrelate/out_matlab_int_lag_100')
        numpy.testing.assert_array_almost_equal(int, matlab_int, decimal = 3)
            
    def testCrosscorrelateLag500(self):
        """Test case with lag is higher than the trial length
        """
        int, int_, norm = analysis.crosscorrelate(self.spk0, self.spk1,
                                                  lag=500.0)
        matlab_int = numpy.loadtxt('analysis/crosscorrelate/out_matlab_int_lag_500')
        numpy.testing.assert_array_almost_equal(int, matlab_int, decimal = 3)
            
if __name__ == "__main__":
    unittest.main()
