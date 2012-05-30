#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
benchmark_retina.py
===================

This should feed the "Hyper-Column" for benchmark one.
(see https://facets.kip.uni-heidelberg.de/private/wiki/index.php/V1_hypercolumn#Benchmark_one )

The input is a discrete dirac simulating the response in Magnocellular Pathway
M to primary visual cortex' layer 4C$\alpha$ then to 4B as defined in Benchmark
one. The paramters tested is SNR sensitivity / spatial stability of V1 response.


Illustrates how one many use parameters to explore different sets of parameters
and compute their effect. See benchmark_noise and benchmark_linear for simpler
examples.

Laurent Perrinet, INCM, CNRS

$ Id $

"""

import os, sys, numpy, pylab, shelve, progressbar

N, N_snr, N_seeds = 1000, 5, 10
from NeuroTools.parameters import *
p =  ParameterSpace({
                'snr' : ParameterRange(list(numpy.linspace(0.5,4.0,N_snr))),
                'kernelseed' : ParameterRange(list([12345 + k for k in range(N_seeds)]))})

name = sys.argv[0].split('.')[0] # name of the current script withpout the '.py' part

try:
    ############## MAKING THE SIMULATIONS ###############
    results = shelve.open('results/mat-' + name)
    try:
        DATA = results['DATA']
        params = results['params']
    except:
        from retina import *
        retina = Retina(N)
        # calculates the dimension of the parameter space
        results_dim, results_label = p.parameter_space_dimension_labels()

        DATA = []
        pbar=progressbar.ProgressBar(widgets=[name, " ", progressbar.Percentage(), ' ',
                progressbar.Bar(), ' ', progressbar.ETA()], maxval=N_snr*N_seeds)
        for i_exp, experiment in enumerate(p.iter_inner()):
            params = retina.params
            params.update(experiment) # updates what changed in the dictionary
            # simulate the experiment and get its data
            data = retina.run(params)#,verbose=False)
            # store it
            DATA.append(data)#
            pbar.update(i_exp)

        results['DATA'] = DATA
        results['params'] = retina.params

        pbar.finish()
    results.close()
    results = shelve.open('results/mat-pre-' + name)
    ############## PRE-PROCESSING ###########################
    #boing # uncomment to force recomputing the pre-processing stage
    lower_edges = results['lower_edges']
    temporal_ON = results['temporal_ON']
    map_spatial_OFF = results['map_spatial_OFF']
    temporal_OFF = results['temporal_OFF']
    map_spatial_ON = results['map_spatial_ON']
    lower_edges = results['lower_edges']
    results.close()

except:
    def temporal_mean(spike_list):
        return numpy.sum(spike_list.firing_rate(t_smooth),axis=0)
        
    t_smooth = 100. # ms.  integration time to show fiber activity
    lower_edges = DATA[0]['out_ON_DATA'].time_axis(t_smooth)
    N_smooth = len(lower_edges)-1

    #N_snr = len(p.snr)
    temporal_ON, temporal_OFF = numpy.zeros((N_smooth,N_snr)), numpy.zeros((N_smooth,N_snr))
    map_spatial_ON, map_spatial_OFF  = numpy.zeros((N,N_snr)), numpy.zeros((N,N_snr))

    #
    N_ret, simtime = params['N_ret'], params['simtime']
    x = params['position'][0]
    y = params['position'][1]
    r2 = x**2 + y**2
    r = numpy.sqrt(r2)
    id_center = [int(k) for k in numpy.where( r2 < N_ret**2)[0]]
    # mean activity accross kernelseeds as a function of SNR
    for i_exp, experiment in enumerate(p.iter_inner()):
        # calculating the index in the parameter space
        index = p.parameter_space_index(experiment)
        # getting SpikeLists corresponding to the interesting parts (within the center)
        temporal_ON[:,index[1]] += temporal_mean(DATA[i_exp]['out_ON_DATA'].id_slice(id_center))/N_seeds
        temporal_OFF[:,index[1]] += temporal_mean(DATA[i_exp]['out_ON_DATA'].id_slice(id_center))/N_seeds
        map_spatial_ON[:,index[1]] += DATA[i_exp]['out_ON_DATA'].mean_rates(t_start=simtime/4.,t_stop=3*simtime/4.)#/N_seeds
        map_spatial_OFF[:,index[1]] += DATA[i_exp]['out_OFF_DATA'].mean_rates(t_start=simtime/4.,t_stop=3*simtime/4.)#/N_seeds

    results = shelve.open('results/mat-pre-' + name)
    results['temporal_ON'] = temporal_ON
    results['map_spatial_OFF'] = map_spatial_OFF
    results['temporal_OFF'] = temporal_OFF
    results['map_spatial_ON'] = map_spatial_ON
    results['lower_edges'] = lower_edges
    results.close()

results.close()

############# MAKING FIGURE ############################
from NeuroTools.plotting import pylab_params
from numpy import zeros, where, arange

pylab.close('all')
pylab.ioff() #pylab.ion() #

""" Figure

Prints to a figure the mean firing rate
* in (x,y) accross time during the stimulation and
* in t accross positions within the center
for the output (ON and OFF) and for the different parameter values.

"""
pylab.rcParams.update(pylab_params(fig_width_pt = 497.9) )#, text_fontsize=8))
pylab.figure(num = 1, dpi=300, facecolor='w', edgecolor='k')

x = params['position'][0]
y = params['position'][1]
#Lmargin, Rmargin, dmargin, umargin = 0.05, 0.15, 0.05,  0.05
#pylab.axes([Lmargin, dmargin , 1.0 - Rmargin- Lmargin,1.0-umargin-dmargin]) # [left, bottom, width, height]
#pylab.subplot(131)
pylab.axes([0.1, 0.33, .3/1.61 , .3]) # [left, bottom, width, height]
pylab.scatter(x,y,c=params['amplitude'], faceted = False) #, edgecolors='none'
pylab.title('Input',fontsize ='small')
pylab.axis('equal')
pylab.subplot(232)
pylab.plot(lower_edges[:-1],temporal_ON)
pylab.title('time course (ROI) ',fontsize = 'small')
#pylab.title('time course ON',fontsize = 'small')
pylab.xticks( numpy.linspace(0, params.simtime, 5) )
pylab.ylabel('ON activity (Hz / neuron)')
#pylab.axis('tight')
pylab.subplot(235)
pylab.plot(lower_edges[:-1],temporal_OFF)
#pylab.title('time course OFF',fontsize = 'small')
pylab.xticks( numpy.linspace(0, params.simtime, 5) )
pylab.ylabel('OFF activity (Hz / neuron)')
#pylab.axis('tight')
pylab.xlabel('time (ms)')
pylab.subplot(233)
pylab.scatter(x, y, c= map_spatial_ON[:,-1], faceted = False) #, edgecolors='none'
#pylab.title('spatial distribution ON',fontsize ='small')
pylab.title('Output',fontsize ='small')
pylab.subplot(236)
pylab.scatter(x, y, c= map_spatial_OFF[:,-1], faceted = False) #, edgecolors='none'
#pylab.title('spatial distribution OFF',fontsize ='small')

if 0:
    pylab.ion()
    pylab.show()
else:
    pylab.savefig('results/fig-' + name + '.pdf')
    pylab.savefig('results/fig-' + name + '.png', dpi = 300)


