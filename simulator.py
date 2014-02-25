class AngelSimulator:
    def __init__(self, data, name, update_rate):
        self.rate = update_rate
        self.sim_name = name
        self.sim_data = data
        
    def get_name(self):
        return self.sim_name
    
    def update_rate(self):
        return self.rate
    
    def get_data_types(self):
        return self.sim_data.get_data_types()
    
    def get_data(self, data_type_list):
        ret = {}
        next_data = self.sim_data.get_measures()
        for data_type in data_type_list:
            if data_type in next_data:
                ret[data_type] = next_data[data_type]
            else:
                ret[data_type] = None
                
        return ret
        
        