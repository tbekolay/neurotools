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
# Bug fix for numpy version 1.0.4 for numpy.histogram
numpy.lib.function_base.any = numpy.any

# For inline C optimization
from scipy import weave

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

# Synaptic couplings (mV)
#S = numpy.zeros((N,N))
#S[:,:Ne] = Je*random.uniform(size=(N,Ne))
#S[:,Ne:] = -Ji*random.uniform(size=(N,Ni))

# Connectivity
#S[:,:Ne][random.uniform(size=(N,Ne))-0.9<=0.0]=0.0
#S[:,Ne:][random.uniform(size=(N,Ni))-0.9<=0.0]=0.0

# 10% Connectivity
targets = []
weights = []
# excitatory
for i in xrange(Ne):
    targets.append(random.permutation(numpy.arange(N))[:random.poisson(N*0.1)])
    weights.append(Je*ones_like(targets[i]))
# inhibitory
for i in xrange(Ne,N):
    targets.append(random.permutation(numpy.arange(N))[:random.poisson(N*0.1)])
    weights.append(-Ji*ones_like(targets[i]))

# Statistics of the background external current
#mb = 3.0; sb = 4.0
#mue = mb; sigmae=sb

#sigmai = 0.0

# State variable v, initial value of 0
v = numpy.zeros(N)

# Refractory period state variable
r = numpy.zeros(N)

# storage for intermediate calculations
I = numpy.zeros(N)
Isyn = numpy.zeros(N)

# Spike timings in a list
spikes = [[] for x in xrange(N)]

#print 'mu(nu=5Hz)=%f' % (mb+Ne*Je*.015-leak,)
#print 'mu(nu=100Hz)=%f' % (mb+Ne*Je*.1-leak,)

# total duration of the simulation (ms)
dt = 0.05
duration = 400.0
t = numpy.arange(0.0,duration,dt)
vt = numpy.zeros_like(t)

# This is inline C code
c_code = """

const double mb = 3.0;
const double sb = 4.0;
double mue = mb;
double sigmae = sb;
double sigmai = 0.0;
//double dt = 0.05; // (ms)
double leak = 5.0; // (mV/ms)
double sdt = sqrt(dt);
double reset = 0.0; //(mV)
double refr = 2.5; //(ms)
double threshold = 20.0; //(mv)
double Je = 250.0/Ne;
double Ji = 0.0;


int i,j,k;

// GSL random number generation setup

const gsl_rng_type * T_gsl;
gsl_rng * r_gsl;
     
gsl_rng_env_setup();
     
T_gsl = gsl_rng_default;
r_gsl = gsl_rng_alloc (T_gsl);

py::list l;

for(i=0;i<Nt[0];i++) {
  // time for a strong external input
  if (t(i)>150.0) {
    mue = 6.5;
    sigmae = 7.5;
  }

  // time to restore the initial statistics of the external input
  if (t(i)>300.0) {
    mue = mb;
    sigmae = sb;
  }

  // Noise plus synaptic input from last step
  for (j=0;j<Ne;j++) {
    I(j)=sdt*sigmae*gsl_ran_gaussian(r_gsl,1.0)+Isyn(j);
    //I(j) = 0.0;
    Isyn(j)=0.0;
  }
  for (j=Ne;j<N;j++) {
    I(j)=sdt*sigmai*gsl_ran_gaussian(r_gsl,1.0)+Isyn(j);
    //I(j)=0.0;
    Isyn(j)=0.0;
  }

  // Euler's method for each neuron
  for (j=0;j<N;j++) {
  
    if (v(j)>=threshold) {
      l = py::list((PyObject*)(spikes[j]));
      l.append(t(i));
      for (k=0;k<targets[j].size();k++) {
        Isyn(targets[j][k]) += (const double)weights[j][k];
      }
      v(j) = reset;
      r(j) = refr;
    }
    
    if(r(j)<0) {
      I(j) -= dt*(leak-mue);
      v(j) +=I(j);
      v(j) = v(j)>=0.0 ? v(j) : 0.0;
    }
    else {
      r(j)-=dt;
    }
  }

  vt(i) = v(0);

}

// Clean-up the GSL random number generator
gsl_rng_free (r_gsl);

l = py::list((PyObject*)spikes[0]);
l.append(3.0);


"""

t2 = time.time()
print 'Elapsed time is ', str(t2-t1), ' seconds.'

t1 = time.time()


weave.inline(c_code, ['v','r','t','vt','dt',
                      'spikes','I','Isyn','Ne','Ni','N','targets','weights'],
             type_converters=weave.converters.blitz,
             headers = ["<gsl/gsl_rng.h>", "<gsl/gsl_randist.h>"],
             libraries = ["gsl","gslcblas"])

t2 = time.time()
print 'Elapsed time is ', str(t2-t1), ' seconds.'


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


