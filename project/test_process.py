import process
import pandas as pd

def test_load_from_yaml():
    pass

def test_save_to_yaml():
    pass

def test_read_user_data():
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

    assert process.read_user_data(test_user_data).to_dict() == test_dict_user_data

def test_fill_results_data():
    pass

def test_sum_results():
    pass

def test_main_process():
    pass

test_read_user_data()
print('ok')