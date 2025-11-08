from symbol_table.Functions.function import Function
from symbol_table.Variables.variable_table import VariableTable


class FunctionDirectory:
    def __init__(self):
        self.functions = {}  # {nombre: Function}
        self.current_function = None  # Funcion actual durante el análisis
        self.global_table = VariableTable('global')
    
    def add_function(self, name, return_type='void'):
        # Agregamos una funcion al directorio
        if name in self.functions:
            return False  # La funcion ya existe 
        
        self.functions[name] = Function(name, return_type)
        return True
    
    def get_function(self, name):
        # Buscamos a una funcion por nombre
        return self.functions.get(name)
    
    def function_exists(self, name):
        # Verificamos si una funcion existe
        return name in self.functions
    
    def set_current_function(self, name):
        # Establecemos a la funcion actual durante el analisis
        self.current_function = name
    
    def get_current_function(self):
        # Obtenemos a la funcion actual
        if self.current_function:
            return self.functions.get(self.current_function)
        return None
    
    def add_global_variable(self, var_name, var_type):
        # Agregamos una variable global
        return self.global_table.add_variable(var_name, var_type)
    
    def add_local_variable(self, var_name, var_type):
        # Agregamos una variable local a la funcion actial
        current_func = self.get_current_function()
        if current_func:
            return current_func.add_local_variable(var_name, var_type)
        return False
    
    def lookup_variable(self, var_name):
        # Primero buscamos localmente si hay funcion actual
        current_func = self.get_current_function()
        if current_func:
            var = current_func.get_variable(var_name)
            if var:
                return var
        
        # Si no se encuentra una variable local, buscar entre la variables globales
        return self.global_table.get_variable(var_name)
    
    def print_directory(self):
        print("Directorio de fucnciones")
    
        print("\nVariables globales:")
        self.global_table.print_table()
        
        print("\nFunciones:")
        if not self.functions:
            print("(nil)")
        else:
            for func in self.functions.values():
                func.print_function()