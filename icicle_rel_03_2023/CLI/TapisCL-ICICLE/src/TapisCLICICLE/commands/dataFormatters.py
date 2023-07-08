import pprint


class BaseDataFormatter:
    def __init__(self, non_verbose_fields: list[list | str] = []):
        self.non_verbose_fields = non_verbose_fields

    def obj_to_dict(self, obj):
        if isinstance(obj, (int, float, str, bool)):
            return obj 
        elif isinstance(obj, dict):
            return {k: self.obj_to_dict(v) for k, v in obj.items()} 
        elif isinstance(obj, (list, tuple, set)):
            return type(obj)(self.obj_to_dict(item) for item in obj) 
        elif obj == None:
            return None
        elif isinstance(obj, object):
            return self.obj_to_dict(obj.__dict__) 
        return None 
    
    def non_verbose_formatter(self, serialized_data):
        formatted = dict()
        if self.non_verbose_fields:
            for field in self.non_verbose_fields:
                if isinstance(field, str):
                    formatted[field] = serialized_data[field]
                    print(serialized_data[field])
                elif isinstance(field, list):
                    formatted[field] = self.non_verbose_formatter(serialized_data[field])
            return formatted
        else:
            return serialized_data
    
    def __call__(self, data, verbose):
        serialized = self.obj_to_dict(data)
        if verbose:
            return serialized
        if isinstance(serialized, list) and self.non_verbose_fields:
            return_data = list()
            for fragment in serialized:
                non_verbose_fragment = self.non_verbose_formatter(fragment)
                return_data.append(non_verbose_fragment)
            return return_data
        return self.non_verbose_formatter(serialized)
        

    
