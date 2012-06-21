Module maintainers
==================

Ideally, each module should have approx. two maintainers.

+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``signals``:      | Pierre Yger, `LaurentPerrinet </trac/NeuroTools/wiki/LaurentPerrinet>`_, Jens Kremkow (others volunteers are more than welcome)   |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``parameters``:   | Andrew Davison                                                                                                                    |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``io``:           | Pierre Yger and ...                                                                                                               |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``plotting``:     | Daniel Bruederle                                                                                                                  |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``analysis``:     | Eilif Muller                                                                                                                      |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``utilities``:    | Daniel Bruederle                                                                                                                  |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``stgen``:        | Eilif Muller, Michael Schmuker                                                                                                    |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``examples``:     | `LaurentPerrinet </trac/NeuroTools/wiki/LaurentPerrinet>`_                                                                        |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``spike2``:       | Jens Kremkow                                                                                                                      |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+
| ``datastore``:    | Andrew Davison                                                                                                                    |
+-------------------+-----------------------------------------------------------------------------------------------------------------------------------+

Maintainers are responsible for

-  identifying missing functionality/tests/docs in their module
-  writing tickets using the Trac
   (`https://neuralensemble.org/trac/NeuroTools/newticket <https://neuralensemble.org/trac/NeuroTools/newticket>`_)
-  finding volunteers to write the code/tests/docs

**Documentation manager**: Pierre Yger

+-------------------------------+--------------------+
| giving the trac a new look:   | Eilif Muller       |
+-------------------------------+--------------------+
| advertising:                  | Laurent Perrinet   |
+-------------------------------+--------------------+

*Responsibilities*: combining the documentation from the different
modules into a coherent whole, ensuring consistent formatting,
spell-checking, etc.

**Testing manager**: Andrew Davison

*Responsibilities*:

-  identifying areas of the codebase that are not well tested, and
   notifying the module maintainers
-  organizing/collecting tests that use several of the
   `NeuroTools </trac/NeuroTools/wiki/NeuroTools>`_ modules, i.e.
   integration tests rather than unit tests.

**Packaging manager**: Eric Mueller

*Responsibilities*:

-  setup.py, i.e. making sure that distutils installation works.
-  uploading packages to PyPI, software.incf.org, etc.
-  evaluating whether easy\_install would work for
   `NeuroTools </trac/NeuroTools/wiki/NeuroTools>`_
