import xml.etree.ElementTree as ET
from data.data import SimulatorData

# constructs SimulatorData from xml
def read_simulator_data(xml):
	ret = SimulatorData()
	
	root = ET.fromstring(xml)
	
	types = root.iter('data_type')
	for data_type in types:
		ret.add_data_type(data_type.attrib['name'])
	
	measures = root.iter('Measures')
	for measure in measures:
		measure_data = {}
		data_entries = measure.iter('Measure')
		for data_entry in data_entries:
			measure_data[data_entry.attrib['type']] = int(data_entry.text.strip())
		ret.add_data_measures(measure_data)

	return ret
		