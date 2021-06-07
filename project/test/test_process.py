import unittest
import filecmp
import os
from project.process import read_user_data, fill_results_data, load_from_yaml, \
    main_process, save_to_yaml


class ProcessTestCase(unittest.TestCase):
    # TODO: Use dics/df from txt/csv/??? file instead of hardcoding in this script
    # TODO: find setup / teardown? to limit crosscontamination test variables between unit tests
    # TODO: Check for tests to fail, skip next tests, as it is chronological.

    def setUp(self):
        self.maxDiff = None
        self.tmp_fname = 'ref_data/tmp_saved.yaml'       # Temporary file to save to if using filecmp

        self.data_bare_minimum = load_from_yaml('ref_data/bare_minimum.yaml')
        self.data_generic_only = load_from_yaml('ref_data/generic_only.yaml')

        self.data_test_user_data = load_from_yaml('ref_data/user_data.yaml')
        self.ref_user_data = load_from_yaml('ref_data/ref_user_data.yaml')

        self.unit_converted_user_data = load_from_yaml('ref_data/unit_converted_user_data.yaml')
        self.ref_fill_results_data = load_from_yaml('ref_data/ref_fill_results_data.yaml')

    def tearDown(self):
        if os.path.exists(self.tmp_fname): # Remove temp saved file if it exists
            os.remove(self.tmp_fname)

    def test_load_from_yaml(self):
        # Try to limit this to the only hard-coded dictionary. If this test passes, all other
        # dictionaries (reference or input) can be loaded from a file instead
        ref_data = {"elements": {"test_element": {"input_type": "parameter_set_1",
                                                  "link_type":"FREE_SPACE",
                                                  "idx": 1,
                                                  "parameters":{"distance": 3000.0,
                                                                "frequency": 5.0},
                                                  "gain_loss": None}},
                    "general_values": {"input_power": 30.0,
                                      "rx_sys_threshold": 6.021,
                                      "total_gain": None,
                                      "total_margin": None},
                    "settings": {"case_type": "nominal"}
                    }
        self.assertDictEqual(self.data_bare_minimum, ref_data)


    def test_save_to_yaml(self):
        ref_data = {"elements": {"test_element": {"input_type": "parameter_set_1",
                                                  "link_type": "FREE_SPACE",
                                                  "idx": 1,
                                                  "parameters": {"distance": 3000.0,
                                                                 "frequency": 5.0},
                                                  "gain_loss": None}},
                    "general_values": {"input_power": 30.0,
                                       "rx_sys_threshold": 6.021,
                                       "total_gain": None,
                                       "total_margin": None},
                    "settings": {"case_type": "nominal"}
                    }
        save_to_yaml(ref_data, self.tmp_fname)

        self.assertTrue(filecmp.cmp('ref_data/bare_minimum.yaml', self.tmp_fname))

        # tearDown automatically removes this file after running


    def test_read_user_data(self):

        self.assertEqual(read_user_data(self.data_test_user_data).to_dict(), self.ref_user_data)

    @unittest.expectedFailure # TODO: Remove this once it works
    def test_fill_results_data(self):

        test_df_user_data = read_user_data(self.unit_converted_user_data)
        out = fill_results_data(test_df_user_data, self.unit_converted_user_data)

        self.assertEqual(out, self.ref_fill_results_data)


    def test_sum_results(self):
        pass

    def test_main_process_basic(self):
        result = main_process(self.data_generic_only)

        self.data_generic_only['general_values']['total_gain'] = -53.0
        self.data_generic_only['general_values']['total_margin'] = -7

        # Check that all units are converted back properly and the inputs have not been changed
        self.assertDictEqual(result, self.data_generic_only)

    def test_main_process_complex(self):
        pass



if __name__ == '__main__':
    unittest.main()
