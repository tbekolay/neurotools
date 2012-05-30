# Generate the PSTH for an inhomogeneous gamma renewal process
# with a step change in the rate (b changes, a stays fixed)



import numpy
from NeuroTools import stgen
from pylab import zeros_like, plot
import sys

dt = 10.0
t = numpy.arange(0,1000.0,dt) 
rate = numpy.ones_like(t)*20.0

# stepup

i_start = t.searchsorted(400.0,'right')-1
i_end = t.searchsorted(600.0,'right')-1

rate[i_start:i_end] = 40.0

a = numpy.ones_like(t)*3.0
b = numpy.ones_like(t)/a/rate

psth = zeros_like(t)

stg = stgen.StGen()

trials = 5000
tsim = 1000.0
print "Running %d trials of %.2f milliseconds" % (trials, tsim)
for i in xrange(trials):
    if i%100==0:
        print "%d" % i,
        sys.stdout.flush()
    st = stg.inh_gamma_generator(a,b,t,1000.0,array=True)
    psth[1:]+=numpy.histogram(st,t)[0]

print "\n"

# normalize

psth = psth.astype(float)
psth/= dt*10000.0/1000.0

# this is for plotting only
psth[0] = psth[1]

plot(t,psth,linestyle='steps')

