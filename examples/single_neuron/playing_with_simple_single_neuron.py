#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Simple demo to:
- produce a spike train using a simulator,
- record the produced spike list to an audio file,
- play it through your loudspeaker!

$Id: playing_with_simple_single_neuron.py 326 2008-11-12 18:49:46Z LaurentPerrinet $
"""
import os, numpy, shelve
import simple_single_neuron as model


def record(output, cfilename = 'SpikeTrain2Play.wav', fs=44100, enc = 'pcm26'):
    """ record the 'sound' produced by a neuron. Takes a spike train as the
    output.

    >>> record(my_spike_train)

    """


    # from the spike list
    simtime_seconds = (output.t_stop - output.t_start)/1000.
    #time = numpy.linspace(0, simtime_seconds , fs*simtime_seconds)
    (trace,time) = numpy.histogram(output.spike_times*1000., fs*simtime_seconds)


    # TODO convolve with proper spike...
    spike = numpy.ones((fs/1000.,)) # one ms

    trace = numpy.convolve(trace, spike, mode='same')#/2.0
    trace /= numpy.abs(trace).max() * 1.1

    try:
        from scikits.audiolab import wavwrite
    except ImportError:
        print "You need the scikits.audiolab package to produce sounds !"
    wavwrite(trace, cfilename, fs = fs, enc = enc)
        

def play(output):
    """
    plays a spike list to the audio output

    play(spike_list) where spike_list is a spike_list object

    see playing_with_simple_single_neuron.py for a sample use

    >>> play(my_spike_train)

    TODO: make it possible to play multiple spike trains in stereo
    """


    from tempfile import mkstemp
    fd, cfilename   = mkstemp('SpikeListPlay.wav')
    try:
        record(output, cfilename)
        import pyaudio
        import wave

        chunk = 1024
        wf = wave.open(cfilename, 'rb')
        p = pyaudio.PyAudio()

        # open stream
        stream = p.open(format =
                        p.get_format_from_width(wf.getsampwidth()),
                        channels = wf.getnchannels(),
                        rate = wf.getframerate(),
                        output = True)

        # read data
        data = wf.readframes(chunk)

        # play stream
        while data != '':
            stream.write(data)
            data = wf.readframes(chunk)

        stream.close()
        p.terminate()
    except:
        print "Error playing the SpikeTrain "
        # finally
        os.remove(cfilename)

    # Python 2.4 compatibility
    # finally:
    os.remove(cfilename)


# in this demo, we generate a simple model
myFibers = model.FiberChannel(N=1)
# generating a simple spike train
output = myFibers.run(myFibers.params)
st = output[0] # the spike train is the first element of the generated spike list
# that we may either record as a WAV file
record(st)
# or directly play with the appropriate library
play(st)
