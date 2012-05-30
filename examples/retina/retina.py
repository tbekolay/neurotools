#!/usr/bin/env python
# -*- coding: utf8 -*-
"""

retina.py
=========

The retina for 'benchmark one'. This should feed the 'Hyper-Column' (see
https://facets.kip.uni-heidelberg.de/private/wiki/index.php/V1_hypercolumn )


For this retina, it consists of 2 layers of neurons on a rectangular
grid connected in a one to one fashion. Here, we more use primate  'Phasic'
responses originate with morphologically larger ganglion cell types with fast
optic nerve fiber conduction velocities (~4 m/s, Gouras, 1969). Microelectrodes
staining of such cells shows that they are 'parasol' types (Dacey and Lee, 1994).
ON types branch low in the inner plexiform layer (sublamina b), while OFF types
branch high in the inner plexiform layer (sublamina a) following the classic
branching pattern for ON and OFF center cells (Nelson et al, 1978; Dacey and Lee,
1994). Phasic cells are often referred to as the 'magnocellular' or 'M-cell'
pathway because their fibers terminate in the magnocellular layer of the lateral
geniculate nucleus of the thalamus. Near the fovea receptive fields of phasic
cells are 2-3 times larger than those of tonic cells and may be 10 times larger
in peripheral retina.

The data times outputted by the model are the input to the LGN (
http://en.wikipedia.org/wiki/Lateral_geniculate_nucleus ). Time for travelling
through the retina being compensated :


@article{Stanford87,
    Author = {Stanford, L R},
    Journal = {Science},
    Month = {Oct},
    Number = {4825},
    Pages = {358-360},
    Title = {Conduction velocity variations minimize conduction time differences
    among retinal ganglion cell axons},
    Volume = {238},
    Year = {1987}}

To remember (in the cat) 5° of visual angle ~ 1 mm of retina

See :
Data for parameters http://webvision.med.utah.edu/GCPHYS1.HTM (TODO LUP: define
different sets for different animals (cat, monkey, human))
Morphology : http://webvision.med.utah.edu/GC1.html
Topics on CVonline http://homepages.inf.ed.ac.uk/cgi/rbf/CVONLINE/phase3entries.pl?TAG59

TODO (LuP) : use Ringach 07 for setting the neurons centers
TODO (LuP) : the grid is rectangular, but should be hexagonal / log-polar conformation
/ define boudaries in biological coordinates

from scipy.interpolate import interpolate
from numpy.random import randn
from numpy import *

data = arange(16)
data = data+1
data = data.reshape(4,4)
xrange = arange(4)
yrange = arange(4)
X,Y = meshgrid(xrange,yrange)

outgrid = interpolate.interp2d(X,Y,data,kind='linear')
xi = array([0,0.5,1,1.5,2,2.5,3])
yi = xi

z = outgrid(xi,yi)



TODO (LuP) : allow the use of moving images /
TODO (LuP) : justify or not SFA (since we are interested in synchrony effect, we should
rather use a simpler model) / noise model
TODO (LuP) : use real delays
TODO (LuP) : get significative statistics to the retina into that file
TODO (Lup) : use another cell type?

TODO (Lup) : use  nest2 definitively

$ Id $

"""
import datetime

import pyNN.nest2 as sim
from pyNN.utility import Timer
from NeuroTools.signals import load_spikelist
import os, tempfile
import numpy
from NeuroTools.parameters import ParameterSet


