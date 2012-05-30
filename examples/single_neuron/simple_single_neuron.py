#/usr/bin/python
# -*- coding: utf8 -*-
"""
simple_single_neuron

Running a single neuron using pyNN + NEST2

Laurent Perrinet, INCM, CNRS -- October 2006

Changes :
Refactored to use the new NeuroTools-- Nov 2007
Changed to use new pyNN syntax / NEST2-- May 2008


$ Id $‚

"""


import numpy
import sys, os, tempfile
# choosing the simulator
import pyNN.nest2 as sim
# the link to read SpikeList files with NeuroTools
from NeuroTools.signals import load_spikelist
# using parameters utility
from NeuroTools.parameters import ParameterSet
from pyNN.utility import Timer

class FiberChannel(object):
    """
    Model class for the fiber of simple neurons.

    """
    def __init__(self,N=100):
        # simulator specific
        simulation_params = ParameterSet({'dt'        : 0.1,# discretization step in simulations (ms)
                    'simtime'   : 40000*0.1,      # float; (ms)
                    'syn_delay' : 1.0,         # float; (ms)
                    'kernelseed' : 4321097,       # array with one element per thread
                    'connectseed' : 12345789  # seed for random generator(s) used during simulation
                    })
        # these may change
        self.params = ParameterSet({'simulation': simulation_params,
                        'N'         : N,
                        'noise_std' : 6.0,       # (nA??) standard deviation of the internal noise
                        'snr'       : 1.0,      # (nA??) size of the input signal
                        'weight'    : 1.0 },
                        label="fiber_params")

        print self.params.pretty()

    def run(self,params, verbose =True):
        tmpdir = tempfile.mkdtemp()
        timer = Timer()
        timer.start() # start timer on construction

        # === Build the network ========================================================
        if verbose: print "Setting up simulation"
        sim.setup(timestep=params.simulation.dt,max_delay=params.simulation.syn_delay, debug=False)

        N = params.N
        #dc_generator
        current_source = sim.DCSource(  amplitude= params.snr,
                                        start=params.simulation.simtime/4,
                                        stop=params.simulation.simtime/4*3)
        
        # internal noise model (NEST specific)
        noise = sim.Population(N,'noise_generator',{'mean':0.,'std':params.noise_std}) 
        # target population
        output = sim.Population(N , sim.IF_cond_exp)

        # initialize membrane potential
        numpy.random.seed(params.simulation.kernelseed)
        V_rest, V_spike = -70., -53.
        output.tset('v_init',V_rest + numpy.random.rand(N,)* (V_spike -V_rest))

        #  Connecting the network
        conn = sim.OneToOneConnector(weights = params.weight)
        sim.Projection(noise, output, conn)

        for cell in output:
            cell.inject(current_source)

        output.record()

        # reads out time used for building
        buildCPUTime= timer.elapsedTime()

        # === Run simulation ===========================================================
        if verbose: print "Running simulation"

        timer.reset() # start timer on construction
        sim.run(params.simulation.simtime)
        simCPUTime = timer.elapsedTime()

        timer.reset()  # start timer on construction

        output_filename = os.path.join(tmpdir,'output.gdf')
        #print output_filename
        output.printSpikes(output_filename)#
        output_DATA = load_spikelist(output_filename,N,
                                        t_start=0.0, t_stop=params.simulation.simtime)
        writeCPUTime = timer.elapsedTime()

        if verbose:
            print "\nFiber Network Simulation:"
            print "Number of Neurons  : ", N
            print "Mean Output rate    : ", output_DATA.mean_rate(), "Hz during ",params.simulation.simtime, "ms"
            print("Build time             : %g s" % buildCPUTime)
            print("Simulation time        : %g s" % simCPUTime)
            print("Writing time           : %g s" % writeCPUTime)

        os.remove(output_filename)
        os.rmdir(tmpdir)

        return output_DATA

if __name__ == '__main__':
    myFibers = FiberChannel(N=50)
    spikes = myFibers.run(myFibers.params)
    spikes.raster_plot()
    import pylab
    pylab.show()
