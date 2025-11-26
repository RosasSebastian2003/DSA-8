class Variable:
    def __init__(self, name, var_type, scope, virtual_address):
        self.name = name
        self.var_type = var_type
        self.scope = scope
        self.virtual_address = virtual_address
    
    def __repr__(self):
        return f"Variable({self.name}, {self.var_type}, {self.scope}, {self.virtual_address})"
    
    def __str__(self):
        return f"{self.name}: {self.var_type} (scope: {self.scope}, address {self.virtual_address})"
