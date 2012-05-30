"""
A higher-level wrapper round the srb module.
Also implements some urllib-like functionality, allowing SRB URLs

Some alternatives:
http://www.cheshire3.org/docs/objects/api/srboo-pysrc.html
http://plone.jcu.edu.au/hpc/staff/projects/hpc-software/SRBpy
http://sourceforge.net/projects/pysrb/

There are some good build instructions for the low-level bindings at:
http://www.vislab.uq.edu.au/research/accessgrid/virtual_fs/building.htm

If building on OS X, I found this useful:
https://lists.sdsc.edu/pipermail/srb-chat/2007-November/004506.html

Andrew Davison, UNIC, CNRS
"""

import srb
import urlparse
urlparse.uses_netloc.append('srb')
import urllib
import os

META_NAME = 0
META_PARENT = 1
META_SIZE = 2
META_TYPE = 3
META_OWNER = 4
META_TIMESTAMP = 5
META_REPLICA = 6
META_RESOURCE = 7
MB = 1024*1024
BUFFER_SIZE = 20*MB # must be less than sys.maxint

def get_MdasEnv(filename=os.path.join(os.path.expanduser("~"), ".srb/.MdasEnv")):
    try:
        f = open(filename, 'r')
    except IOError, msg:
        print "Warning: %s" % msg
        connection_dict = {}
    else:
        mdasenv = {}
        for line in f.readlines():
            k,v = line.split()
            mdasenv[k] = eval(v)
        connection_dict = {'host': mdasenv['srbHost'],
                           'domain': mdasenv['mdasDomainHome'],
                           'username': mdasenv['srbUser'],
                           'password': mdasenv['password'],
                           'default_resource': mdasenv['defaultResource'],                      
        }
        f.close()
    return connection_dict

DEFAULT_CONNECTION = get_MdasEnv()

class SRBFileError(Exception):

    def __init__(self, dir, filename, mode, error_code, extra_msg=''):
        self.path = "%s/%s" % (dir, filename)
        self.mode = mode
        self.errormsg = srb.get_error(error_code) + " " + extra_msg
    
    def __str__(self):
        return "Could not %s SRB file %s (%s)" % (self.mode,
                                                  self.path,
                                                  self.errormsg)

class SRBConnectionError(Exception): pass


class SRBConnection(object):
    
    def __init__(self, host, port="", domain="", username="",
                 password=""):
        """
        Create a connection to an SRB server.
        Disconnection is automatic when the object is destroyed
        (e.g. on program exit).
        """
        if DEFAULT_CONNECTION and host == DEFAULT_CONNECTION['host']:
            domain = domain or DEFAULT_CONNECTION['domain']
            username = username or DEFAULT_CONNECTION['username']
            password = password or DEFAULT_CONNECTION['password']
        self.id = srb.connect(host, port, domain, "ENCRYPT1", username, password, "")
        if self.id < 0:
            raise SRBConnectionError("Could not connect to %s" % host)
        
    def __del__(self):
        srb.disconnect(self.id)
        
        
class SRBFileSystem(object):
    """
    An interface for browsing/navigating a directory structure on an SRB server.
    """
    
    def __init__(self, host, port="", domain="", username="",
                 password="", root="", default_resource=""):
        """
        A connection to the SRB server is established when an SRBServer object
        is created. Disconnection is automatic when the object is destroyed
        (e.g. on program exit).
        """
        self._connection = SRBConnection(host, port, domain, username, password)
        self._root = root
        self._pathoffset = len(self._root)
        self.default_resource = default_resource
        if not default_resource:
            if DEFAULT_CONNECTION:
                self.default_resource = DEFAULT_CONNECTION['default_resource']
        self.pwd = "/"
    
    def __del__(self):
        del(self._connection)
    
    def ls(self, path=''):
        """List the contents of the current directory/collection."""
        if path == '':
            full_path = self._root + self.pwd
        elif path[0] != '/':
            full_path = self._root + self.pwd + '/' + path
        else:
            full_path = path
        full_path = "/" + full_path.strip("/")
        ##print full_path
        c = self._connection.id
        contents = []
        for i in range(srb.get_subcolls(c, 0, full_path)):
            dirname = srb.get_subcoll_name(c,i)
            if path == '' or path[0] != '/':
                cut_initial = self._pathoffset + len(self.pwd) + 1
                if self.pwd == '/':
                    cut_initial -= 1
                dirname = dirname[cut_initial:]
            else:
                dirname = dirname[self._pathoffset:]                
            contents.append(dirname + "/")
        for i in range(srb.get_objs_in_coll(c, 0, 0, full_path)):
            filename = srb.get_obj_metadata(c, META_NAME, i)
            if path != '' and path[0] == '/':       
                filename = full_path + '/' + filename    
            contents.append(filename)
        return contents
            
    def rm(self, filename):
        """Delete a file in the current directory/collection."""
        path = self._root + self.pwd
        c = self._connection.id
        ##print c, filename, path
        status = srb.obj_delete(c, filename, 0, path)
        if status < 0:
            return SRBFileError(self.pwd, filename, 'delete', status)
        
    def cd(self,dir):
        """
        Change the current directory.
        Currently there is no check that the directory (collection) actually exists.
        """
        if dir[0] == "/":
            self.pwd = dir
        else:
            self.pwd = self.pwd + "/" + dir
        self.pwd = "/" + self.pwd.strip("/") # strip off trailing '/' and make sure there is only a single '/' at the start
    
    def open(self, filename, mode='r', resource=''):
        """
        Open a file in the current directory. If the file does not exist, it is
        created.
        """
        resource = resource or self.default_resource
        return SRBFile(self._connection, os.path.join("/", self._root, self.pwd[1:], filename), resource, mode)
            
    def get(self, srbfilename, localpath=''):
        """
        Save an SRB file to the local file system.
        
        srbfile should be a file name in the current directory/collection.
        There is no warning if the local file already exists.
        """
        # open the SRB file
        assert srbfilename.find("/") < 0 # srbfilename should be a file name, not a path
        srbfile = self.open(srbfilename, mode='r')
        # open the local file
        localpath = localpath or srbfilename
        local_file = open(localpath,'wb')
        # write the SRB file contents to the local file
        local_file.write(srbfile.read())
        # close all files
        local_file.close()
        srbfile.close()
    
    def put(self, localpath, srbfilename, resource=''):
        """
        Copy a local file to the current directory on the SRB server. If a file
        with the same name already exists, it is deleted before the new file is
        copied.
        """
        assert srbfilename.find("/") < 0 # srbfilename should be a file name, not a path
        resource = resource or self.default_resource
        self.rm(srbfilename) # this is not very nice. Should really check if a file with the same name already exists
                             # and have a flag which determines whether to raise an Exception or overwrite the file
                             # also, the file should be first copied to a temporary name and only deleted if the upload
                             # succeeds.
        srbfile = self.open(srbfilename, mode='w', resource=resource)      
        local_file = open(localpath, 'r')
        srbfile.write(local_file.read())
        local_file.close()
        srbfile.close()
        
            
