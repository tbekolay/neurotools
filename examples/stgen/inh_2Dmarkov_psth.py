# This script generates Figure 5 in:

#       Eilif Muller, Lars Buesing, Johannes Schemmel, and Karlheinz Meier 
#       Spike-Frequency Adapting Neural Ensembles: Beyond Mean Adaptation and Renewal Theories
#       Neural Comput. 2007 19: 2958-3010.

# i.e. the PSTH for a 2D adapting markov process undergoing
# a step change in statistics due to a step stimulus.


import numpy,sys
from NeuroTools import stgen
from pylab import zeros_like, plot

dt = 10.0
t = numpy.arange(0,1000.0,dt) 
a = numpy.ones_like(t)*11.346
bq = numpy.ones_like(t)*0.1231*14.48

# stepup

i_start = t.searchsorted(400.0,'right')-1
i_end = t.searchsorted(600.0,'right')-1

a[i_start:i_end] = 92.25
bq[i_start:i_end] = 0.09793*14.48

psth = zeros_like(t)

stg = stgen.StGen()

tau_s = 110.0
tau_r = 1.97
qrqs = 221.96
t_stop = 1000.0

trials = 5000
print "Running %d trials of %.2f milliseconds" % (trials, t_stop)
for i in xrange(trials):
    if i%100==0:
        print "%d" % i,
        sys.stdout.flush()
    st = stg.inh_2Dadaptingmarkov_generator(a,bq,tau_s,tau_r,qrqs,t,t_stop,array=True)
    psth[1:]+=numpy.histogram(st,t)[0]

print "\n"

# normalize

psth = psth.astype(float)
psth/= dt*float(trials)/1000.0

# this is for correct 'steps' plotting only
psth[0] = psth[1]

plot(t,psth,linestyle='steps')

print "Done."


