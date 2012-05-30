#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
CRF_neuron_vs_signal.py

Testing the mean firing rate of a fiber for different signal strengths.
Prints to a figure the mean firing rate for the output (ON and OFF) as a function
of the different parameter values. It's similar to a CRF function.

Results illustrate that
- the higher the value the more the neuron spikes (wouah!),
- that this follows a ramp-type of function
- and that noise "smoothes" the  transition in theinput/output function.

TODO: do a better plot as in benchmark_neuron_vs_noise.py

$Id: CRF_neuron_vs_signal.py 362 2008-12-08 17:35:59Z LaurentPerrinet $
"""

import os, sys, numpy, pylab, shelve

from NeuroTools.parameters import *

# this is not mandatory but just a "easy_install progressbar" away
# else remove all corresponding 3 lines in this code...
import progressbar # see http://projects.scipy.org/pipermail/scipy-dev/2008-January/008200.html


N_exp_snr = 20
N_exp_noise = 9

ps =  ParameterSpace({
                'snr' : ParameterRange(list(numpy.linspace(-1.,4.,N_exp_snr))),
                'noise_std' : ParameterRange(list(10.**(numpy.linspace(-.50,1.,N_exp_noise))))})


name = sys.argv[0].split('.')[0] # name of the current script withpout the '.py' part
results = shelve.open('results/mat-' + name)
try:
    CRF = results['CRF']
except:

    # calculates the dimension of the parameter space
    results_dim, results_label = ps.parameter_space_dimension_labels()

    # creates results array with size of parameter space dimension
    import simple_single_neuron as model
    myFibers = model.FiberChannel()
    CRF = numpy.empty(results_dim)

    pbar=progressbar.ProgressBar(widgets=[name, " ", progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ', progressbar.ETA()], maxval=numpy.prod(results_dim))
    for i_exp,experiment in enumerate(ps.iter_inner()):
        params = myFibers.params
        params.update(experiment) # updates what changed in the dictionary
        # simulate the experiment and get its data
        data = myFibers.run(params,verbose=False)
        # calculating the index in the parameter space
        index = ps.parameter_space_index(experiment)
        # put the data at the right position in the results array
        CRF[index] = data.mean_rate()#
        pbar.update(i_exp)

    results['CRF'] = CRF
    pbar.finish()

results.close()

#numpy.array(p.noise_std._values),numpy.array(p.snr._values),
#pylab.plot(ps.snr._values,CRF.transpose()) #color = (sin(2*pi*noise_list)**2,cos(2*pi*noise_list)**2,1))
for i_noise, noise in enumerate(ps.noise_std._values):
    pylab.plot(ps.snr._values,CRF[i_noise,:], label='noise = %5.3f' % noise)
#pylab.yticks(p.noise_std._values[:2:])
pylab.ylabel('Firing Rate (Hz/neuron)')
#pylab.xticks(p.snr._values[:2:])
pylab.xlabel('Signal')
pylab.legend(loc = 'lower right')
pylab.axis([numpy.min(ps.snr._values), numpy.max(ps.snr._values), 0.0, numpy.max(CRF[:])])
if 0:
    pylab.show()
else:
    pylab.savefig('results/fig-' + name + '.pdf')
    pylab.savefig('results/fig-' + name + '.png')
