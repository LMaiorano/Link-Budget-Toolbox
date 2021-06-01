import unittest
from project.unit_conversion import to_base_SI, to_prefixed_SI, freq_to_wavelength, wavelength_to_freq


class UnitConversionTests(unittest.TestCase):
    def test_base_SI(self):
        in_val  = 300
        in_unit = 'km'

        out_val = to_base_SI(in_val, in_unit)
        ref_val = 300e3

        self.assertEqual(ref_val, out_val)


    def test_base_SI_freq(self):
        in_val  = 300
        in_unit = 'kHz'

        out_val = to_base_SI(in_val, in_unit)
        ref_val = 300e3

        self.assertEqual(ref_val, out_val)


    def test_prefix_SI(self):
        in_val = 750e-9
        desired_unit = 'nm'

        out_val = to_prefixed_SI(in_val, desired_unit)

        ref_val = 750

        self.assertAlmostEqual(ref_val, out_val, 8)


    def test_prefix_SI_freq(self):
        in_val = 750e6
        desired_unit = 'MHz'

        out_val = to_prefixed_SI(in_val, desired_unit)

        ref_val = 750

        self.assertAlmostEqual(ref_val, out_val, 8)


    def test_freq_wavelength(self):
        freq1 = 500         # Hz
        wavelen1 = 599584.9   # m

        freq2 = 1000        # Hz
        wavelen2 = 299792.5   # m

        self.assertAlmostEqual(freq_to_wavelength(freq1), wavelen1, 0)
        self.assertAlmostEqual(freq_to_wavelength(freq2), wavelen2, 0)

    def test_wavelength_freq(self):
        freq1 = 500  # Hz
        wavelen1 = 599584.9  # m

        freq2 = 1000  # Hz
        wavelen2 = 299792.5  # m

        self.assertAlmostEqual(wavelength_to_freq(wavelen1), freq1, 0)
        self.assertAlmostEqual(wavelength_to_freq(wavelen2), freq2, 0)




if __name__ == '__main__':
    unittest.main()
