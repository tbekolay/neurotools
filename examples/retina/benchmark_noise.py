#!/usr/bin/env python
#-*- coding: utf8 -*-
"""
benchmark_noise.py
==================

Just studying how different background noise current are integrated by the
neurons on the retinal fibers.

Illustrates how one many use parameters to explore one set of parameters and
compute a CRF function. See benchmark_linear to store time varrying values.

Laurent Perrinet, INCM, CNRS

$ Id $

"""

import os, sys, numpy, shelve

N, N_exp_noise = 1000, 22
from NeuroTools.parameters import *
p =  ParameterSpace({'noise_std' : ParameterRange(list(10.**(numpy.linspace(-.50,1.,N_exp_noise))))})

name = sys.argv[0].split('.')[0] # name of the current script withpout the '.py' part
results = shelve.open('results/mat-' + name)
try:
    CRF = results['CRF']
except:
    # this is not mandatory but just a "easy_install progressbar" away
    # else remove all corresponding lines in this code...
    import progressbar # see http://projects.scipy.org/pipermail/scipy-dev/2008-January/008200.html
    import retina as model
    retina = model.Retina(N) 
    retina.params['snr'] = 0 # no input
    
    # calculates the dimension of the parameter space
    results_dim, results_label = p.parameter_space_dimension_labels()

    # creates results array with size of parameter space dimension
    CRF = numpy.empty(results_dim)

    pbar=progressbar.ProgressBar(widgets=[name, " ", progressbar.Percentage(), ' ',
            progressbar.Bar(), ' ', progressbar.ETA()], maxval=numpy.prod(results_dim))
    for i_exp,experiment in enumerate(p.iter_inner()):
        params = retina.params
        params.update(experiment) # updates what changed in the dictionary
        # simulate the experiment and get its data
        data = retina.run(params,verbose=False)
        # calculating the index in the parameter space
        index = p.parameter_space_index(experiment)
        # put the data at the right position in the results array
        CRF[index] = data['out_ON_DATA'].mean_rate()#
        pbar.update(i_exp)

    results['CRF'] = CRF

    pbar.finish()

results.close()

from NeuroTools.plotting import pylab_params

""" Figure 1

Prints to a figure the mean firing rate for the output (ON and OFF) as a function of the different parameter values. It's similar to a CRF function.

TODO put standard deviation of activity, print CV

"""

import pylab

pylab.figure(num = 1)

pylab.plot(p.noise_std._values,CRF,'go-', label='line 1', linewidth=2)
pylab.ylabel('Firing Frequency (Hz)')
pylab.xlabel('Noise amplitude')


if 0:
    pylab.show()
else:
    pylab.savefig('results/fig-' + name + '.pdf')
    pylab.savefig('results/fig-' + name + '.png', dpi = 300)


#TODO: make a plot showing that spontaneous activity is a point process with a known histogram