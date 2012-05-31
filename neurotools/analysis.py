# -*- coding: utf8 -*-
"""
NeuroTools.analysis
==================

A collection of analysis functions that may be used by NeuroTools.signals or other packages.

Classes
-------

TuningCurve - A tuning curve object (not very documented)


Functions
---------

ccf                       - fast cross correlation function based on fft
crosscorrelate            - cross-correlation between two series of discrete
                            events (e.g. spikes)
simple_frequency_spectrum - Simple frequencxy spectrum
arrays_almost_equal       - comparison of two arrays
make_kernel               - creates kernel functions for convolution
"""

import os

import numpy

from NeuroTools import check_dependency

HAVE_PYLAB = check_dependency('pylab')
HAVE_MATPLOTLIB = check_dependency('matplotlib')
if HAVE_PYLAB:
    import pylab
else:
    PYLAB_ERROR = "The pylab package was not detected"
if not HAVE_MATPLOTLIB:
    MATPLOTLIB_ERROR = "The matplotlib package was not detected"


def arrays_almost_equal(a, b, threshold):
    return (abs(a-b) < threshold).all()

def ccf(x, y, axis=None):
    """
    Computes the cross-correlation function of two series x and y.
    Note that the computations are performed on anomalies (deviations from
    average).
    Returns the values of the cross-correlation at different lags.
        
    Inputs:
        x    - 1D MaskedArray of a Time series.
        y    - 1D MaskedArray of a Time series.
        axis - integer *[None]* Axis along which to compute (0 for rows, 1 for cols).
               If `None`, the array is flattened first.
    
    Examples:
        >> z= arange(1000)
        >> ccf(z,z)

    """
    assert x.ndim == y.ndim, "Inconsistent shape !"
#    assert(x.shape == y.shape, "Inconsistent shape !")
    if axis is None:
        if x.ndim > 1:
            x = x.ravel()
            y = y.ravel()
        npad = x.size + y.size
        xanom = (x - x.mean(axis=None))
        yanom = (y - y.mean(axis=None))
        Fx = numpy.fft.fft(xanom, npad, )
        Fy = numpy.fft.fft(yanom, npad, )
        iFxy = numpy.fft.ifft(Fx.conj()*Fy).real
        varxy = numpy.sqrt(numpy.inner(xanom,xanom) * numpy.inner(yanom,yanom))
    else:
        npad = x.shape[axis] + y.shape[axis]
        if axis == 1:
            if x.shape[0] != y.shape[0]:
                raise ValueError, "Arrays should have the same length!"
            xanom = (x - x.mean(axis=1)[:,None])
            yanom = (y - y.mean(axis=1)[:,None])
            varxy = numpy.sqrt((xanom*xanom).sum(1) * (yanom*yanom).sum(1))[:,None]
        else:
            if x.shape[1] != y.shape[1]:
                raise ValueError, "Arrays should have the same width!"
            xanom = (x - x.mean(axis=0))
            yanom = (y - y.mean(axis=0))
            varxy = numpy.sqrt((xanom*xanom).sum(0) * (yanom*yanom).sum(0))
        Fx = numpy.fft.fft(xanom, npad, axis=axis)
        Fy = numpy.fft.fft(yanom, npad, axis=axis)
        iFxy = numpy.fft.ifft(Fx.conj()*Fy,n=npad,axis=axis).real
    # We juste turn the lags into correct positions:
    iFxy = numpy.concatenate((iFxy[len(iFxy)/2:len(iFxy)],iFxy[0:len(iFxy)/2]))
    return iFxy/varxy

from NeuroTools.plotting import get_display, set_labels

HAVE_PYLAB = check_dependency('pylab')


