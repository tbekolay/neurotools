"""
Unit tests for the NeuroTools.plotting module
"""

import unittest
from NeuroTools import plotting
import pylab
import os



class PylabParamsTest(unittest.TestCase):

    def runTest(self):

        # define arbitrary values
        fig_width_pt =  123.4
        ratio = 0.1234
        text_fontsize = 10 
        tick_labelsize = 8
        useTex = True

        inches_per_pt = 1.0/72.27               # Convert pt to inch
        fig_width = fig_width_pt*inches_per_pt  # width in inches
        fig_height = fig_width*ratio            # height in inches

        testDict = {
            'axes.labelsize'  : text_fontsize,
            'text.fontsize'   : text_fontsize,
            'xtick.labelsize' : tick_labelsize,
            'ytick.labelsize' : tick_labelsize,
            'text.usetex'     : useTex,
            'figure.figsize'  : [fig_width, fig_height]}

        plotting.set_pylab_params(fig_width_pt=fig_width_pt, ratio=ratio, text_fontsize=text_fontsize, \
            tick_labelsize=tick_labelsize, useTex=useTex)
        for k in testDict.keys():
            assert pylab.rcParams.has_key(k)
            assert pylab.rcParams[k] == testDict[k]



class GetDisplayTest(unittest.TestCase):

    def runTest(self):

        a = plotting.get_display(True)
        assert a != None
        a = plotting.get_display(False)
        assert a == None
        a = plotting.get_display(1234)
        assert a == 1234



class ProgressBarTest(unittest.TestCase):

    def runTest(self):

        import time
        print '\nINFO: Testing progress bar...'
        for i in range(100):
            plotting.progress_bar(i/100.)
            time.sleep(.01)
        print '\n'



class Save2DImageTest(unittest.TestCase):

    def runTest(self):

        import numpy
        mat = numpy.random.random([50,50])
        filename = 'deleteme.png'
        if os.path.exists(filename): os.remove(filename)
        plotting.save_2D_image(mat, filename)
        assert os.path.exists(filename)
        os.remove(filename)



class Save2DMovieTest(unittest.TestCase):

    def runTest(self):

        import numpy
        frames = []
        duration = 0.1
        for i in range(10):
            frames.append(numpy.random.randint(0,255,[10,10]))
        filename = 'deleteme.zip'
        if os.path.exists(filename): os.remove(filename)
        plotting.save_2D_movie(frames, filename, duration)
        assert os.path.exists(filename)
        os.remove(filename)



class SetLabelsTest(unittest.TestCase):

    def runTest(self):

        f = plotting.get_display(True)
        x = range(10)
        p = pylab.plot(x)
        plotting.set_labels(pylab, 'the x axis', 'the y axis')

        # set up a SimpleMultiplot with arbitrary values
        self.nrows = 1
        self.ncolumns = 1
        title = 'testMultiplot'
        xlabel = 'testXlabel'
        ylabel = 'testYlabel'
        scaling = ('linear','log')
        self.smt = plotting.SimpleMultiplot(nrows=self.nrows, ncolumns=self.ncolumns, title=title, xlabel=xlabel, ylabel=ylabel, scaling=scaling)
        plotting.set_labels(self.smt.panel(0), 'the x axis', 'the y axis')




class SetAxisLimitsTest(unittest.TestCase):

    def runTest(self):

        f = plotting.get_display(True)
        x = range(10)
        pylab.plot(x)
        plotting.set_axis_limits(pylab, 0., 123., -123., 456.)

        # set up a SimpleMultiplot with arbitrary values
        self.nrows = 1
        self.ncolumns = 1
        title = 'testMultiplot'
        xlabel = 'testXlabel'
        ylabel = 'testYlabel'
        scaling = ('linear','log')
        self.smt = plotting.SimpleMultiplot(nrows=self.nrows, ncolumns=self.ncolumns, title=title, xlabel=xlabel, ylabel=ylabel, scaling=scaling)
        plotting.set_axis_limits(self.smt.panel(0), 0., 123., -123., 456.)



class SimpleMultiplotTest(unittest.TestCase):

    def setUp(self):

        # define arbitrary values
        self.nrows = 4
        self.ncolumns = 5
        title = 'testMultiplot'
        xlabel = 'testXlabel'
        ylabel = 'testYlabel'
        scaling = ('linear','log')
        self.smt = plotting.SimpleMultiplot(nrows=self.nrows, ncolumns=self.ncolumns, title=title, xlabel=xlabel, ylabel=ylabel, scaling=scaling)



class SimpleMultiplotSaveTest(SimpleMultiplotTest):

    def runTest(self):

        filename = "deleteme.png"
        if os.path.exists(filename): os.remove(filename)
        self.smt.save(filename)
        assert os.path.exists(filename)
        os.remove(filename)



class SimpleMultiplotSetFrameTest(SimpleMultiplotTest):

    def runTest(self):

        numPanels = self.nrows * self.ncolumns
        boollist = [True,False,False,True]
        for i in range(numPanels):
            ax_indexed = self.smt.panel(i)
            ax_next = self.smt.next_panel()
            assert ax_indexed == ax_next
            self.smt.set_frame(ax_indexed,boollist,linewidth=4)



if __name__ == "__main__":
    unittest.main()
