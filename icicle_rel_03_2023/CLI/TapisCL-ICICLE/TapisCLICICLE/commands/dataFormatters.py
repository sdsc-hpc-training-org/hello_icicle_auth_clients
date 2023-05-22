from tapipy.tapis import TapisResult


HANDLED_TYPES = (TapisResult)
JSON_SERIALIZABLE = (str, int, dict, list, set, tuple)
    

class DataFormatters:
    pod_data = ('pod_id', 'pod_template', 'status')
    system_data = ('id', 'owner', 'systemType', 'canExec')
    app_data = ('id', 'owner', 'version', 'runtime')
    server_data = ('username',)

    @staticmethod
    def json_serializer(return_data):
        if isinstance(return_data, list):
            processed_data = []
            for data in return_data:
                processed_data.append(DataFormatters.json_serializer(data))
            return processed_data
        
        elif isinstance(return_data, dict):
            processed_data = dict()
            for name, data in return_data.items():
                processed_data[name] = DataFormatters.json_serializer(data)
            return processed_data

        elif isinstance(return_data, TapisResult):
            return DataFormatters.json_serializer(return_data.__dict__)
        
        return return_data

    @staticmethod
    def base_formatter(self, return_data, desired_data=None):
        filled_data = None
        if isinstance(return_data, list):
            filled_data = []
            for data in return_data:
                filled_data.append(DataFormatters.base_formatter(self, data, desired_data=desired_data))
            return filled_data
        elif isinstance(return_data, dict):
            filled_data = dict()
            for name, data in return_data.items():
                if name in desired_data:
                    filled_data[name] = data
            return filled_data
        return return_data
    
    @staticmethod
    def pod_formatter(self, return_data, verbose):
        if not verbose:
            return_data = DataFormatters.json_serializer(return_data)
            return DataFormatters.base_formatter(self, return_data, desired_data=DataFormatters.pod_data)
        return str(return_data)
    
    @staticmethod
    def system_formatter(self, return_data, verbose):
        if not verbose:
            return_data = DataFormatters.json_serializer(return_data)
            return DataFormatters.base_formatter(self, return_data, desired_data=DataFormatters.system_data)
        return str(return_data)
    
    @staticmethod
    def app_formatter(self, return_data, verbose):
        if not verbose:
            return_data = DataFormatters.json_serializer(return_data)
            return DataFormatters.base_formatter(self, return_data, desired_data=DataFormatters.app_data)
        return str(return_data)
    
    @staticmethod
    def server_formatter(self, return_data, verbose):
        if not verbose:
            return_data = DataFormatters.json_serializer(return_data)
            return DataFormatters.base_formatter(self, return_data, desired_data=DataFormatters.server_data)
        return str(return_data)
    
