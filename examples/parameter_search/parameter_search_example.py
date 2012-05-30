"""
parameter_search_example.py

$Id: parameter_search_example.py 365 2008-12-23 21:47:50Z mschmucker $

Author: Michael Schmuker

This script demonstrates how to use the parameter_search module for parallel 
computation together with PyNN for (minimal) network simulation and NeuroTools 
for almost everything else.

The network consists of a SpikeSource driving a neuron with conductance-based 
synapses.

To run this script, you first have to invoke an IPython controller and 
computation engines. If IPython is installed correctly and with parallel 
computation support, you can just type:

> ipcluster -n 2 &

This will start two computation engines and a controller in the background.

When the controller is up, run this script:

> python parameter_search_example.py

Calculation will start, and after a few seconds (depending on your hardware) 
it will save a png graphics file that illustrates the firing rate of a neuron 
as a function of the input rate and the weight of the synapse to your current 
directory.

"""
def model_network(param_dict):
    """
    This model network consists of a spike source and a neuron (IF_curr_alpha). 
    The spike rate of the source and the weight can be specified in the 
    param_dict. Returns the number of spikes fired during 1000 ms of simulation.
    
    Parameters:
    param_dict - dictionary with keys
                 rate - the rate of the spike source (spikes/second)
                 weight - weight of the connection source -> neuron
                 
    Returns:
    dictionary with keys:
        source_rate - the rate of the spike source
        weight - weight of the connection source -> neuron
        neuron_rate - spike rate of the neuron
    """ 
    #set up the network
    import pyNN.neuron as sim
    sim.setup(dt = 0.01,  min_delay = 1.,  max_delay = 1.,  debug = False,  
              quit_on_end = False)
    
    weight = param_dict['weight']
    
    import NeuroTools.stgen as stgen
    stgen = stgen.StGen()
    spiketrain = stgen.poisson_generator(param_dict['rate'], t_stop = 1000.)
    source = sim.Population(1, sim.SpikeSourceArray,  
                            {'spike_times':spiketrain.spike_times})
    neuron = sim.Population(1, sim.IF_cond_alpha)
    sim.Projection(source, neuron, 
                   method = sim.OneToOneConnector(weights = param_dict['weight'], 
                                                  delays = 1.))
    
    #set recorder
    neuron.record()
    neuron.record_v()
    
    #run the simulation
    sim.run(1001.)
    sim.end()
    
    # count the number of spikes
    spikes = neuron.getSpikes()
    numspikes = len(spikes)
    
    # return everything, including the input parameters
    return {'source_rate':param_dict['rate'], 
            'weight':param_dict['weight'], 
            'neuron_rate':numspikes }
    
def make_param_dict_list():
    """
    create a list of parameter dictionaries for the model network.
    """
    # there is certainly a way to do this with NeuroTools. 
    import numpy
    rates = numpy.linspace(start = 10., stop = 100.,  num = 5)
    weights = numpy.linspace(start = 0.1,  stop = 1.0, num = 5)
    from NeuroTools.parameters import ParameterSet, ParameterSpace, ParameterRange
    params = ParameterSpace(ParameterSet({'rate':ParameterRange(rates), 
                                          'weight': ParameterRange(weights)}))
    dictlist = [p.as_dict() for p in params.iter_inner()]
    return dictlist

def show_results(result):
    """
    visualizes the result of the parameter search.
    Parameters:
    result - list of result dictionaries.
    """
    import numpy
    rates = numpy.sort([r['source_rate'] for r in result])
    weights = numpy.sort([r['weight'] for r in result])
    neuron_rates = numpy.zeros((len(rates), len(weights)))
    for r_i in range(len(rates)):
        for w_i in range(len(weights)):
            neuron_rates[r_i, w_i] = [r['neuron_rate'] for r in result 
                                      if (r['source_rate'] == rates[r_i])
                                      and (r['weight'] == weights[w_i])][0]
    import NeuroTools.plotting as plotting
    pylab = plotting.get_display(True)
    pylab.rcParams.update(plotting.pylab_params())
    subplot = pylab.imshow(neuron_rates, 
                           interpolation = 'nearest',  
                           origin = 'lower')
    plotting.set_labels(subplot.get_axes(), 
                        xlabel = 'rate',  
                        ylabel = 'weight')
    pylab.colorbar()
    # could add fancy xticks and yticks here
    import tempfile, os
    (fd,  figfilename) = tempfile.mkstemp(prefix = 'parameter_search_result', 
                                          suffix = '.png', 
                                          dir = os.getcwd())
    pylab.gcf().savefig(figfilename)
 
def run_it():
    """"
    Run the parameter search.
    """
    import NeuroTools.optimize.parameter_search as ps

    # search the parameter space
    param_dict_list = make_param_dict_list()
    srchr = ps.IPythonParameterSearcher(
        dict_iterable = param_dict_list,
        func = model_network)
    srchr.search()
    outlist = srchr.harvest()

    #return the results
    return outlist

if __name__ == '__main__':
    results = run_it()
    show_results(results)
