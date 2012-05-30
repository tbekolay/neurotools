"""
Example to show off some capabilities of the signals module 
and the SpikeList and AnalogSignalList class.

- loads spiking and voltage data simulated with pyNN
- calculates various measurements (mean firing rate, cv...)
- plot the signals
- plots the spike-triggered-averages

Performed at the NeuroTools demo session, INCF booth, 
SfN annual meeting 2008, Washington. DC.
"""
import NeuroTools.signals as signals

# loading spiking data
s = signals.load_spikelist('spike_data')

# raster plot
s.raster_plot()

# mean rate
print 'mean rate: ',s.mean_rate()
print 'mean rates: ',s.mean_rates()
# fano factor of isi
print 'fano factor of isi: ',s.fano_factors_isi()
# cv of isi
print 'cv of isi:',s.cv_isi()

# isi distribution
hs = s.isi_hist(bins=20, display=True)


# loading voltage data
v = signals.load_vmlist('vm_data')

# plot all the signals
v.plot()
# plot only one AnalogSignal
v[1].plot()

# spike triggered averages
v.event_triggered_average(s,t_min=50.)

