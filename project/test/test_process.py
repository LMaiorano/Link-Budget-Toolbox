import unittest
from project.process import read_user_data, fill_results_data

class MyTestCase(unittest.TestCase):
    # TODO: Use dics/df from txt/csv/??? file instead of hardcoding in this script
    # TODO: find setup / teardown? to limit crosscontamination test variables between unit tests
    # TODO: Check for tests to fail, skip next tests, as it is chronological.
    def test_load_from_yaml(self):
        pass

    def test_save_to_yaml(self):
        pass

    def test_read_user_data(self):
        test_user_data = {'elements': {'Free Space': {'gain_loss': None,
                                                 'idx': 3,
                                                 'input_type': 'parameter_set_2',
                                                 'link_type': 'FREE_SPACE',
                                                 'parameters': {'angle': 10.0,
                                                                'distance': 1500.0,
                                                                'gs_altitude': 0.0,
                                                                'sc_altitude': 300.0,
                                                                'wavelength': 10.0}},
                                  'GS RX Ant': {'gain_loss': None, 'idx': 1,
                                                'input_type': 'parameter_set_1',
                                                'link_type': 'RX',
                                                'parameters': {'antenna_diameter': 1.0,
                                                               'antenna_efficiency': 0.8,
                                                               'wavelength': 100.0}},
                                  'SC TX Ant': {'gain_loss': 10.0,
                                                'idx': 2,
                                                'input_type': 'gain_loss',
                                                'link_type': 'GENERIC',
                                                'parameters': None}},
                     'general_values': {'input_power': 65,
                                        'rx_sys_threshold': 6,
                                        'total_gain': None,
                                        'total_margin': None},
                     'settings': {'case_type': 'nominal'}}

        test_dict_user_data = {'name':
                                   {0: 'Free Space',
                                    1: 'GS RX Ant',
                                    2: 'SC TX Ant'},
                               'gain_loss': {0: None,
                                             1: None,
                                             2: 10.0},
                               'idx': {0: 3,
                                       1: 1,
                                       2: 2},
                               'input_type': {0: 'parameter_set_2',
                                              1: 'parameter_set_1',
                                              2: 'gain_loss'},
                               'link_type': {0: 'FREE_SPACE',
                                             1: 'RX',
                                             2: 'GENERIC'},
                               'parameters': {0: {'angle': 10.0,
                                                  'distance': 1500.0,
                                                  'gs_altitude': 0.0,
                                                  'sc_altitude': 300.0,
                                                  'wavelength': 10.0},
                                              1: {'antenna_diameter': 1.0,
                                                  'antenna_efficiency': 0.8,
                                                  'wavelength': 100.0},
                                              2: None}}

        self.assertEqual(read_user_data(test_user_data).to_dict(), test_dict_user_data)

    def test_fill_results_data(self):
        test_user_data = {'elements': {'Free Space': {'gain_loss': None,
                                                      'idx': 3,
                                                      'input_type': 'parameter_set_2',
                                                      'link_type': 'FREE_SPACE',
                                                      'parameters': {'angle': 10.0,
                                                                     'distance': 1500.0,
                                                                     'gs_altitude': 0.0,
                                                                     'sc_altitude': 300.0,
                                                                     'wavelength': 10.0}},
                                       'GS RX Ant': {'gain_loss': None, 'idx': 1,
                                                     'input_type': 'parameter_set_1',
                                                     'link_type': 'RX',
                                                     'parameters': {'antenna_diameter': 1.0,
                                                                    'antenna_efficiency': 0.8,
                                                                    'wavelength': 100.0}},
                                       'SC TX Ant': {'gain_loss': 10.0,
                                                     'idx': 2,
                                                     'input_type': 'gain_loss',
                                                     'link_type': 'GENERIC',
                                                     'parameters': None}},
                          'general_values': {'input_power': 65,
                                             'rx_sys_threshold': 6,
                                             'total_gain': None,
                                             'total_margin': None},
                          'settings': {'case_type': 'nominal'}}

        test_df_user_data = read_user_data(test_user_data)

        test_result_data = {'elements': {'Free Space': {'gain_loss': -66.72664804890425,
                                                        'idx': 3,
                                                        'input_type': 'parameter_set_2',
                                                        'link_type': 'FREE_SPACE',
                                                        'parameters': {'angle': 10.0,
                                                                       'distance': 1500.0,
                                                                       'gs_altitude': 0.0,
                                                                       'sc_altitude': 300.0,
                                                                       'wavelength': 10.0}},
                                         'GS RX Ant': {'gain_loss': -31.026102676197887,
                                                       'idx': 1,
                                                       'input_type': 'parameter_set_1',
                                                       'link_type': 'RX',
                                                       'parameters': {'antenna_diameter': 1.0,
                                                                      'antenna_efficiency': 0.8,
                                                                      'wavelength': 100.0}},
                                         'SC TX Ant': {'gain_loss': 10.0,
                                                       'idx': 2,
                                                       'input_type': 'gain_loss',
                                                       'link_type': 'GENERIC',
                                                       'parameters': None}},
                            'general_values': {'input_power': 65,
                                               'rx_sys_threshold': 6,
                                               'total_gain': None, 'total_margin': None},
                            'settings': {'case_type': 'nominal'}}

        self.assertEqual(fill_results_data(test_df_user_data, test_user_data), test_result_data)


    def test_sum_results(self):
        pass

    def test_main_process(self):
        pass

if __name__ == '__main__':
    unittest.main()
