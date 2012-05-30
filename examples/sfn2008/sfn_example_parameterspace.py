"""
$Id: sfn_example_parameterspace.py 350 2008-11-16 00:51:40Z mschmucker $

Example to show off some capabilities of the parameters module.

- creates a ParameterSpace of c and jitter for the example shown in 
  sfn_example_stgen.py
- the parameters c and jitter are scanned and the cc and the corrcoef 
  are calculated
- all the cc's are plotted

Performed at the NeuroTools demo session, INCF booth, 
SfN annual meeting 2008, Washington. DC.
"""
import numpy, pylab

import NeuroTools.stgen as stgen
sg = stgen.StGen()

from NeuroTools.parameters import ParameterSpace
from NeuroTools.parameters import ParameterRange
from NeuroTools.sandbox import make_name

# creating a ParameterSpace
p = ParameterSpace({})

# adding fixed parameters
p.nu = 20. # rate [Hz]
p.duration = 1000.

# adding ParameterRanges
p.c = ParameterRange([0.0,0.01,0.1,0.5])
p.jitter = ParameterRange([0.0,1.0,5.0,])

# calculation of the ParameterSpace dimension and the labels of the parameters
# containing a range
dims, labels = p.parameter_space_dimension_labels()
print "dimensions: ", dims
print ' labels: ', labels

def calc_cc(p):
    """
    Generate correlated spike trains from the ParameterSet.
    
    Parameter:
    p - ParameterSet containing parameters nu (rate), c (correlation),
        duration (in ms), jitter (in ms).
        
    Returns: (cc, time_axis_cc, corrcoef)
    cc - correlation coefficient
    time_axis_cc - time axis for cross-correlation (for plotting)
    corrcoef - correlation coefficient between the two SpikeTrains
    """
    rate_independent = (1-p.c)*p.nu
    rate_shared = p.c*p.nu
    
    st1 = sg.poisson_generator(rate=rate_independent, t_stop = p.duration) 
    st2 = sg.poisson_generator(rate=rate_independent, t_stop = p.duration)
    if p.c > 0.:
        st3 = sg.poisson_generator(rate=rate_shared, t_stop = p.duration) 
        st1.merge(st3.jitter(p.jitter))
        st2.merge(st3.jitter(p.jitter))
    
    cc = numpy.correlate(st1.time_histogram(time_bin = 1.0),
                         st2.time_histogram(time_bin = 1.),mode = 'same')
    corrcoef = numpy.corrcoef(st1.time_histogram(time_bin = 1.0),
                              st2.time_histogram(time_bin = 1.))
    time_axis_cc = numpy.linspace(-cc.shape[0]/2.,cc.shape[0]/2.,cc.shape[0])
    return cc, time_axis_cc, corrcoef[0][1]


# creating a results array, with the dimensions of the ParameterSpace
corrcoef_results = numpy.empty(dims)

# scanning the ParameterSpace
for experiment in p.iter_inner():
    # calculation of the index in the space
    index = p.parameter_space_index(experiment)
    # perfomring the experiment
    cc,time_axis_cc, corrcoef = calc_cc(experiment)
    corrcoef_results[index] = corrcoef
    # plotting the cc's
    subplot_index = (dims[1]*index[0])+index[1]
    pylab.subplot(dims[0],dims[1],subplot_index+1)
    pylab.plot(time_axis_cc,cc)
    pylab.title(make_name(experiment,p.range_keys()))
    pylab.xlim(-30,30.)
    pylab.ylim(0,10.)


# plot the results
pylab.matshow(corrcoef_results)
pylab.xticks(numpy.arange(0.5,dims[1]+0.5,1.0),[str(i) for i in p.jitter._values])
pylab.yticks(numpy.arange(0.5,dims[0]+0.5,1.0),[str(i) for i in p.c._values])
pylab.xlim(0,dims[1])
pylab.ylim(dims[0],0)
pylab.xlabel('jitter (ms)')
pylab.ylabel('correlation')
ax = pylab.colorbar()
ax.set_label('correlation')
pylab.draw()

