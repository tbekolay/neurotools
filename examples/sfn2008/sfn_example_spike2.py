import NeuroTools.spike2.spike2channels as spike2
import pylab, numpy
"""
Example to show off some capabilities of the spike2 module 
and the SpikeTrain and AnalogSignal class.

- loads content from a CED Son file which contains data from a IF-curve experiment
- then the data is processed and a IF-Curve is plotted

Performed at the NeuroTools demo session, INCF booth, 
SfN annual meeting 2008, Washington. DC.
"""

# IF-curve

filename = 'IF-Curve-example-data-provided-by-Florian-Rau-University-of-Freiburg-2008.smr'

# load all channels in the file
#all_channels = spike2.load(filename)
# or only selected channels
all_channels = spike2.load(filename,channels=[1,2,32])

# seperate the channels, just for better reading
vm = all_channels[2]
dc = all_channels[1]
dc_onset_marker = all_channels[32]

pylab.close('all')
# show original data
# vm
pylab.figure()
pylab.plot(vm.time_axis(),vm.signal())
# currents
pylab.figure()
pylab.plot(dc.time_axis(),dc.signal())
# dc_onset_markers


# cutout the dc and vm around a dc step, markers are in seconds, we need them in milliseonds
dc_sequence = dc.slice_by_events(dc_onset_marker.times*1000,t_min=500,t_max=1000)
vm_sequence = vm.slice_by_events(dc_onset_marker.times*1000,t_min=500,t_max=1000)

xlim = [1000,27000]

# first figure shows the data
pylab.rcParams['figure.figsize'] = [15.,10.]
pylab.figure()
# plot dc signal with real time
subplot = pylab.subplot(2,2,1)
for dc_slice in dc_sequence.values():
    # we plot each dc_slice with its real time
    pylab.plot(dc_slice.time_axis(),dc_slice.signal)
# we show only part of the data
pylab.xlim(xlim)
pylab.ylabel('current (pA)')
pylab.title('current with real time')
xmin,xmax,ymin,ymax = subplot.axis()
# plot dc signal with normalized time, such that each dc_slice starts at time 0.0
pylab.subplot(2,2,2)
for index, dc_slice in dc_sequence.items():
    # we plot each dc_slice with its normalized time --> start at 0.0 ms
    if index <= 4:
        # only 5 slices are plotted
        pylab.plot(dc_slice.time_axis(normalized=True),dc_slice.signal)
pylab.ylim([ymin,ymax])
pylab.title('current with normalized time')

# plot vm signal with real time
subplot = pylab.subplot(2,2,3)
for vm_slice in vm_sequence.values():
    pylab.plot(vm_slice.time_axis(),vm_slice.signal)
pylab.xlim(xlim)
pylab.xlabel('Time (ms)')
pylab.ylabel('mp (mV)')
pylab.title('mp with real time')
xmin,xmax,ymin,ymax = subplot.axis()
# plot vm signal with normalized time, such that each dc_slice starts at time 0.0
pylab.subplot(2,2,4)
for index, vm_slice in vm_sequence.items():
    if index <= 4:
        pylab.plot(vm_slice.time_axis(normalized=True),vm_slice.signal)
pylab.xlabel('Time (ms)')
pylab.title('mp with normalized time')
pylab.ylim([ymin,ymax])
pylab.savefig('IF_curve_data.png')
pylab.close('all')


# second figure shows the IF-curve
pylab.rcParams['figure.figsize'] = [6.,5.]
pylab.figure()
dc_inputs = []
frs = []

# calculate the actual IF-curve
for dc_slice, vm_slice in zip(dc_sequence.values(), vm_sequence.values()):
    # we calculate the max of the dc_slice
    input_dc = dc_slice.max()
    # we perform a threshold detection on the vm slice, which returns a SpikeTrain object, this knows its mean_rate (Hz)
    fr = vm_slice.threshold_detection(0.0).mean_rate()
    # we append the values
    dc_inputs.append(input_dc)
    frs.append(fr)
# and plot them
pylab.plot(dc_inputs,frs,'ok',label='data')

pylab.xlabel('I (pA)')
pylab.ylabel('spikes/s')
pylab.title('IF-curve')


pylab.savefig('IF_curve_curve.png')

