"""
$Id: sfn_example_stgen.py 362 2008-12-08 17:35:59Z LaurentPerrinet $

Example to show off some capabilities of the stgen module 
and the SpikeTrain class.

- Creates two poisson spike trains with approx. rate of 100 Hz. 
- Calculates rate, coefficient of variance and fano factor using the 
  functions form SpikeTrain.
- Calculates cross correlation between the two SpikeTrains.
- generates a third SpikeTrain with rate ~10Hz and merges it into the 
  previous two, effectively injecting correlation.
- Plots the cross correlation for the correlated and uncorrelated SpikeTrains.
- Generates shot noise from one SpikeTrain using the StGEn class and plots it.
- Calculates spike triggered average from shot noise to reconstruct the initial 
  shot noise kernel.

Performed at the NeuroTools demo session, INCF booth, 
SfN annual meeting 2008, Washington. DC.
"""
import NeuroTools.stgen as stgen
import pylab
sg = stgen.StGen()
duration = 10000.
rate_independent = 100. #Hz
rate_shared = 10. #Hz, 10 % correlation

st1 = sg.poisson_generator(rate=rate_independent, t_stop = duration) 
print "Spiketrain 1:"
print "mean rate: %f" % st1.mean_rate()
print "coefficient of variation: %f" % st1.cv_isi()
print "fano factor: %f" % st1.fano_factor_isi()

st2 = sg.poisson_generator(rate=rate_independent, t_stop = duration) 
print "Spiketrain 2:"
print "mean rate: %f" % st2.mean_rate()
print "coefficient of variation: %f" % st2.cv_isi()
print "fano factor: %f" % st2.fano_factor_isi()

# cross correlation
import numpy
cc = numpy.correlate(st1.time_histogram(time_bin = 1.), 
                     st2.time_histogram(time_bin = 1.), 
                     mode = 'same')
time_axis = numpy.linspace(cc.shape[0]/-2., cc.shape[0]/2, cc.shape[0])

pylab.plot(time_axis, cc, label = 'no correlation', alpha = 0.5)

# inject correlation into st1 and st2 
st3 = sg.poisson_generator(rate = rate_shared, t_stop = duration) 
st1.merge(st3)
st2.merge(st3)

cc2 = numpy.correlate(st1.time_histogram(time_bin = 1.), 
                      st2.time_histogram(time_bin = 1.), 
                      mode = 'same')

pylab.plot(time_axis, cc2, label = '10% correlation', alpha = 0.5)
pylab.legend()
pylab.show()

#generate shot noise from st1
st1_shot = stgen.shotnoise_fromspikes(st1, 
                                      q = 1.0, 
                                      tau = 10., 
                                      t_start = st1.t_start, 
                                      t_stop = st1.t_stop)
f = pylab.figure()
pylab.plot(st1_shot.signal)
f.gca().set_title('shot noise')
f.gca().set_xlabel('time [ms]')

# spike triggered average reveals the original shot-noise kernel
sta = st1_shot.event_triggered_average(st1, display = True, average = True)


