from symbol_table.Variables.variable import Variable

class VariableTable:
    def __init__(self, scope_name):
        self.scope_name = scope_name
        self.variables = {}  # {nombre: Variable}

    # Agregamos una variable a la tabla
    def add_variable(self, name, var_type):
        if name in self.variables:
            return False  # La variable ya existe
        
        self.variables[name] = Variable(name, var_type, self.scope_name)
        return True
    
    def get_variable(self, name):
        # Buscamos a una variable por su nombre
        return self.variables.get(name)
    
    def variable_exists(self, name):
        # Verificamos si una variable existe en la tabla
        return name in self.variables
    
    def get_all_variables(self):
        # Retornamos una lista con todas las variables en la tabla
        return list(self.variables.values())
    
    # Defue como se representa un objeto en la consola
    def __repr__(self):
        return f"VariableTable({self.scope_name}, {len(self.variables)} vars)"
    
    def print_table(self):
        print(f"\n  Tabla de Variables en el scope {self.scope_name}")

        if not self.variables:
            print("(nil)")
        else:
            for var in self.variables.values():
                print(f"{var.name:15} | {var.var_type:10}")
