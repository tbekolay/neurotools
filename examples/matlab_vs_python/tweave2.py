import scipy
import scipy.weave as weave
import numpy
import numpy.random as random
from time import time

n = 10000000
a = numpy.arange(n,dtype=float)
b = random.uniform(size=n)
c1 = zeros_like(a)
c2 = zeros_like(a)
c3 = zeros_like(a)


def f_opt_c(a,b,c):

    code = r"""


    // this simplified form is only ok for contiguous arrays, non-strided ...
    // i.e. Sa[0]==Sb[0]==Sc[0]

    double* da = (double*)a;
    double* db = (double*)b;
    double* dc = (double*)c;

    for(int i=0;i<Na[0];++i) {
      *(dc+i) = *(da+i)* *(db+i);
    }

    """


    weave.inline(code,['a','b','c'])


def f_c(a,b,c):

    code = r"""


    int ia = 0;
    int ib = 0;
    int ic = 0;

    for(int i=0;i<Na[0];++i) {
      ia+=Sa[0]; ib+=Sb[0]; ic+=Sc[0];
      *(double*)((char*)c+ic) = *(double*)((char*)a+ia) * *(double*)((char*)b+ib);
    }

    """


    weave.inline(code,['a','b','c'])


def f_macro(a,b,c):

    code = r"""


    #define GET(ARR,IDX,TYPE) (*(TYPE*)( ((char*)ARR)+(IDX) * S ## ARR[0]))

    for(int i=0;i<Na[0];i++) {
      GET(c,i,double) = GET(a,i,double) * GET(b,i,double);
    }

    """


    weave.inline(code,['a','b','c'])

def f_blitz(a,b,c):

    code = r"""


    for(int i=0;i<Na[0];i++) {
      c(i) = a(i)*b(i);
    }

    """


    weave.inline(code,['a','b','c'], type_converters=weave.converters.blitz)



t1 = time()
f_opt_c(a,b,c1)
t2 = time()
print '*double: ', t2-t1

t1 = time()
f_c(a,b,c1)
t2 = time()
print 'strided *double: ',t2-t1

t1 = time()
f_macro(a,b,c2)
t2 = time()
print 'macro: ',t2-t1

t1 = time()
f_blitz(a,b,c3)
t2 = time()
print 'blitz: ',t2-t1




