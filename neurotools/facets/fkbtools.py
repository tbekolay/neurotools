"""
Assorted tools relating to the FACETS Knowledge Base (FKB)
$Id: fkbtools.py 131 2007-03-15 08:08:13Z apdavison $
"""

from neurotools import check_dependency

if check_dependency('PIL'):
    import PIL

if check_dependency('tables'):
    import tables

use_hdf5 = check_dependency('neurotools.facets.hdf5')
if use_hdf5:
    import neurotools.facets.hdf5.FileExtension as file_extension
    import neurotools.facets.hdf5.Movie as movie

if check_dependency('srblib'):
    import srblib
else:
    import urllib as srblib

import os, sys, zipfile, tempfile, shutil, subprocess, logging, time, numpy


def getFromURL(url):
    """
    Get a remote file and save in a temporary directory.
    Return the path to the local file.
    """
    tmpdir = tempfile.mkdtemp()
    localfilepath = os.path.join(tmpdir,os.path.basename(url))
    srblib.urlretrieve(url,localfilepath)
    logging.debug('  getFromURL("%s") --> %s' % (url, localfilepath))
    return localfilepath

def getZipURL(url):
    """
    Get the zipfile from the URL and unpack it into a temporary directory.
    Return the temporary directory.
    """
    TIMEOUT = 30 # seconds
    SLEEP = 1 # seconds
    success = -1
    start_time = time.time()
    while success != 0:
        if time.time()-start_time > TIMEOUT:
            raise Exception("Timeout when trying to get zipfile from %s" % url)
        logging.debug('  getZipURL("%s")' % url)
        localfilepath = getFromURL(url)
        tmpdir = os.path.dirname(localfilepath)
        logging.debug('  run process: "unzip -o -q %s -d %s"' % (localfilepath,tmpdir))
        p = subprocess.Popen("unzip -o -q %s -d %s" % (localfilepath,tmpdir), shell=True,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        success = p.wait()
        if success != 0:
            logging.warning("Problem unzipping file: %s %s.\nRetrying %s." % (p.stdout.read(), p.stderr.read(), url))
            time.sleep(SLEEP)
            SLEEP *= 2
    return tmpdir

def _get_frame_list(path):
    f = open(path+"frames",'r')
    frames = f.readlines()
    f.close()
    return [path+f for f in frames]

def _get_parameters(path):
    f = open(path+"parameters",'r')
    parameters = {}
    for line in f.readlines():
        k,v = line.split('=')
        parameters[k.strip()] = v.strip()
    f.close()
    return parameters

def png_to_hdf5(input_url,output_url,title="Movie"):
    """
    Creates a series of frames in png format to FACETS HDF5 format.
    input_url can be a zip file or a local directory containing png files, a
    'frames' text file and a 'parameters' text file.
    """
    if not use_hdf5:
        raise Exception("PyTables not installed.")
    if os.path.splitext(input_url)[1] == '.zip':
        tmp_dir = getZipURL(input_url)
        container = os.listdir(tmp_dir)[0]
        png_dir = '%s/%s/' % (tmp_dir,container)
    else:
        png_dir = input_url.split("//")[1]
        if png_dir[-1] != "/":
            png_dir += '/'
    frames = _get_frame_list(png_dir)
    parameters = _get_parameters(png_dir)
    print "Creating movie file with %d frames, saving to %s" % (len(frames),output_url)
    h5file = file_extension.openHDF5File(output_url, "w", title=title)
    h5file.createCMovie(h5file.root, "Movie", frames, coding=8, complevel=9,
                       frame_duration=parameters['frame_duration'])
    h5file.close()

def hdf5_to_png(input_url,output_url):
    """
    Converts a movie in FACETS HDF5 format to a 'zipped png' format, i.e. a
    zipped folder containing one png file for each frame of the movie, plus a
    'frames' text file listing the png files in the order they appear in the
    movie, and a 'parameters' text file giving the frame_duration parameter.
    """
    if not use_hdf5:
        raise Exception("PyTables not installed.")
    tmpdir_list = []
    assert output_url[-3:] == 'zip', "output_url must point to a zip file"
    assert output_url[0:7] == 'file://', "for now, must be a file:// url"
    input_protocol = input_url.split('://')[0]
    # if remote file, create local copy
    if input_protocol != 'file':
        tmp_dir1 = tempfile.mkdtemp()
        tmpdir_list.append(tmp_dir1)
        srblib.urlretrieve(input_url,tmp_dir1+"/tmp.h5")
        input_url = "file://"+tmp_dir1+"/tmp.h5"
    # process local hdf5 file
    h5file = file_extension.openHDF5File(input_url, 'r')
    if isinstance(h5file.root.Movie, movie.CMovie):
        # export the movie frames as PNG files to a temporary directory
        tmp_dir = tempfile.mkdtemp()
        tmpdir_list.append(tmp_dir)
        mov = h5file.root.Movie
        png_list = mov.export('png','file://' + tmp_dir)
        # create and add movie frames to zip archive
        output_path = output_url.split('//')[1]
        zf = zipfile.ZipFile(output_path,'w',zipfile.ZIP_DEFLATED)
        container = os.path.basename(output_path)[:-4] # remove .zip
        for pngfile in png_list:
            arcname = "%s/%s" % (container,os.path.basename(pngfile))
            zf.write(pngfile,arcname)
        # add 'parameters' and 'frames' files to the zip archive
        zf.writestr("%s/parameters" % container,
                    'frame_duration = %s' % mov.attrs.FRAME_DURATION)
        zf.writestr("%s/frames" % container,
                    '\n'.join([os.path.basename(p) for p in png_list]))
        zf.close()
    else:
        raise Exception("Specified node is not a Movie")
    h5file.close()
    # remove the temporary directories
    for tmpdir in tmpdir_list:
        shutil.rmtree(tmpdir)

def getStimulus(url):
    """
    Get the stimulus in either zip(png) or hdf5 format, unpack individual frames
    into a temporary directory, and return the temp directory, a file containing
    a list of frames, and the frame duration.
    """
    tmpdir1 = tempfile.mkdtemp()
    if url[-3:] == ".h5":
        try:
            hdf5_to_png(url,"file://%s/tmpstim.zip" % tmpdir1)
            url = "%s/tmpstim.zip" % tmpdir1
        except IOError: # not an hdf5 file, or some other problem.
            pass
    tmpdir = getZipURL(url)
    dirlist = [f for f in os.listdir(tmpdir) if f.find(".zip") < 0 and f.find("MACOSX") < 0]
    if len(dirlist) == 1:
        topdir = os.path.join(tmpdir, dirlist[0])
    else:
        raise Exception("Problem obtaining stimulus. Contents of %s: %s" % (tmpdir, os.listdir(tmpdir)))
    frame_list = (os.path.join(topdir,"frames"),topdir)
    f = open(os.path.join(topdir,"parameters"),'r') # parameteters should contain the frame_duration parameter
    for line in f.readlines():
        if line.find('frame_duration') == 0:
            exec(line)
            break
    f.close()
    shutil.rmtree(tmpdir1)
    return (tmpdir,frame_list,frame_duration)

def txt_to_hdf5(input_url,output_url):
    """
    Convert a data file in ascii format to a simple HDF5 file containing a
    single table. The data file should contain numerical data in columns
    separated by spaces and/or tabs.
    Lines beginning with '#' are taken to be comments.
    Column headings can be specified as a comment on the first line of the file.

    Example:
    # time voltage
    0.0  -65.0
    0.1  -64.8
    """
    if not use_hdf5:
        raise Exception("PyTables not installed.")
    f = srblib.urlopen(input_url)
    contents = f.readlines()
    f.close()

    # extract header information
    firstline = contents[0]
    headers = []
    udict = {}
    if firstline[0] == '#':
        if '"' in firstline:
            headers = [h.strip() for h in firstline[1:].split('"') if h and h.strip()]
        else:
            headers = firstline[1:].split()
        for h,colname in enumerate(headers):
            # check for units
            p = colname.find("(")
            if p > 0:
                units = colname[p:]
                colname = colname[:p].strip().replace(" ","_")
                udict[colname] = units
            headers[h] = colname.strip().replace(" ","_")
    secondline = contents[1]
    nfields = len(secondline.split())
    if len(headers) != nfields:
        headers = ['col%d' % i for i in range(1,nfields+1)]

    # create row format
    class_str = "class DataRow(tables.IsDescription):\n"
    for pos,colname in enumerate(headers):
        class_str += "  %s = tables.Float32Col(pos=%d)\n" % (colname,pos)
    exec(class_str)

    # create HDF5 file
    protocol, path = output_url.split('://')
    path,ext = os.path.splitext(path)
    filename = os.path.basename(path)
    assert protocol == 'file', "For now, we only support writing to local files."
    h5file = tables.openFile('%s.h5' % path, mode='w', title=filename)

    # create and fill table
    table = h5file.createTable(h5file.root, filename, DataRow, "Converted from %s" % input_url)
    for k,v in udict.items():
        table.attrs.__setattr__("units_%s" % k,v)
    for line in contents[1:]:
        line = line.strip()
        data = [float(x) for x in line.split()]
        row = table.row
        for col,val in zip(headers,data):
            row[col] = val
        row.append()
    table.flush()

    h5file.close()

def hdf5_to_txt(input_url,output_url,spacer=" "):
    """
    Convert a simple HDF5 file (one table as a child of the root node) to text
    format, with columns separated by 'spacer'.
    """
    if not use_hdf5:
        raise Exception("PyTables not installed")
    # Open hdf5 file and get table
    path = getFromURL(input_url)
    h5file = tables.openFile(path, mode='r')
    assert len(h5file.listNodes(h5file.root,classname="Table")) == 1, "File contains more than one table."
    table = h5file.listNodes(h5file.root,classname="Table")[0]

    # Open and write to text file
    protocol, path = output_url.split('://')
    txtfile = open(path,'w')
    colnames = table.colnames
    ncols = len(colnames)
    txtfile.write("# " + spacer.join(colnames) + "\n")
    # add units to header if they are available in the table attributes
    #    (TO-DO)
    for row in table:
        values = [0]*ncols
        for i,colname in enumerate(colnames):
            values[i] = str(row[colname])
        txtfile.write(spacer.join(values)+'\n')

    txtfile.close()
    h5file.close()

def getData(url):
    """
    Get tabular data from either a text file or HDF5 table, and return it as a
    numpy array.
    """
    path = getFromURL(url)
    if use_hdf5 and tables.isHDF5File(path):
        h5file = tables.openFile(path, mode='r')
        assert len(h5file.listNodes(h5file.root,classname="Table")) == 1, "File contains more than one table."
        table = h5file.listNodes(h5file.root,classname="Table")[0]
        arr = numpy.zeros((table.nrows,len(table.colnames)),'float')
        for i,row in enumerate(table):
            for j,colname in enumerate(table.colnames):
                arr[i,j] = row[colname]
    elif os.path.isfile(path):
        f = srblib.urlopen(url)
        arr = numpy.array([l.split() for l in f.readlines() if l[0] != '#']).astype('float')
        f.close()
    else:
        raise Exception("Not a valid file.")
    return arr