class SRBFile(object):
    """Limited file-like object."""
    
    def __init__(self, connection, path, resource='', mode='r'):
        self._connection = connection
        (self.path, self.filename) = os.path.split(path)
        c = self._connection.id
        if mode == 'w': # we delete the existing file first - see comments in "put()" above on how this needs to be improved.
            status = srb.obj_delete(c, self.filename, 0, self.path)
        # first try to open the file
        self.id = srb.obj_open(c, self.path, self.filename, 0)
        # if we get an error, try to create a new file
        # should really check it is the right kind of error...
        if self.id < 0:
            cat_type = 0
            data_type = ''
            path_name = ''
            data_size = 0
            if mode == 'r':
                raise SRBFileError(self.path, self.filename, 'open', self.id)
            else:
                print "File %s in %s does not exist. Trying to create it." % (self.filename, self.path)
                self.id = srb.obj_create(c, cat_type, self.filename, data_type,
                                         resource, self.path, path_name, data_size)
                if self.id < 0:
                    raise SRBFileError(self.path, self.filename, 'open or create', self.id)
        else:
            print "Opened file %s in %s" % (self.filename, self.path)

    def read(self, limit=1e8):
        if self._connection is None:
            raise Exception("File has been closed, and so cannot be read.")
        content = ''
        c = self._connection.id
        s = srb.obj_read(c, self.id, min(BUFFER_SIZE, limit))
        while len(s) > 0 and len(content) < limit:
            content += s
            s = srb.obj_read(c, self.id, BUFFER_SIZE)
        return content
    
    def readlines(self):
        return self.read().strip().split("\n")
    
    def write(self, content):
        if self._connection is None:
            raise Exception("File has been closed, and so cannot be written to.")
        c = self._connection.id
        bytes_written = srb.obj_write(c, self.id, content, len(content))
        if bytes_written < 0:
            raise SRBFileError(self.path, self.filename, 'write', bytes_written)
        else:
            return bytes_written
    
    def close(self):
        srb.obj_close(self._connection.id, self.id)
        self._connection = None
        
# urllib-equivalent functionality for SRB URLs, which are not supported by urllib
# SRB URI protocol from http://www.sdsc.edu/srb/jargon/SRBURI.html
# srb:// [ userName . domainHome [ : password ] @ ] host [ : port ][ / path ]
# e.g. srb://fkbUser@facets.inria.fr/WP5/Benchmarks/Retina/EnRo66_Fig1_X/phase0deg.zip

def urlopen(url):
    protocol,host,path = urlparse.urlsplit(url)[0:3]
    connection_dict = {}
    if '@' in host:
        username, host = host.split("@")
        if ':' in username:
            username, password = username.split(":")
            connection_dict['password'] = password
        if '.' in username:
            username,domain = username.split(".")
            connection_dict['domain'] = domain
            connection_dict['username'] = username
    connection_dict['host'] = host
    if protocol == 'srb':
        connection = SRBConnection(**connection_dict)
        return SRBFile(connection, path)
    else:
        return urllib.urlopen(url)

def urlretrieve(url,localfilename):
    protocol,host,path = urlparse.urlsplit(url)[0:3]
    if protocol == 'srb':
        srbf = urlopen(url)
        localf = open(localfilename,'wb')
        localf.write(srbf.read())
        localf.close()
        srbf.close()
    else:
        urllib.urlretrieve(url,filename=localfilename)