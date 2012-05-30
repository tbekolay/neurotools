from NeuroTools.parameters import ParameterSet
from NeuroTools.parameters import ParameterRange
from NeuroTools.parameters import ParameterTable



p = ParameterSet({})
p.orientation = ParameterTable("""
#           RS  RSa RSb FS FSa FSb 
RS          15. 15. 12  13  12  1
FS          15. 15.  9 2    2  9
LGN          0.  12. 0  2  0  0
V2            3.  2. 2   2  9 7
M1            0.  0. 8 2  2   1
""")
p.a = 23
p.b = ParameterSet({})
p.b.s = ParameterRange([1,2,3])
p.b.w = ParameterTable("""
#           RS  FS
all          1. 0.
none         -1. -2.
""")
p.name = 'first experiment'
p.simulator = 'pyNN'



p.export('exportetd_model_parameters.tex',format='latex',**{'indent':1.5})
