# Created by Eugene M. Izhikevich, 2003 Modified by S. Fusi 2007
# Ported to Python by Eilif Muller, 2008.
#
# Notes:
#
# Requires matplotlib,ipython,numpy>=1.0.3
# On a debian/ubuntu based system:
# $ apt-get install python-matplotlib python-numpy ipython
#
# Start ipython with threaded plotting support:
# $ ipython -pylab
#
# At the resulting prompt, run the file by:
# In [1]: execfile('smallnet.py')

# Modules required
import numpy
import numpy.random as random
import acml_rng
# Bug fix for numpy version 1.0.4
numpy.lib.function_base.any = numpy.any

# For measuring performance
import time
t1 = time.time()

# Excitatory and inhibitory neuron counts
Ne = 1000      
Ni = 4
N = Ne+Ni

# Synaptic couplings
Je = 250.0/Ne 
Ji = 0.0

# reset depolarization (mV)
reset = 0.0

# refractory period (ms)
refr = 2.5 

# Synaptic couplings (mV)
S = numpy.zeros((N,N))
S[:,:Ne] = Je*random.uniform(size=(N,Ne))
S[:,:Ni] = -Ji*random.uniform(size=(N,Ni))

# Connectivity
S[:,:Ne][random.uniform(size=(N,Ne))-0.9<=0.0]=0.0
S[:,Ne:][random.uniform(size=(N,Ni))-0.9<=0.0]=0.0

# (mV/ms) (lambda is a python keyword)
leak = 5.0
dt = 0.05
sdt = numpy.sqrt(dt)

# Statistics of the background external current
mb = 3.0; sb = 4.0
mue = mb; sigmae=sb

sigmai = 0.0

# State variable v, initial value of 0
v = numpy.zeros(N)

# Refractory period state variable
r = numpy.zeros(N)

# Spike timings in a list
firings = []
spikes = [[]]*N


print 'mu(nu=5Hz)=%f' % (mb+Ne*Je*.015-leak,)
print 'mu(nu=100Hz)=%f' % (mb+Ne*Je*.1-leak,)

# total duration of the simulation (ms)
duration = 400.0
t = numpy.arange(0.0,400.0,dt)
vt = numpy.zeros_like(t)

t2 = time.time()
print 'Elapsed time is ', str(t2-t1), ' seconds.'

t1 = time.time()

for i,ti in enumerate(t):
    # time for a strong external input
    if ti>150.0:
        mue = 6.5
        sigmae = 7.5

    # time to restore the initial statistics of the external current
    if ti>300.0:
        mue = mb
        sigmae = sb

    Iext = acml_rng.normal(1.0,N)
    Iext[:Ne]*=sigmae
    Iext[Ne:]*=sigmai

    # Which neurons fired?
    fired = numpy.nonzero(v>=20.0)[0]

    if len(fired)>0:

        # Save mean firing rate of the excitatory neurons

        v[fired] = reset
        r[fired] = refr

        # Append spikes to the spike list
        for n in fired:
            # Spikes are stored by a (neuron, time) pair
            # For easy plotting later
            firings.append((n,ti))
            # and as a list for each neuron
            spikes[n].append(ti)
    
        aux = v-dt*(leak-mue)+numpy.sum(S[:,fired],1)+sdt*Iext

    else:
        aux = v-dt*(leak-mue)+sdt*Iext;

    # Neurons not in the refractory period
    nr = numpy.nonzero(r<=0)[0]
    # Bound voltages above 0.0
    v[nr] = numpy.where(aux[nr]>=0.0,aux[nr],0.0)

    # Progress refractory variable
    nr = numpy.nonzero(r>0)[0]
    r[nr]-=dt

    # record the voltage trace of the zeroeth neuron
    vt[i] = v[0]


t2 = time.time()
print 'Elapsed time is ', str(t2-t1), ' seconds.'

# -------------------------------------------------------------------------
# Plot everything
# -------------------------------------------------------------------------


def myplot():
    
    global firings

    t1 = time.time()

    figure()
    
    # Membrane potential trace of the zeroeth neuron
    subplot(3,1,1)
    
    vt[vt>=20.0]=65.0
    plot(t,vt)
    ylabel(r'$V-V_{rest}\ \left[\rm{mV}\right]$')
    
    # Raster plot of the spikes of the network
    subplot(3,1,2)
    myfirings = array(firings)
    myfirings_100 = myfirings[myfirings[:,0]<min(100,Ne)]
    plot(myfirings_100[:,1],myfirings_100[:,0],'.')
    axis([0, duration, 0, min(100,Ne)])
    ylabel('Neuron index')
    
    # Mean firing rate of the excitatory population as a function of time
    subplot(3,1,3)
    # 1 ms resultion of rate histogram
    dx = 1.0
    x = arange(0,duration,dx)
    myfirings_Ne = myfirings[myfirings[:,0]<Ne]
    mean_fe,x = numpy.histogram(myfirings_Ne[:,1],x)
    plot(x,mean_fe/dx/Ne*1000.0,ls='steps')
    ylabel('Hz')
    xlabel('time [ms]')
    t2 = time.time()
    print 'Finished.  Elapsed', str(t2-t1), ' seconds.'



#myplot()

