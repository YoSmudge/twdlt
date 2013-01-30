import json

class ConfigException(Exception):
    None

class Config(dict):
    """
    Load the configuration file
    
    @cvar   config:     Configuration options
    @type   config:     dict
    """
    
    def __init__(self,configFile):
        """
        Load the configuration
        
        @arg    configFile:     Path to config file
        @type   configFile:     str
        """
        
        #Exceptions should be caught further up the stack
        f = open(configFile, 'r')
        raw = f.read()
        f.close()
        
        self.config = {
            'age':24,
            'atAge':None,
            'consumerKey':None,
            'consumerSecret':None,
            'accessToken':None,
            'accessSecret':None,
            'perPage':150,
            'maxPage':5,
            'useLimit':0.25,
            'every':60
        }
        
        self.config.update(json.loads(raw))
        
        for k in self.config.keys():
            if not self.config[k]:
                raise ConfigException("Config argument {0} is required".format(k))
    
    def __getitem__(self,key):
        return self.config[key]