def crosscorrelate(sua1, sua2, lag=None, n_pred=1, predictor=None,
                   display=False, kwargs={}):
    """
    Calculates the cross-correlation between two vectors containing event times.
    Returns (int, int_, norm). See below for details.
    
    Adapted from original script written by Martin P. Nawrot for the FIND MATLAB
    toolbox.
    See FIND - a unified framework for neural data analysis,
        Meier R, Egert U, Aertsen A, Nawrot MP; Neural Netw. 2008 Oct;
        21(8):1085-93. 
     
    Inputs:
        sua1      - array of event times. Can be either a column/row vector or a
                    member of the SpikeTrain class.
        sua2      - array of event times. Can be either a column/row vector or a
                    member of the SpikeTrain class.
                    If sua2 == sua1 the result is the
                    autocorrelogram.
        lag       - the max. lag for which relative event timing is considered
                    with a max. difference of +/- lag. A default lag is computed
                    from the inter-event interval of the longer of the two sua
                    arrays 
        n_pred    - number of surrogate compilations for the predictor. This
                    influences the total length of the predictor output array
                    int_
        predictor - string array determines the type of bootstrap predictor to
                    be used:
                        shuffle - shuffles inter-event intervals of the longer
                                  input array and calculates relative
                                  differences with the shorter input array.
                                  n_pred determines the number of repeated
                                  shufflings, resulting differences are pooled
                                  from all repeated shufflings
        display   - if True the corresponding plots will be displayed. If False,
                    int, int_ and norm will be returned.
                    when display = True and n_pred > 1, the averaged predictor
                    will be plotted.
        kwargs    - arguments to be passed to numpy.histogram.

    Outputs:
        int  - accumulated differences of events in sua1 minus the events in
               sua2. Thus positive values of int relate to events of sua2 that
               lead events of sua1. Units are the same as the input arrays.
        int_ - predictor: accumulated differences based on the prediction
               method. The length of int_ is n_pred * length(int).  Units are
               the same as the input arrays.
        norm - normalization factor used to scale the bin heights in int and
               int_. int/norm and int_/norm correspond to the linear
               correlation coefficient.
    
    Examples:
        >> crosscorrelate(numpy_array1, numpy_array2)
        >> crosscorrelate(spike_train1, spike_train2)
        >> crosscorrelate(spike_train1, spike_train2, lag = 150.0)
        >> crosscorrelate(spike_train1, spike_train2, display=True,
                          kwargs={'bins':100})
            
    See also:
        ccf
    """    
    assert predictor is 'shuffle' or predictor is None, "predictor must be \
    either None or 'shuffle'. Other predictors are not yet implemented."
    
    #Check whether sua1 and sua2 are SpikeTrains or arrays
    sua = []
    for x in (sua1, sua2):
        #if isinstance(x, SpikeTrain):
        if hasattr(x, 'spike_times'):
            sua.append(x.spike_times)
        elif x.ndim == 1:
            sua.append(x)
        elif x.ndim == 2 and (x.shape[0] == 1 or x.shape[1] == 1):
            sua.append(x.ravel())
        else:
            raise TypeError("sua1 and sua2 must be either instances of the" \
                            "SpikeTrain class or column/row vectors")
    sua1 = sua[0]
    sua2 = sua[1]
    
    if sua1.size < sua2.size:
        if lag is None:
            lag = numpy.ceil(10*numpy.mean(numpy.diff(sua1)))
        reverse = False
    else:
        if lag is None:
            lag = numpy.ceil(20*numpy.mean(numpy.diff(sua2)))
        sua1, sua2 = sua2, sua1
        reverse = True
            
    #construct predictor
    if predictor is 'shuffle':
        isi = numpy.diff(sua2)
        sua2_ = numpy.array([])
        for ni in xrange(1,n_pred+1):
            idx = numpy.random.permutation(isi.size-1)            
            sua2_ = numpy.append(sua2_, numpy.add(numpy.insert(
                (numpy.cumsum(isi[idx])), 0, 0), sua2.min() + (
                numpy.random.exponential(isi.mean()))))
            
    #calculate cross differences in spike times
    int = numpy.array([])
    int_ = numpy.array([])
    for k in xrange(0, sua1.size):
        int = numpy.append(int, sua1[k] - sua2[numpy.nonzero(
            (sua2 > sua1[k] - lag) & (sua2 < sua1[k] + lag))])
    if predictor == 'shuffle':
        for k in xrange(0, sua1.size):
            int_ = numpy.append(int_, sua1[k] - sua2_[numpy.nonzero(
                (sua2_ > sua1[k] - lag) & (sua2_ < sua1[k] + lag))])
    if reverse is True:
        int = -int
        int_ = -int_
        
    norm = numpy.sqrt(sua1.size * sua2.size)
    
    # Plot the results if display=True   
    if display:
        subplot = get_display(display)
        if not subplot or not HAVE_PYLAB:
            return int, int_, norm
        else:
            # Plot the cross-correlation
            try:
                counts, bin_edges = numpy.histogram(int, **kwargs)
                edge_distances = numpy.diff(bin_edges)
                bin_centers = bin_edges[1:] - edge_distances/2
                counts = counts / norm
                xlabel = "Time"
                ylabel = "Cross-correlation coefficient"
                #NOTE: the x axis corresponds to the upper edge of each bin
                subplot.plot(bin_centers, counts, label='cross-correlation', color='b')
                if predictor is None:
                    set_labels(subplot, xlabel, ylabel)
                    pylab.draw()
                elif predictor is 'shuffle':            
                    # Plot the predictor
                    norm_ = norm * n_pred
                    counts_, bin_edges_ = numpy.histogram(int_, **kwargs)
                    counts_ = counts_ / norm_
                    subplot.plot(bin_edges_[1:], counts_, label='predictor')
                    subplot.legend()
                    pylab.draw()
            except ValueError:
                print "There are no correlated events within the selected lag"\
                " window of %s" % lag
    else:
        return int, int_, norm
    
