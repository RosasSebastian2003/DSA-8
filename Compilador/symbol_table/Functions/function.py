from symbol_table.Variables.variable_table import VariableTable

class Function:
    def __init__(self, name, return_type='void'):
        self.name = name
        self.return_type = return_type
        self.parameters = []  # [(nombre, tipo, ...]
        self.variable_table = VariableTable(name)
    
    def add_parameter(self, param_name, param_type):
        # Los parametros son variables locales
        if self.variable_table.add_variable(param_name, param_type):
            self.parameters.append((param_name, param_type))
            return True
        return False
    
    def add_local_variable(self, var_name, var_type):
        # Agrefar una variable local a la funcion
        return self.variable_table.add_variable(var_name, var_type)
    
    def get_variable(self, var_name):
        # Buscar una variable local en la funcion
        return self.variable_table.get_variable(var_name)
    
    def get_parameter_types(self):
        # Obtenemos los tipos de parametros en orden
        return [param_type for _, param_type in self.parameters]
    
    def __repr__(self):
        params = ', '.join([f"{name}:{type_}" for name, type_ in self.parameters])
        return f"Function({self.name}, [{params}])"
    
    def print_function(self):
        # Help
        params = ', '.join([f"{name}:{type_}" for name, type_ in self.parameters])
        print(f"\nFuncion: {self.name}")
        print(f"Tipo: {self.return_type}")
        print(f"Parametros: [{params}]")
        self.variable_table.print_table()
