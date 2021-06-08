# Satellite Link Budget Toolbox


[![Toolbox Verification Tests](https://github.com/LMaiorano/Link-Budget-Toolbox/actions/workflows/python-app.yml/badge.svg)](https://github.com/LMaiorano/Link-Budget-Toolbox/actions/workflows/python-app.yml)
[![GitHub license](https://img.shields.io/github/license/LMaiorano/Link-Budget-Toolbox)](https://github.com/LMaiorano/Link-Budget-Toolbox/blob/master/LICENSE)

A modular Python alternative to STK to easily calculate satellite link budgets


## TODO Checklist:
- [ ] Review all entries in element_reference.yaml
- [ ] Proofread ReadMe
- [ ] Create relevant example config 
- [ ] Settings.py description



More documentation to follow...


## Usage
Install venv

To use the Link Budget Toolbox, `main.py` can be run from the terminal. By default (no additional arguments) it will run in application-mode, which opens a 
user-friendly GUI. This allows the user to create a valid link budget and calculate
the margins.

`
$ python main.py
`

Alternatively, if a configuration file is already present, the link budget calculation
can be run as a CLI script using the `-s` flag. The path to the YAML config can be specified with the `-f <filepath>` argument. 

`
$ python main.py -s -f "project/configs/demo.yaml"
`


By default, an example configuration file will be used, which is defined in `settings.py` by variable `DEFAULT_LINK_CONFIG`.

```
usage: Link Budget Toolbox [-h] [-d | -s] [-f FILE]

Runs by default as application with GUI

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           GUI app only: Print debug statements to terminal
  -s, --script          Run as CLI script. Does not open GUI
  -f FILE, --file FILE  Link Budget configuration file (YAML)

```

Settings.py stuff


## Link Budget Configuration Files

Example configuration:
```yaml
elements:
  Free Space:
    gain_loss: null
    idx: 3
    input_type: parameter_set_2
    link_type: FREE_SPACE
    parameters:
      angle: 10.0
      distance: 1500.0
      gs_altitude: 0.0
      sc_altitude: 300.0
      frequency: 10.0
  GS RX Ant:
    gain_loss: null
    idx: 1
    input_type: parameter_set_1
    link_type: RX
    parameters:
      antenna_diameter: 1.0
      antenna_efficiency: 0.8
      frequency: 100.0
  SC TX Ant:
    gain_loss: 10.0
    idx: 2
    input_type: gain_loss
    link_type: GENERIC
    parameters: null
general_values:
  input_power: 65
  rx_sys_threshold: 6
  total_gain: null
  total_margin: null
settings:
  case_type: nominal

```
Explanation of each field here...

# Development

## Project Structure

stuff about folders and standard locations

## How-To: Creating a New Element:
New element types can be added using the steps below. The GUI dynamically loads these elements, and therefore does not need modification.

1. Create a new LINKTYPE_link_element.py file
2. Import the LinkElement parent class
3. Create the LINKTYPE_LinkElement(LinkElement) childclass
4. Initialize the class, requiring a name, input_type, gain and a parameters dictionary
5. The name, linktype = LINKTYPE, and gain are initialized from the parent class
6. All attributes that are unique to the class, such as the input_type and any parameters, are assigned after this. The parameters are obtained from the parameters dictionary
7. Finally in the intialization, check if the gain is directly given. If not, call the process method to calculate it
8. In the process method, check which parameter_set_# is to be used and call the specific required class methods to calculate the gain per parameter_set_#
9. For any parameter_set_#, define the required methods to calculate the gain with
10. Finally convert per calculation the gain to decibels using the LinkElement.dB(value) method and then update the new LINKTYPE_LinkElement.gain

### Example Link Element
```python
from project.link_element import LinkElement
# import other packages here

class RX_LinkElement(LinkElement):
    def __init__(self, name, input_type, gain, parameters):
        # Run the initialization of parent LinkElement
        super().__init__(name, linktype='RX', gain = gain)

        # Add attributes that are unique to Rx_LinkElement
        self.input_type = input_type

        # Add attributes that are unique parameters to RxElement
        self.param_a = parameters.get('param_a', None)
        self.param_b = parameters.get('param_b', None)
        self.param_c = parameters.get('param_c', None)
        # check if gain/loss is given directly or calculations are required
        if self.input_type != 'gain_loss':
            self.process()
        
    def process(self):
        if self.input_type == "parameter_set_1":
            G = self.calc_1()
            self.gain = self.dB(G)
        elif self.input_type == "parameter_set_2":
            G = self.calc_2()
            self.gain = self.dB(G)

    def calc_1(self):
        G = self.param_a + self.param_b
        return G

    def calc_2(self):
        G = self.param_a*self.param_c + self.param_b
        return G
    
if __name__ == '__main__':
    elem_name = 'Test Element'
    testparameters = {'antenna_efficiency':0.7,
                      'antenna_diameter':10,
                      'wavelength':1550e-9,
                      'waist_radius': 24.7e-3}

    rx_le = RX_LinkElement(elem_name, 'parameter_set_2', None, testparameters)
```
### Definitions:
|            	|                                                        Description                                                         	|   Naming Convention  	|
|------------	|:--------------------------------------------------------------------------------------------------------------------------:	|:--------------------:	|
| link_type  	|                                                                                                                            	| All Caps (required)  	|
| input_type 	| Which parameter set is to be used. This depends on the Link Type, and is defined for reference in `element_reference.yaml` 	| lower_case no spaces 	|


### Element Reference File:
Found at `project/element_reference.yaml`
This is used for the backend, to define for each `link_type`, per parameter set:
 - Which attributes are required
 - The units of each attribute
 - A description for each attribute
 - The acceptable domain of the attribute (using mathematical "[ ]" and "()" interval notation)
 

An example is shown below. Note: this is incomplete and not up-to-date.
```yaml
FREE_SPACE:
    overall_description:    Summary of FREE_SPACE element
    parameter_set_1:
        distance:
            description:    Distance between spacecraft and ground station
            units:          m
            range:          "(0, inf)"
        frequency:
            description:    Radio frequency
            units:          "MHz"
            range:          "(0, inf)"
    parameter_set_2:
        angle:
            description:    "Elevation angle"
            units:          "deg"
        distance:
            description:    "Slant range between spacecraft and ground station"
            units:          "km"
            range:          "(0, inf)"
        gs_altitude:
            description:    Ground station altitude
            units:          m
            range:          "[0, inf)"
        sc_altitude:
            description:    Spacecraft altitude
            units:          km
            range:          "[0, inf)"
        frequency:
            description:    Radio frequency
            units:          MHz
            range:          "(0, inf)"
```
