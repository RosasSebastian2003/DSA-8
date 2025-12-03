class SemanticCube:
    def __init__(self):
        self.cube = {}
        
        # Definicion del cubo
        self.cube['+'] = {
            'int': {
                'int': 'int',     
                'float': 'float' 
            },
            'float': {
                'int': 'float',  
                'float': 'float' 
            }
        }
        
        self.cube['-'] = {
            'int': {
                'int': 'int',     
                'float': 'float'  
            },
            'float': {
                'int': 'float',   
                'float': 'float' 
            }
        }
        
        self.cube['*'] = {
            'int': {
                'int': 'int',    
                'float': 'float' 
            },
            'float': {
                'int': 'float',   
                'float': 'float'  
            }
        }
        
        self.cube['/'] = {
            'int': {
                'int': 'float',    
                'float': 'float'   
            },
            'float': {
                'int': 'float',    
                'float': 'float'  
            }
        }
        
        self.cube['>'] = {
            'int': {
                'int': 'int',    
                'float': 'int'   
            },
            'float': {
                'int': 'int',      
                'float': 'int'    
            }
        }
        
        self.cube['<'] = {
            'int': {
                'int': 'int',     
                'float': 'int'    
            },
            'float': {
                'int': 'int',  
                'float': 'int'    
            }
        }
        
        self.cube['!='] = {
            'int': {
                'int': 'int',      
                'float': 'int'    
            },
            'float': {
                'int': 'int',     
                'float': 'int'  
            }
        }

        self.cube['='] = {
            'int': {
                'int': 'int',
                'float':'int'      
            },
            'float': {
                'int': 'float',    
                'float': 'float'   
            }
        }
    
    def get_result_type(self, operator, left_type, right_type):
        try:
            return self.cube[operator][left_type][right_type]
        except KeyError:
            return None
    
    def is_valid_operation(self, operator, left_type, right_type):
        return self.get_result_type(operator, left_type, right_type) is not None
    

semantic_cube = SemanticCube()