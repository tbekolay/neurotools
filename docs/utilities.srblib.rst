===============================
The ``utilities.srblib`` module
===============================

SRB_ ("Storage Resource Broker") is a distributed filesystem, developed by the
San Diego Supercomputer Center, and intended for "Grid" applications, where
geographically-separated groups need to share large quantities of data.

SRB comes with a client Python library, but this is very low level, and the API
is not very Pythonic. This module aims to provide a more useable interface to
SRB, allowing you to treat an SRB system more like a local filesystem.

Various alternative high-level SRB Python interfaces are available: srboo_,
SRBpy_ and pysrb_. These mostly offer more features than `srblib`, but I didn't
succeed in getting any of them up-and-running, so here is another one.

Installing the low-level ``srb`` module
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

There are some good build instructions for the low-level bindings at:
`<http://www.vislab.uq.edu.au/research/accessgrid/virtual_fs/building.htm>`_

If building on OS X, I found this useful:
`<https://lists.sdsc.edu/pipermail/srb-chat/2007-November/004506.html>`_

Make sure you create a directory called ``.srb`` in your home directory and, in
this directory, a file called ``.MdasEnv``, which should look something like this::
    
    mdasCollectionHome '/home/srbdev.sdsc'
    mdasDomainHome 'sdsc'
    srbUser 'srbdev'
    srbHost 'torah.sdsc.edu'
    defaultResource 'unix-sdsc'
    AUTH_SCHEME 'ENCRYPT1'
    
Check your configuration works using the "Scommands_" before trying the Python
interface. You will find full details on the `SRB website`__.

Browsing an SRB filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~

If you have your ``.MdasEnv`` file setup correctly, you can connect to an SRB
server using::

    >>> from NeuroTools.utilities.srblib import *
    >>> S = SRBFileSystem('facets.inria.fr')
    
(It is also possible to override the contents of ``.MdasEnv``, or even to have
no such file at all, by passing the connection parameters (``username``,
``password``, etc) as keyword arguments to the constructor.) You can now browse
the server using method calls similar to the Unix command-line, e.g.::

    >>> S.ls()
    ...
    >>> S.cd("/INRIA/home/INRIA/WP5")
    >>> S.ls()
    >>> S.get("srbtestfile", "/tmp/localfile")
    >>> S.put("/tmp/localfile", "srbtestfile_copy")

You can also open files and read to/write from them more-or-less as if they were
on your local filesystem::

    >>> f = S.open("srbtestfile2", "w")
    >>> f.write("Mate, this bird wouldn't 'voom' if you put four million volts through it!\n")
    >>> f.close()
    >>> f = S.open("srbtestfile2", "r")
    >>> print f.read()
    Mate, this bird wouldn't 'voom' if you put four million volts through it!
    >>> f.close()

Accessing files by URL
~~~~~~~~~~~~~~~~~~~~~~

This part of the interface was inspired by `urllib`_ from the Python standard
library. There is no need to create an ``SRBServer`` object, just pass an
"``srb://``" URL to the ``urlopen`` or ``urlretrieve`` functions::

    >>> f = urlopen("srb://facets.inria.fr/INRIA/home/INRIA/WP5/srbtestfile2")
    >>> print f.read()
    Mate, this bird wouldn't 'voom' if you put four million volts through it!
    >>> f.close()


.. _SRB: http://www.sdsc.edu/srb/index.php/Main_Page
.. _srboo: http://www.cheshire3.org/docs/objects/api/srboo-pysrc.html
.. _SRBpy: http://plone.jcu.edu.au/hpc/staff/projects/hpc-software/SRBpy
.. _pysrb: http://sourceforge.net/projects/pysrb/
.. _urllib: http://docs.python.org/lib/module-urllib.html
.. _Scommands: http://www.sdsc.edu/srb/index.php/Scommands

__ SRB_