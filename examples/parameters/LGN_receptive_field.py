# encoding: utf-8

"""
Cai et al. 1997 Neurophysiol

"""

import numpy,pylab
from NeuroTools.parameters import ParameterSpace
from NeuroTools.parameters import ParameterRange
from NeuroTools.sandbox import make_name
#
lw = 2.
fs = 16



def parameter_scan(p=None):
    if p is None:
        p = default_parameters()
    #p.K2 = ParameterRange([0.7,0.0])
    #p.dt = ParameterRange([1.,6.77,10.,1000.]) # ms
    #p.td = ParameterRange([0.])#,6.,20.])
    #p.t1 = ParameterRange([0.]) # ms
    #p.t2 = ParameterRange([0.]) # ms
    #g = 0.8
    #p.c1 = ParameterRange([0.14*g])
    #p.c2 = ParameterRange([0.12*g])
    p.sigma_c = ParameterRange([0.1,0.4,0.8])
    
    create_figure()
    
    for experiment in p.iter_inner():
        name = make_name(experiment,p.range_keys())
        print name
        plot_receptive_field(p=experiment,label=name)

def create_figure():
    pylab.close('all')
    pylab.rcParams['figure.figsize'] = (10.0,5.5)
    pylab.rcParams['figure.facecolor'] = 'white'
    pylab.figure()
    
def plot_receptive_field(p=None,d2=False,label=None):
    if p == None:
        p = default_parameters()
    if label == '':
        label = 'default'
    # temporal
    t = numpy.arange(0.,p.duration,p.dt)
    
    # spatial
    x = numpy.arange(-p.size/2.+p.degree_per_pixel/2.,p.size/2.+p.degree_per_pixel/2.,p.degree_per_pixel)

    xm , tm = numpy.meshgrid(x,t)
    kernel = RF(xm,tm,p)
    
    kernel_shape = kernel[:,:].shape
    kernel_fra = kernel_shape[1]/6.
    ticks_st = numpy.arange(-kernel_shape[1]/2.,kernel_shape[1]/2.+1,kernel_fra)
    ticks_st += kernel_shape[1]/2.
    ticks_st -= 0.5
    min_max_label = kernel_shape[1]*p.degree_per_pixel
    min_max_label /= 2.
    ticks_st_label = numpy.arange(-min_max_label,min_max_label+1,min_max_label/3.).astype('int')
    degree_ticks_label = [str(i) for i in ticks_st_label]
    degree_ticks = ticks_st
    
    time_ticks = numpy.arange(kernel.shape[0])*p.dt
    time_vector = time_ticks
    time_ticks_label = numpy.arange(0.,p.duration,p.dt)
    time_ticks_label = numpy.array([str(i) for i in time_ticks_label.round(0).astype('int')])
    time_steps = int(30/p.dt)
    
    label_degree = 'degree'
    label_time = 'time (ms)'
    label_norm = 'normalized amplitude'
    norm_act_lim = (-0.4,1.1)
    if not d2:
        # spatial 1d
        time = int(34./p.dt)
        pylab.subplot(1,2,1)
        pylab.plot(kernel[time,:],label='34 ms',linewidth=lw,label=label)
        pylab.xticks(degree_ticks,degree_ticks_label,fontsize=fs)
        pylab.yticks(fontsize=fs)
        pylab.xlabel(label_degree,fontsize=fs)
        pylab.ylabel(label_norm,fontsize=fs)
        pylab.ylim(norm_act_lim)
        pylab.title('spatial at 34 ms',fontsize=fs)
        
        # temporal 1d
        pylab.subplot(1,2,2)
        pylab.plot(time_vector,kernel[:,44],label='x: 0.0, y: 0.0',linewidth=lw,label=label)
        pylab.xticks(time_ticks[0::time_steps],time_ticks_label[0::time_steps].tolist(),fontsize=fs)
        pylab.yticks(fontsize=fs)
        pylab.xlabel(label_time,fontsize=fs)
        # pylab.ylabel(label_norm,fontsize=fs)
        pylab.ylim(norm_act_lim)
        pylab.legend()
        pylab.title('temporal at 0.0 degree',fontsize=fs)

    if d2:
        pylab.close('all')
        pylab.rcParams['figure.figsize'] = (6.5,6.0)
        pylab.rcParams['figure.facecolor'] = 'white'
        pylab.figure()
        
        pylab.pcolor(kernel.T,vmin=norm_act_lim[0],vmax=norm_act_lim[1],shading='flat')
        pylab.xticks(time_ticks[0::time_steps],time_ticks_label[0::time_steps].tolist(),fontsize=fs)
        pylab.yticks(degree_ticks,degree_ticks_label,fontsize=fs)
        pylab.xlabel(label_time,fontsize=fs)
        pylab.ylabel(label_degree,fontsize=fs)
        pylab.ylim(0,kernel.shape[1])
        cb = pylab.colorbar()
        cb.set_label(label_norm,fontsize=fs)
        pylab.show()
        
def default_parameters():
    # receptive field parameters
    p = ParameterSpace({})
    p.Ac = 1.
    p.As = 1./3.
    p.K1 = 1.05
    p.K2 = 0.7
    p.c1 = 0.14
    p.c2 = 0.12
    p.n1 = 7.
    p.n2 = 8.
    p.t1 = -6. # ms
    p.t2 = -6. # ms
    p.td = 6.0 # time differece between ON-OFF
    p.sigma_c = 0.3#0.4 # Allen 2006 # sigma of center gauss degree
    p.sigma_s = 1.5#p.sigma_c*1.5+0.4 # Allen 2006 # sigma of surround gauss degree
    
    # Kernel dims
    # temporal
    p.size = 10. # degree
    p.degree_per_pixel = 0.1133
    # spatial
    p.dt = 1.0 # ms
    p.duration = 200. # ms
    
    return p


def RF(x,t,p): 
    kernel = Fc(x,p)*Gc(t,p)-Fs(x,p)*Gs(t,p)
    kernel /= kernel.max()
    return kernel

def Fc(x,p):
    return F(x,p.Ac,p.sigma_c)

def Fs(x,p):
    return F(x,p.As,p.sigma_s)

def Gc(t,p):
    return G(t,p)

def Gs(t,p):
    return G(t-p.td,p)

def F(x,A,sigma):
    return A*numpy.exp((-x**2)/(2*sigma**2))

def G(t,p):
    p1 = p.K1*(((p.c1*(t-p.t1))**p.n1)*numpy.exp((-p.c1*(t-p.t1))))/((p.n1**p.n1)*numpy.exp(-p.n1))
    p2 = p.K2*(((p.c2*(t-p.t2))**p.n2)*numpy.exp((-p.c2*(t-p.t2))))/((p.n2**p.n2)*numpy.exp(-p.n2))
    p3 = p1-p2
    return p3
