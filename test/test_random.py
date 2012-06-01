"""
Unit tests for the neurotools.random module

"""

import unittest
from neurotools.random import *

class RandomDistributionTest(unittest.TestCase):
    
    def test_GammaDistFromStats(self):
        g = GammaDist()
        vals = [1,2,3]
        g.from_stats(vals)
        self.assertEqual(g.mean(), numpy.mean(vals))
        self.assertAlmostEqual(g.std(), numpy.std(vals), 10)
        
    def test_GammaDistFromArgs(self):
        g1 = GammaDist(mean=2.0, std=0.5)
        g2 = GammaDist(**{'m': 2.0, 's': 0.5})
        g3 = GammaDist(**{'a': 16.0, 'b': 0.125})
        for g in g1, g2, g3:
            self.assertEqual(g.mean(), 2.0)
            self.assertEqual(g.std(), 0.5)
        
    def test_UniformDistFromStats(self):
        u = UniformDist()
        vals = range(-5, 5)
        u.from_stats(vals)
        outputs = u.next(100)
        assert min(outputs) > -5 # should have >= here?
        assert max(outputs) < 4
        
    def test_ParameterDist(self):
        pd = ParameterDist()
        self.assertRaises(NotImplementedError, pd.next)
        
# ==============================================================================
if __name__ == '__main__':
    unittest.main()
    