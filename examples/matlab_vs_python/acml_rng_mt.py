
import numpy
from scipy import weave

force = 0

def rng_init(seed=1234):
    """ Initializes ACML Mersenne Twister random number generator
    with 1 seed

    (The seed initializes a ACML NAG generator to generate
    the 624 seeds required for the ACML Mersenne Twister algo)
    """
    
    global _state

    code = """

    int seeds[1];
    seeds[0] = seed;
    int lseeds = 1;
    int lstate = 633;
    int info;

    drandinitialize(3,1,seeds,&lseeds,_state,&lstate,&info);

    return_val = info;

    """

    info = weave.inline(code, ['_state','seed'],
                        headers = ['<acml.h>'],
                        libraries = ["acml","acml_mv"],
                        include_dirs = ['/opt/acml4.0.1/gfortran64/include'],
                        library_dirs = ['/opt/acml4.0.1/gfortran64/lib'],
                        force = force)

    if info!=0:
        raise Exception, "Error initializing ACML rng."



# Storage for rng state
_state = numpy.zeros(633,numpy.intc)
rng_init()

def normal(loc=0.0,scale=1.0,size=None):
    """ ACML optimized version of numpy.random.normal """
    global _state

    if size==None:
        size=(1,)

    x = numpy.zeros(size,float)
    n = len(x.flat)

    code = """

    int info;
    int n_ = n;
    double mean_ = loc;
    double var_ = scale; 

    drandgaussian_(&n,&mean_,&var_,_state,x,&info);

    """

    weave.inline(code, ['x','scale','loc','n','_state'],
                 headers = ['<acml.h>'],
                 libraries = ["acml","acml_mv"],
                 include_dirs = ['/opt/acml4.0.1/gfortran64/include'],
                 library_dirs = ['/opt/acml4.0.1/gfortran64/lib'],
                 force = force)


    return x

def uniform(low=0.0,high=1.0,size=None):
    """ ACML optimized version of numpy.random.uniform """
    global _state

    if size==None:
        size=(1,)

    if low>=high:
        raise ValueError, "Error: require low<high"

    x = numpy.zeros(size,float)
    n = len(x.flat)

    code = """

    int info;
    int n_ = n;
    double min_ = low;
    double max_ = high; 

    dranduniform_(&n,&min_,&max_,_state,x,&info);

    """

    weave.inline(code, ['x','low','high','n','_state'],
                 headers = ['<acml.h>'],
                 libraries = ["acml", "acml_mv"],
                 include_dirs = ['/opt/acml4.0.1/gfortran64/include'],
                 library_dirs = ['/opt/acml4.0.1/gfortran64/lib'],
                 force = force)


    return x



def exponential(scale=1.0,size=None):
    """ ACML optimized version of numpy.random.exponential """
    global _state

    if size==None:
        size=(1,)

    x = numpy.zeros(size,float)
    n = len(x.flat)

    code = """

    int info;
    int n_ = n;
    double scale_ = scale;

    drandexponential_(&n,&scale_,_state,x,&info);

    """

    weave.inline(code, ['x','scale','n','_state'],
                 headers = ['<acml.h>'],
                 libraries = ["acml","acml_mv"],
                 include_dirs = ['/opt/acml4.0.1/gfortran64/include'],
                 library_dirs = ['/opt/acml4.0.1/gfortran64/lib'],
                 force = force)


    return x


def randint(low,high=None,size=None):
    """ ACML optimized version of numpy.random.randint """

    global _state

    if size==None:
        size=(1,)

    if high==None:
        high = low
        low = 0

    x = numpy.zeros(size,numpy.intc)
    n = len(x.flat)

    code = """

    int info;
    int n_ = n;
    int low_ = low;
    int high_ = high;

    dranddiscreteuniform_(&n,&low_,&high_,_state,x,&info);

    """

    weave.inline(code, ['x','low','high','n','_state'],
                 headers = ['<acml.h>'],
                 libraries = ["acml","acml_mv"],
                 include_dirs = ['/opt/acml4.0.1/gfortran64/include'],
                 library_dirs = ['/opt/acml4.0.1/gfortran64/lib'],
                 force = force)


    return x

