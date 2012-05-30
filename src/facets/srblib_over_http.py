import httplib,string,base64

class SRBServer(object):
    """
    Abstraction of an SRB server, providing a higher-level wrapper around the
    rather low-level API in the srb module.
    """
    
    def __init__(self,host="facets.inria.fr",port="",domain="FacetsDomain",
                 username="fkbUser",password="viveFKB",root="/INRIA/home/INRIA"):
        temp = "%s:%s" % (username,password)
        temp = base64.encodestring(temp)
        self._auth = "Basic %s" % string.strip(temp)
        self._root = root
        self._pathoffset = len(self._root)
        self.pwd = ""
        
    def __del__(self):
        pass
    
    def _downloadConnection(self,srbfilename):
        conn = httplib.HTTPS('facets.inria.fr')
        #if it is an absolute path
        if(srbfilename.startswith('/')):
            conn.putrequest('GET', '/SRB/SRBDownload?file=%s' % (srbfilename))
            print ('sending request /SRB/SRBDownload?file=%s' % (srbfilename))
        #if not, add root and pwd before
        else:
            conn.putrequest('GET', '/SRB/SRBDownload?file=%s/%s/%s' % (self._root,self.pwd,srbfilename))
            print ('sending request  /SRB/SRBDownload?file=%s/%s/%s' % (self._root,self.pwd,srbfilename))
        conn.putheader('Accept', 'application/octet-stream')
        conn.putheader("Authorization",self._auth)
        conn.endheaders()
        return conn

    def ls(self):
        """List the contents of the current directory/collection."""
        conn = httplib.HTTPS('facets.inria.fr')
        conn.putrequest('GET', '/SRB/SRBManageFiles?action=getChildren&subDir=%s/%s' % (self._root,self.pwd))
        print ('sending request /SRB/SRBManageFiles?action=getChildren&subDir=%s/%s' % (self._root,self.pwd))
        conn.putheader('Accept', 'text/html')
        conn.putheader('Accept', 'text/xml')
        conn.putheader('Accept', 'text/plain')
        conn.putheader("Authorization",self._auth)
        conn.endheaders()
        
        # Get the answer
        errcode, errmsg, headers = conn.getreply()
        
        f=conn.getfile()
        for line in f.readlines():
            print line
    
    def cd(self,dir):
        """
        Change the current directory.
        Currently there is no check that the directory (collection) actually exists.
        """
        if dir[0] == "/":
            self.pwd = dir
        else:
            self.pwd = self.pwd + "/" + dir
        if self.pwd[-1] == "/": # strip off trailing '/'
            self.pwd = self.pwd[:-1]
        if self.pwd[0] == "/": # strip off beginning '/'
            self.pwd = self.pwd[1:]  
    
    def get(self,srbfilename,localpath):
        """
        Save an SRB file to the local file system.
        
        srbfile should be a file name in the current directory/collection.
        There is no warning if the local file already exists.
        """
        # open the SRB file
        assert srbfilename.find("/") < 0 # srbfilename should be a file name, not a path
        
        conn = self._downloadConnection(srbfilename)
        
        # Get the answer
        errcode, errmsg, headers = conn.getreply()
        if errcode != 200:
            raise SRBError("Could not open SRB file %s (http error code %d)" % (srbfilename,errcode))
        # open the local file
        local_file = open(localpath,'wb')
        # write the SRB file contents to the local file
        local_file.write(conn.getfile())
        # close all files
        local_file.close()

# urllib-equivalent functionality for SRB URLs, which are not supported by urllib
# SRB URI protocol from http://www.sdsc.edu/srb/jargon/SRBURI.html
# srb:// [ userName . domainHome [ : password ] @ ] host [ : port ][ / path ]
# e.g. srb://fkbUser@facets.inria.fr/INRIA/home/INRIA/WP5/Benchmarks/Retina/EnRo66_Fig1_X/phase0deg.zip
# or srb://fkbUser@facets.inria.fr/WP5/Benchmarks/Retina/EnRo66_Fig1_X/phase0deg.zip (root will be added)
# 

class SRBFile(object):
    """Very limited file-like object."""
    
    def __init__(self,path,host="facets.inria.fr",port="",domain="FacetsDomain",
                 username="fkbUser",password="viveFKB",root="/INRIA/home/INRIA"):
        self.server = SRBServer(host,port,domain,username,password,root)
        (self.path,self.filename) = os.path.split(path)
        #add the root folder to the path if not already done
        if not(self.path.startswith(self.server._root)):
            if self.path[0] == "/":
                self.path = self.path[1:]
            self.path = os.path.join(self.server._root,self.path)
        self.srbfilename = os.path.join(self.path,self.filename)
    
    def read(self):
        conn = self.server._downloadConnection(self.srbfilename)
         # Get the answer
        errcode, errmsg, headers = conn.getreply()
        return conn.getfile().read()
    
    def readlines(self):
        return self.read().strip().split("\n")
    
    def close(self):
        pass