def _dict_max(D):
    """
    For a dict containing numerical values, contain the key for the
    highest value. If there is more than one item with the same highest
    value, return one of them (arbitrary - depends on the order produced
    by the iterator).
    """
    max_val = max(D.values())
    for k in D:
        if D[k] == max_val:
            return k
        
def make_kernel(form, sigma, time_stamp_resolution, direction=1):
    """
    Constructs a numeric linear convolution kernel of basic shape to be used
    for data smoothing (linear low pass filtering) and firing rate estimation
    from single trial or trial-averaged spike trains.
    
    Exponential and alpha kernels may also be used to represent postynaptic
    currents / potentials in a linear (current-based) model.
    
    Adapted from original script written by Martin P. Nawrot for the FIND MATLAB
    toolbox.
    See FIND - a unified framework for neural data analysis,
        Meier R, Egert U, Aertsen A, Nawrot MP; Neural Netw. 2008 Oct;
        21(8):1085-93. 
        
        Nawrot M, Aertsen A, Rotter S (1999)
        Single-trial estimation of neuronal firing rates - From single neuron
        spike trains to population activity.
        J Neurosci Meth 94: 81-92
        
    Inputs:
        form                  - kernel form (string) Currently implemented forms
                                are BOX - boxcar, TRI - triangle, GAU - gaussian
                                , EPA - epanechnikov, EXP - exponential, ALP -
                                alpha function.
                                EXP and ALP are aymmetric kernel forms and
                                assume optional parameter 'direction'
        sigma                 - standard deviation of the distribution
                                associated with kernel shape. This parameter
                                defines the time resolution of the kernel
                                estimate and makes different kernels comparable
                                (cf. [1] for symetric kernels). This is used
                                here as an alternative definition to the cut-off
                                frequency of the associated linear filter.
        time_stamp_resolution - temporal resolution of input and output in ms
        direction             - Asymmetric kernels have two possible directions.
                                The values are -1 or 1, default is 1. The
                                definition here is that for direction = 1 the
                                kernel represents the impulse response function
                                of the linear filter. Default value is 1.
    
    Outputs:
        kernel  - array of kernel. The length of this array is always an odd
                  number to represent symmetric kernels such that the center bin
                  coincides with the median of the numeric array, i.e for a
                  triangle, the maximum will be at the center bin with equal
                  number of bins to the right and to the left.
        norm    - for rate estimates. The kernel vector is normalized such that
                  the sum of all entries equals unity sum(kernel)=1. When
                  estimating rate functions from discrete spike data (0/1) the
                  additional parameter 'norm' allows for the normalization to
                  rate in spikes per second.
                  Use: rate = norm * scipy.signal.lfilter(kernel, 1, spike_data)
        m_idx   - index of the numerically determined median (center of gravity)
                  of the kernel function
                  
    Further comments:
    
    Assume matrix X of n spike trains represented as binary vector (0/1).
    
    To obtain single trial rate function of trial one should use
        r = norm * scipy.signal.fftconvolve(sua, kernel)
    To obtain trial-averaged spike train one should use
        r_avg = norm * scipy.signal.fftconvolve(sua, numpy.mean(X,1))
        
        where X is an array of shape (l,n), where n is the number of trials and
        l the length of each trial
    
    Note that the output of scipy.signal.fftconvolve needs to trimmed acordingly
    before being displayed. For more information see the source of the method
    SpikeTrain.instantaneous_rate()
    
    See also:
        SpikeTrain.instantaneous_rate, SpikeList.averaged_instantaneous_rate
    """
    assert form.upper() in ('BOX','TRI','GAU','EPA','EXP','ALP'), "form must \
    be one of either 'BOX','TRI','GAU','EPA','EXP' or 'ALP'!"
    
    assert direction in (1,-1), "direction must be either 1 or -1"
    
    sigma = sigma / 1000. #convert to SI units
    
    time_stamp_resolution = time_stamp_resolution / 1000. #convert to SI units
    
    norm = 1./time_stamp_resolution

    if form.upper() == 'BOX':
        w = 2.0 * sigma * numpy.sqrt(3)
        width = 2 * numpy.floor(w / 2.0 / time_stamp_resolution) + 1  # always odd number of bins
        height = 1. / width
        kernel = numpy.ones((1, width)) * height  # area = 1
        
    elif form.upper() == 'TRI':
        w = 2 * sigma * numpy.sqrt(6)
        halfwidth = numpy.floor(w / 2.0 / time_stamp_resolution)
        trileft = numpy.arange(1, halfwidth + 2)
        triright = numpy.arange(halfwidth, 0, -1)  # odd number of bins
        triangle = numpy.append(trileft, triright)
        kernel = triangle / triangle.sum()  # area = 1
        
    elif form.upper() == 'EPA':
        w = 2.0 * sigma * numpy.sqrt(5)
        halfwidth = numpy.floor(w / 2.0 / time_stamp_resolution)
        base = numpy.arange(-halfwidth, halfwidth + 1)
        parabula = base**2
        epanech = parabula.max() - parabula  # inverse parabula
        kernel = epanech / epanech.sum()  # area = 1
        
    elif form.upper() == 'GAU':
        SI_sigma = sigma / 1000.0
        w = 2.0 * sigma * 2.7  # > 99% of distribution weight
        halfwidth = numpy.floor(w / 2.0 / time_stamp_resolution)  # always odd 
        base = numpy.arange(-halfwidth, halfwidth + 1) / 1000.0 * (
            time_stamp_resolution)
        g = numpy.exp(-(base**2) / 2.0 / SI_sigma**2) / SI_sigma / numpy.sqrt(
            2.0 * numpy.pi)
        kernel = g / g.sum()
        
    elif form.upper() == 'ALP':
        SI_sigma = sigma / 1000.0
        w = 5.0 * sigma
        alpha = numpy.arange(1, (2.0 * numpy.floor(
            (w / time_stamp_resolution / 2.0)) + 1) + 1) / 1000.0 * \
        time_stamp_resolution
        alpha = (2.0 / SI_sigma**2) * alpha * numpy.exp(-alpha * numpy.sqrt(2) \
                                                        / SI_sigma)
        kernel = alpha / alpha.sum()  # normalization
        if direction == -1:
            kernel = numpy.flipud(kernel)
            
    elif form.upper() == 'EXP':
        SI_sigma = sigma / 1000.0
        w = 5.0 * sigma
        expo = numpy.arange(1, (2.0 * numpy.floor(w / time_stamp_resolution / (
            2.0)) + 1) + 1) / 1000.0 * time_stamp_resolution
        expo = numpy.exp(-expo / SI_sigma)
        kernel = expo / expo.sum()
        if direction == -1:
            kernel = numpy.flipud(kernel)
    
    kernel = kernel.ravel()
    m_idx = numpy.nonzero(kernel.cumsum() >= 0.5)[0].min()
    
    return kernel, norm, m_idx

