# holds simulator data to
class SimulatorData:
    types = set()
    data = []
    # measures are streamed from the data buffer in rotating order, the index signifies the current data to send
    curr_idx = 0
    
    # the data types must be added before actual data
    # since for each data row, the code will validate each measure as of a valid type
    def add_data_type(self, data_type):
        if not data_type in self.types:
            self.types.add(data_type)
            
    def get_data_types(self):
        return self.types
            
    def add_data_measures(self, measures):
        if not set(measures.keys()).issubset(self.types):
            raise Exception('unexpected data types passed:', set(measures.keys()) - self.types)
        else:
            self.data.append(measures)
            
    def get_measures(self):
        ret = self.data[self.curr_idx]
        self.curr_idx = (self.curr_idx + 1) % len(self.data)
        return ret