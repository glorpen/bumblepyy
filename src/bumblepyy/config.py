'''
Created on 22-08-2011

@author: arkus
'''

from configobj import ConfigObj, Section

class Config():
    def __init__(self, path_or_dict):
        if type(path_or_dict) == dict:
            self._config = dict
        else:
            self._config = ConfigObj(path_or_dict)
    
    def __getattr__(self, key):
        if key == "system":
            sys_dict=self._config["config"][self._config["system"]]
            if sys_dict.has_key("x_args"):
                sys_dict["x_args"] += self.x_args
            else:
                sys_dict["x_args"] = self.x_args
            return Config(sys_dict)
        
        if type(self._config[key]) == Section:
            return Config(self._config[key])
        
        return self._config[key]
        
