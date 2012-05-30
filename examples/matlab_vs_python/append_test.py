import time
import numpy

n = 100000

print 'n=',n
# fill a list


t1 = time.time()

l = []

for i in xrange(n):
	l.append(1.0)
	
t2 = time.time()

print 'list append: ',t2-t1


# fill an array by concatenation

t1 = time.time()

a = array([])
for i in xrange(n):
	a = numpy.concatenate((a,[1.0]))

t2 = time.time()

print 'numpy.concatentate ',t2-t1


# fill an array by resizing self

t1 = time.time()

a = array([])
for i in xrange(n):
	a.resize(len(a)+1)
	a[-1] = 1.0

t2 = time.time()

print 'a.resize', t2-t1


# fill an array by resize function

t1 = time.time()

a = array([])
for i in xrange(n):
	a = numpy.resize(a,len(a)+1)
	a[-1] = 1.0

t2 = time.time()

print 'a=numpy.resize(a,n) ', t2-t1


# fill an array without resize

t1 = time.time()

a = zeros(n)
for i in xrange(n):
	a[i] = 1.0

t2 = time.time()

print 'fill array of known size ',t2-t1

# fill an array with append

t1 = time.time()

a = array([])
for i in xrange(n):
	a = append(a,1.0)

t2 = time.time()

print 'numpy.append ', t2-t1