class Retina(object):
    """
    Model class for the retina.

    """
    def __init__(self,N=1000):
        """
        Default parameters for the retina of size NxN.

        Sets up parameters and the whole structure of the dictionary / HDF file in url.
        It contains all relevant parameters and stores them to a dictionary for
         clarity &future compatibility with XML exports.

        """
        #try :
        #    url = "https://neuralensemble.org/svn/NeuroTools/trunk/examples/retina/retina.param"
        #    self.params = ParameterSet(url)
        #    print "Loaded parameters from SVN"
        #except :
        params = {} # a dictionary containing all parameters
        # === Define parameters ========================================================
        # LUP: get running file name and include script in HDF5?

        params = {'description' : 'default retina',
            'N': N, # integer;  square of total number of Ganglion Cells LUP: how do we include types and units in parameters? (or by default it is a float in ISO standards) TODO: go rectangular
            'N_ret': .2, # float;  diameter of Ganglion Cell's RF (max: 1)
            'K_ret': 4.0, # float; ratio of center vs. surround in DOG
            'dt'         : 0.1,# discretization step in simulations (ms)
            'simtime'    : 40000*0.1,      # float; (ms)
            'syn_delay'  : 1.0,         # float; (ms)
            'noise_std' : 5.0,       # (nA) standard deviation of the internal noise
            'snr' : 2.0, # (nA) maximum signal
            'weight'     : 1.0, #
            #'threads' : 2, 'kernelseeds' : [43210987, 394780234],      # array with one element per thread
            #'threads' : 1,
            'kernelseed' : 4321097,       # array with one element per thread
            # seed for random generator used when building connections
            'connectseed' : 12345789,  # seed for random generator(s) used during simulation
            'initialized' : datetime.datetime.now().isoformat() # the date in ISO 8601 format to avoid overriding old simulations
        }

        # retinal neurons parameters
        params['parameters_gc'] = {'Theta':-57.0, 'Vreset': -70.0,'Vinit': -70.0,
        'TauR': 0.5, 'gL':28.95,
        'C':289.5, 'V_reversal_E': 0.0, 'V_reversal_I': -75.0, 'TauSyn_E':1.5,
        'TauSyn_I': 10.0, 'V_reversal_sfa': -70.0, 'q_sfa': 0., #14.48,
        'Tau_sfa':110.0, 'V_reversal_relref': -70.0, 'q_relref': 3214.0,
        'Tau_relref': 1.97}#,'python':True}

        ## default input image # TODO add start and stop time
        # define the center of every neuron in normalized visual angle / retinal space

        #X,Y = numpy.meshgrid(numpy.linspace(-N/2, N/2,N),numpy.linspace(-N/2,N/2,N))
        X,Y = numpy.random.rand(N)*2-1, numpy.random.rand(N)*2 -1

        # Generate a DOG excitation on the input layer of the GC
        # Based on the assumptions of the DOG model (Enroth-Cugell and Robson, 1966) that ganglion cells linearly add signals from both center and surround mechanisms for all points in space
        # this is the impulse response to a discrete dirac in the center to some specific luminance / excentricity value
        #   easy : extend to input images (simply by convoluting the image with this kernel)
        #   hard : extend to time varrying movies (not only a step)
        params['position'] = [X,Y]
        R2= X**2 + Y**2
        N, N_ret, K_ret = params['N'], params['N_ret'], params['K_ret']
        amplitude = (numpy.exp(-R2 / ( 2 * N_ret**2) )  - 1/K_ret**2 * numpy.exp(-R2 / ( 2 *  N_ret**2 * K_ret**2) )) / (1  - 1/K_ret**2)
        #amplitude *=  params['noise_std'] # scaled by the noise variance
        #file.setStructure({'amplitude' : amplitude }, "/build", createparents=True)
        params['amplitude'] = amplitude

        self.params =  ParameterSet(params)
            #self.params.save('file://' + os.getcwd() + '/retina.param')


    def run(self,params,verbose=True):
        """
        params are the parameters to use

        """
        tmpdir = tempfile.mkdtemp()
        myTimer = Timer()
        # === Build the network ========================================================
        if verbose: print "Setting up simulation"
        myTimer.start() # start timer on construction
        sim.setup(timestep=params['dt'],max_delay=params['syn_delay'])
        N = params['N']
        #dc_generator
        phr_ON = sim.Population((N,),'dc_generator')
        phr_OFF  = sim.Population((N,),'dc_generator')


        for factor, phr in [(-params['snr'],phr_OFF),(params['snr'],phr_ON)]:
            phr.tset('amplitude', params['amplitude'] * factor )
            phr.set({ 'start' : params['simtime']/4, 'stop' : params['simtime']/4*3})

        # internal noise model (see benchmark_noise)
        noise_ON = sim.Population((N,),'noise_generator',{'mean':0.,'std':params['noise_std']})
        noise_OFF = sim.Population((N,),'noise_generator',{'mean':0.,'std':params['noise_std']})


        # target ON and OFF populations (what about a tridimensional Population?)
        out_ON = sim.Population((N,), sim.IF_curr_alpha)#'IF_cond_alpha) #iaf_sfa_neuron')# EIF_cond_alpha_isfa_ista, IF_cond_exp_gsfa_grr,sim.IF_cond_alpha)#'iaf_sfa_neuron',params['parameters_gc'])#'iaf_cond_neuron')# IF_cond_alpha) #
        out_OFF = sim.Population((N,), sim.IF_curr_alpha)#'IF_cond_alpha) #IF_curr_alpha)#'iaf_sfa_neuron')#sim.IF_curr_alpha)#,params['parameters_gc'])


        # initialize membrane potential TODO: and conductances?
        from pyNN.random import RandomDistribution, NumpyRNG
        rng = NumpyRNG(seed=params['kernelseed'])
        vinit_distr = RandomDistribution(distribution='uniform',parameters=[-70,-55], rng=rng)
        for out_ in [out_ON, out_OFF]:
            out_.randomInit(vinit_distr)


        retina_proj_ON = sim.Projection(phr_ON, out_ON, sim.OneToOneConnector())
        retina_proj_ON.setWeights(params['weight'])
        # TODO fix setWeight, add setDelays to 10 ms (relative to stimulus onset)
        retina_proj_OFF = sim.Projection(phr_OFF, out_OFF, sim.OneToOneConnector())
        retina_proj_OFF.setWeights(params['weight'])

        noise_proj_ON = sim.Projection(noise_ON, out_ON, sim.OneToOneConnector())
        noise_proj_ON.setWeights(params['weight'])
        noise_proj_OFF = sim.Projection(noise_OFF, out_OFF, sim.OneToOneConnector()) # implication if ON and OFF have the same noise input?
        noise_proj_OFF.setWeights(params['weight'])


        out_ON.record()
        out_OFF.record()

        # reads out time used for building
        buildCPUTime= myTimer.elapsedTime()

        # === Run simulation ===========================================================
        if verbose: print "Running simulation"

        myTimer.reset() # start timer on construction
        sim.run(params['simtime'])
        simCPUTime = myTimer.elapsedTime()

        myTimer.reset()  # start timer on construction
        # TODO LUP use something like "for pop in [phr, out]" ?
        out_ON_filename=os.path.join(tmpdir,'out_on.gdf')
        out_OFF_filename=os.path.join(tmpdir,'out_off.gdf')
        out_ON.printSpikes(out_ON_filename)#
        out_OFF.printSpikes(out_OFF_filename)#

        # TODO LUP  get out_ON_DATA on a 2D grid independantly of out_ON.cell.astype(int)
        out_ON_DATA = load_spikelist(out_ON_filename,range(N),
                                        t_start=0.0, t_stop=params['simtime'])
        out_OFF_DATA = load_spikelist(out_OFF_filename,range(N),
                                        t_start=0.0, t_stop=params['simtime'])

        out = {'out_ON_DATA':out_ON_DATA,
                'out_OFF_DATA':out_OFF_DATA}#,'out_ON_pos':out_ON}
        # cleans up
        os.remove(out_ON_filename)
        os.remove(out_OFF_filename)
        os.rmdir(tmpdir)
        writeCPUTime = myTimer.elapsedTime()

        if verbose:
            print "\nRetina Network Simulation:"
            print(params['description'])
            print "Number of Neurons  : ", N
            print "Output rate  (ON) : ", out_ON_DATA.mean_rate(), "Hz/neuron in ", params['simtime'], "ms"
            print "Output rate (OFF)   : ", out_OFF_DATA.mean_rate(), "Hz/neuron in ",params['simtime'], "ms"
            print("Build time             : %g s" % buildCPUTime) 
            print("Simulation time        : %g s" % simCPUTime)
            print("Writing time           : %g s" % writeCPUTime)

        return out


if __name__ == '__main__':

    ret = Retina(100)
    out = ret.run(ret.params)
    # plotting
    import pylab
    fig = pylab.figure(1)
    z = pylab.subplot(121)
    out['out_ON_DATA'].raster_plot(display=z, id_list=range(20), kwargs={'color':'r'})
    z = pylab.subplot(122)
    out['out_OFF_DATA'].raster_plot(display=z, id_list=range(20), kwargs={'color':'b'})
    fig = pylab.figure(2)
    z = pylab.subplot(111)
    out['out_ON_DATA'].firing_rate(ret.params.simtime/100, display=z, kwargs={'label':'ON','color':'r'})
    out['out_OFF_DATA'].firing_rate(ret.params.simtime/100, display=z, kwargs={'label':'OFF','color':'b'})
    pylab.legend()

