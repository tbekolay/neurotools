import NeuroTools.spike2.spike2channels as spike2
import pylab, numpy
from scipy.optimize import leastsq
pylab.rcParams['text.usetex'] = True
# helper function
def fit_exp(xs,ys,arg):
    def minimize(arg):
        tau, offset, a = arg
        res = [a*numpy.exp(-x/tau)+offset - ys[i] for i,x in enumerate(xs)]
        return res
    fitres = leastsq(minimize,arg)
    return fitres
filename = '/Users/jenskremkow/src/NeuroTools/examples/spike2/080814_cortex1_1cell001.smr'
a = spike2.load(filename)
current = a[1]
vm = a[2]
#marker = a[32]
t_min = 200.
t_max = 800.
# since the markers dont really work
marker =  current.threshold_detection(threshold=-30.,sign='below')
# current average
current_average, time_axis = current.event_triggered_average(marker,average=True,t_min=t_min,t_max=t_max, with_time = True)
I_base = current_average[0:t_min/current.dt].mean()
I = current_average.min()-I_base
# vm average
vm_average= vm.event_triggered_average(marker,average=True,t_min=t_min,t_max=t_max)
vm_base = vm_average[0:t_min/vm.dt].mean()
# vm average for fit, I am just to lazy to slice the vm_avrage, so I recalculate it, starting with t_min 0.0
vm_average_for_fit, time_axis_for_fit = vm.event_triggered_average(marker,average=True,t_min=0.0,t_max=60., with_time=True)
# fit
tau, offset, a = fit_exp(time_axis_for_fit,vm_average_for_fit,(10.,-69.,3.))[0]
x = numpy.arange(0,200,0.1)
y = a*numpy.exp(-x/tau)+offset
vm_step = offset-vm_base
R = vm_step/I
C = tau/R
# figure
lw = 2.
pylab.subplot(2,1,1)
pylab.plot(time_axis,current_average,'k',lw=lw)
pylab.ylim(-40,-10)
pylab.ylabel('I (pA)')
pylab.subplot(2,1,2)
pylab.plot(time_axis,vm_average,'k',lw=lw)
pylab.plot(x,y,'r',lw=lw)
pylab.xlabel('Time (ms)')
pylab.ylabel('U (mV)')
pylab.ylim(-71.,-68.5)
pylab.text(100,-69.,r'R: %0.3f; C: %0.3f; $\tau$: %0.2f'%(R,C,tau))
pylab.savefig('figure_neuron_parameters.png')