def simple_frequency_spectrum(x):
    """
    Very simple calculation of frequency spectrum with no detrending,
    windowing, etc. Just the first half (positive frequency components) of
    abs(fft(x))
    """
    spec = numpy.absolute(numpy.fft.fft(x))
    spec = spec[:len(x)/2] # take positive frequency components
    spec /= len(x)         # normalize
    spec *= 2.0            # to get amplitudes of sine components, need to multiply by 2
    spec[0] /= 2.0         # except for the dc component
    return spec

class TuningCurve(object):
    """Class to facilitate working with tuning curves."""

    def __init__(self, D=None):
        """
        If `D` is a dict, it is used to give initial values to the tuning curve.
        """
        self._tuning_curves = {}
        self._counts = {}
        if D is not None:
            for k,v in D.items():
                self._tuning_curves[k] = [v]
                self._counts[k] = 1
                self.n = 1
        else:
            self.n = 0

    def add(self, D):
        for k,v  in D.items():
            self._tuning_curves[k].append(v)
            self._counts[k] += 1
        self.n += 1

    def __getitem__(self, i):
        D = {}
        for k,v in self._tuning_curves[k].items():
            D[k] = v[i]
        return D
    
    def __repr__(self):
        return "TuningCurve: %s" % self._tuning_curves

    def stats(self):
        """Return the mean tuning curve with stderrs."""
        mean = {}
        stderr = {}
        n = self.n
        for k in self._tuning_curves.keys():
            arr = numpy.array(self._tuning_curves[k])
            mean[k] = arr.mean()
            stderr[k] = arr.std()*n/(n-1)/numpy.sqrt(n)
        return mean, stderr

    def max(self):
        """Return the key of the max value and the max value."""
        k = _dict_max(self._tuning_curves)
        return k, self._tuning_curves[k]
