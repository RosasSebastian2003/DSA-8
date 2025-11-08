class Variable:
    def __init__(self, name, var_type, scope):
        self.name = name
        self.var_type = var_type
        self.scope = scope
    
    def __repr__(self):
        return f"Variable({self.name}, {self.var_type}, {self.scope})"
    
    def __str__(self):
        return f"{self.name}: {self.var_type} (scope: {self.scope})"
