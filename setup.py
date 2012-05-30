#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "NeuroTools",
    version = "0.2.0dev",
    package_dir={'NeuroTools': 'src'},
    packages = ['NeuroTools',
                'NeuroTools.utilities',
                'NeuroTools.tisean',
                'NeuroTools.spike2',
                'NeuroTools.signals',
                'NeuroTools.spike2.sonpy',
                'NeuroTools.datastore',
                'NeuroTools.parameters',
                'NeuroTools.datastore.django_orm',
                'NeuroTools.optimize',
               ],
    package_data={'NeuroTools': ['doc/*.txt', 'README']},
    author = "The NeuralEnsemble Community",
    author_email = "neurotools@neuralensemble.org",
    description = "A collection of tools to support all tasks associated with a neural simulation project which are not handled by the simulation engine",
    license = "GPLv2",
    keywords = ('computational neuroscience', 'simulation', 'analysis', 'visualization', 'parameters'),
    url = "http://neuralensemble.org/NeuroTools",
    classifiers = ['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'License :: OSI Approved :: GNU General Public License (GPL)',
                   'Operating System :: POSIX',
                   'Topic :: Scientific/Engineering',
                   'Topic :: Utilities',
                  ],
     )
