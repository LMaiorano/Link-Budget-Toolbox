import unittest
from project.unit_conversion import base_SI, prefixed_SI


class MyTestCase(unittest.TestCase):
    def test_base_SI(self):
        in_val  = 300
        in_unit = 'km'

        out_val, out_unit = base_SI(in_val, in_unit)
        ref_val = 300e3
        ref_unit = 'm'

        self.assertEqual(ref_val, out_val)
        self.assertEqual(ref_unit, out_unit)

    def test_prefix_SI(self):
        in_val = 750e-9
        desired_unit = 'nm'

        out_val, out_unit = prefixed_SI(in_val, desired_unit)

        ref_val = 750
        ref_unit = 'nm'

        self.assertAlmostEqual(ref_val, out_val, 8)
        self.assertEqual(ref_unit, out_unit)



if __name__ == '__main__':
    unittest.main()
