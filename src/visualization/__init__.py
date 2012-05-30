import sys, os.path
import numpy
import tempfile, shutil
import logging
from NeuroTools import check_dependency
from NeuroTools.plotting import progress_bar

if check_dependency('matplotlib'):
    from matplotlib.figure import Figure
    from matplotlib.lines import Line2D
    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
    from matplotlib.image import imread
    import matplotlib.cm



class MultipanelMovie(object):
    
    def __init__(self, title='', frame_duration=40.0):
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        self.panels = []        
        self.title = title
        self.frame_duration = frame_duration
        
    def add_panel(self, obj, bottomleft_corner, width, height):
        """
        obj must be an object that has a string attribute `plot_function` and
        a method `next_frame()`.
        """
        panel = self.fig.add_axes([bottomleft_corner[0], bottomleft_corner[1], width, height])
        self.panels.append((panel, obj))
        return panel
    
    def get_panel(self, obj):
        for panel,_obj in self.panels:
            if obj_ == obj:
                return panel
        return None
    
    def add_text(self, bottomleft_corner, text, **kwargs):
        x, y = bottomleft_corner
        self.fig.text(x, y, text, **kwargs)
    
    def write_frames(self, nframes):
        if nframes >= 1e6:
            raise Exception("Cannot handle movies with 1 million frames or more.")
        self.frame_directory = tempfile.mkdtemp(prefix='tmp_NeuroTools_visualization_')
        time_label = self.fig.text(0.01, 0.01, "t = 0 ms", horizontalalignment='left')
        for i in range(int(nframes)):
            for panel,obj in self.panels:
                assert self.frame_duration == obj.frame_duration, "%s != %s" % (self.frame_duration, obj.frame_duration)
                panel.lines = []; panel.images = []
                plot = getattr(panel, obj.plot_function)
                plot(*obj.next_frame(), **obj.kwargs)
                if obj.plot_function == "imshow" and i==0:
                    pos = panel.get_position()
                    try:
                        l,b,w,h = pos # older versions of Matplotlib
                    except TypeError:
                        l,b,w,h = pos.bounds # newer versions return a Bbox object
                    cb_panel = self.fig.add_axes([l+w, b, 0.05*w, h])
                    self.fig.colorbar(panel.images[0], cb_panel)
            time_label.set_text("t = %g ms" % (i*self.frame_duration,))
            self.canvas.print_figure(os.path.join(self.frame_directory, "frame%06d.png" % i))
            progress_bar(float(i)/nframes)
            
    def __del__(self):
        # when the object is deleted, delete temp directory
        if hasattr(self, 'frame_directory'):
            shutil.rmtree(self.frame_directory, ignore_errors=False)        

    def render(self, filename, fps=25):
        command = "mencoder 'mf://%s/frame*.png' -mf type=png:fps=%d -ovc lavc -lavcopts vcodec=wmv2 -oac copy -o %s" % (self.frame_directory,
                                                                                                                         fps, filename)
        print command
        os.system(command)


class ImageSequence(object):

    plot_function = "imshow"
    
    def __init__(self, frames, frame_duration=40.0, **kwargs):
        self.frames = frames
        self.frame_duration = frame_duration
        self._i = -1
        self.kwargs = {'interpolation': 'nearest'}
        self.kwargs.update(kwargs)
        
    def next_frame(self):
        self._i += 1
        return [self.frames[:,:,self._i]]
    
    
class SineWave(object):

    plot_function = "plot"
    
    def __init__(self, **kwargs):
        self.t = numpy.arange(0, 2*numpy.pi, numpy.pi/20)
        self.phase = numpy.pi/20
        self.kwargs = kwargs
    
    def next_frame(self):
        self.phase -= numpy.pi/20
        return self.t, numpy.sin(self.t + self.phase)

def xy2ij(coordinates, height):
    """
    Generally, we use (x,y) coordinates, but since arrays use matrix coordinates,
    (x,y) <--> (j,i), and so we need to do a flip when putting data into arrays.
    """
    assert len(coordinates) == 2
    x,y = coordinates
    j = x
    i = height - 1 - y
    return (i,j)

class ActivityMap(object):
    
    plot_function = "imshow"
    
    def __init__(self, spikelist, frame_duration=40.0, **kwargs):
        self.spikelist = spikelist
        self.frame_duration = frame_duration
        self.kwargs = kwargs
        if self.spikelist.dimensions is None:
            raise Exception("Dimensions of the population are not defined ! Set spikelist.dims")
        
        self.time, self.ids = self.spikelist.convert("times, ids")
        # We sort the spikes to allow faster process later
        sort_idx = self.time.ravel().argsort(kind="quicksort")
        self.time = self.time[sort_idx]
        self.ids = self.ids[sort_idx]
        self.i = 0
        self.max_i = len(self.time)-1
        self.t_start = 0
        
    def next_frame(self):
        spk = self.spikelist
        activity_map = numpy.zeros(spk.dimensions)
        h,w = spk.dimensions
        id_offset = min(spk.id_list())
        xarr,yarr = spk.id2position(self.spikelist.id_list() - id_offset)
        while (self.i < self.max_i) and (self.time[self.i] < self.t_start + self.frame_duration):
            id = self.ids[self.i] - id_offset
            x = xarr[id]
            y = yarr[id]
            #xy = spk.id2position(self.ids[self.i] - id_offset)
            #assert xy == (x,y), "%s != %s" % (xy, str((x,y)))
            activity_map[xy2ij((x,y), h)] += 1
            self.i += 1
        self.t_start += self.frame_duration
        #logging.debug("next_frame: i=%d, t_start=%g, max_i=%d, time[i]=%g" % (self.i, self.t_start, self.max_i, self.time[self.i]))
        activity_map *= 1000.0/self.frame_duration # convert to spikes/second    
        return [activity_map]
        

def test():
    sine = SineWave()
    movie = MultipanelMovie()
    sine_panel = movie.add_panel(sine, (0.1,0.1), 0.4, 0.4)
    sine_panel.set_title("Sine wave")
    sine_panel.set_xticks(numpy.pi*numpy.arange(0, 2, 0.5))
    
    lena = imread("lena.png")[:,:,0]
    frames = numpy.zeros([lena.shape[0], lena.shape[1], 50])
    for i in range(1,50):
        j = 10*i
        frame = numpy.zeros_like(lena)
        frame[:, :j] = lena[:,-j:]
        frames[:,:,i] = frame
    lena_seq = ImageSequence(frames, cmap=matplotlib.cm.gray)
    lena_panel = movie.add_panel(lena_seq, (0.55, 0.55), 0.4, 0.4)
        
    movie.write_frames(50)
    movie.render("test.mpg", fps=25)
    print movie.frame_directory
    
