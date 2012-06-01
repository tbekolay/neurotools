"""
mixedutils.py

Routines and classes for FACETS members and friends.
"""

from neurotools import check_dependency

def save_image(arr, filename):
    assert filename[-3:] == "png"
    import pylab
    fig = pylab.figure()
    pylab.imshow(arr)
    if arr.min() != arr.max():
        pylab.colorbar()
    fig.savefig(filename)



"""
Convert between FACETS movie (image sequence) formats
At the moment, these are:
* zipped directory containing png files, a frames text file and a parameters text file
* HDF5
"""

if check_dependency('neurotools.facets.hdf5'):
    from neurotools.facets.hdf5 import FileExtension as file_extension

from neurotools.facets.fkbtools import png_to_hdf5, hdf5_to_png
import os, sys


def show(url):
    """Display an HDF5 movie."""
    file = file_extension.openHDF5File(url, "r")
    file.showMovie("/Movie")
    file.close()

#===============================================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == 'convert':
            input_file = "file://" + os.path.join(os.getcwd(),sys.argv[2])
            ext = os.path.splitext(input_file)[1]
            if ext == '.h5':
                hdf5_to_png(input_file, input_file.replace('.h5','.zip'))
            elif ext == '.zip':
                png_to_hdf5(input_file, input_file.replace('.zip','.h5'))
            elif ext == '': # directory
                png_to_hdf5(input_file, input_file + '.h5')
        elif sys.argv[1] == 'show':
            show("file://" + os.path.join(os.getcwd(),sys.argv[2]))
        else:
            print "Valid commands are 'convert' and 'show'"
    else:
        print "Usage examples:\n  $ python movieformats.py convert teststim.zip\n  $ python movieformats.py convert teststim1.h5"
