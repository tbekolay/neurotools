# generate shot noise from step poisson

from NeuroTools import stgen

clf()
stg = stgen.StGen()

rate = numpy.array([6.0,10.0,6.0,6.0])
t = numpy.array([0.0,100.0,200.0,300.0])


q = 2.0
tau = 10.0

trials = 1000
st = stg.inh_poisson_generator(rate, t, 300.0)
g,tsn = stgen.shotnoise_fromspikes(st,q,tau,dt=0.1,t_start=0.0,t_stop=300.0,array=True)
for i in range(trials-1):
    st = stg.inh_poisson_generator(rate, t, 300.0)
    g_tmp,tmp = stgen.shotnoise_fromspikes(st,q,tau,dt=0.1,t_start=0.0,t_stop=300.0,array=True)
    g+=g_tmp

plot(t,rate,'b:',ls='steps-post',lw=2)
plot(tsn,g/q/tau/trials*1000.0,'r-',lw=2)
xlabel('time [ms]',size=20)
xticks(size=16)
ylabel(r'$\nu(t)$ [Hz]',size=20)
yticks(size=16)

