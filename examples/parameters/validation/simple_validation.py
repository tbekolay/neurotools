import NeuroTools.parameters.validators
import NeuroTools.parameters as ntp

schema = ntp.ParameterSchema("./data/conf_schema1.yaml")
p1 = ntp.ParameterSet("./data/conf1.yaml")
p2 = ntp.ParameterSet("./data/conf2.yaml")

v = ntp.CongruencyValidator()

print v.validate(p1,schema)

# Find first error
try:
    v.validate(p2,schema)
except Exception as e:
    print e
    # correct it
    p2[e.path] = ''

# Find second error
try:
    v.validate(p2,schema)
except Exception as e:
    # 
    print e

