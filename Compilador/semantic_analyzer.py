from semantic_cube import semantic_cube
from symbol_table.Functions.function_directory import FunctionDirectory
from symbol_table.Variables.variable import Variable


class SemanticError(Exception):
    # Excepcion para errores semanticos
    pass

class SemanticAnalyzer:
    def __init__(self):
        # Inicializamos al analizador semantico
        self.function_directory = FunctionDirectory()
        self.current_function = None
        self.errors = []
        self.program_name = None
        self.debug = False
    
    def add_error(self, message, line=None):
        # Agregamos un error semantico a la lista
        if line:
            error_msg = f"Error en la linea {line}: {message}"
        else:
            error_msg = f"Error: {message}"
        
        self.errors.append(error_msg)
        print(error_msg)
    
    def has_errors(self):
        # Verificamos si hubieron errores semanticos
        return len(self.errors) > 0
    
    def print_errors(self):
        # Helper para imprimir a todos los errores encontrados
        if self.has_errors():
            for error in self.errors:
                print(f"{error}")
    
    # Punto neuralgico para empezar el programa
    def np_start_program(self, program_name):
        self.program_name = program_name
        if self.debug:
            print(f"Iniciando programa: {program_name}")
        
     # Iniciar con la declaracion de la funcion   
    def np_start_function(self, func_name, return_type='void'):
        if self.debug:
            print(f"Declarando funcion: {func_name}")
        
        # Verificar que la funcion no este declarada
        if self.function_directory.function_exists(func_name):
            self.add_error(f"La funcion '{func_name}' ya fue declarada")
            return False
        
        # Agregamos a la funcion al directorio
        self.function_directory.add_function(func_name, return_type)
        self.function_directory.set_current_function(func_name)
        self.current_function = func_name
        return True
    
    # Fin de la declaracion de la funcion
    def np_end_function(self, func_name):
        if self.debug:
            print(f"Fin de la funcion: {func_name}")
        self.current_function = None
        self.function_directory.set_current_function(None)
    
    def np_add_parameter(self, param_name, param_type):
        if self.debug:
            print(f"Agregando parametro: {param_name}:{param_type}")
        
        if self.current_function:
            func = self.function_directory.get_function(self.current_function)
            if func:
                if not func.add_parameter(param_name, param_type):
                    self.add_error(
                        f"Parametro '{param_name}' doblemente declarado en función '{self.current_function}'"
                    )
    
    # Puntos neuralgicos para variables
    # declaracion de una variable
    def np_declare_variable(self, var_name, var_type, is_global=False):
        # Definimos el scope
        scope = "global" if is_global else self.current_function
        if self.debug:
            print(f"Declarando variable: {var_name}:{var_type}, scope: {scope}")
        
        success = False
        if is_global:
            success = self.function_directory.add_global_variable(var_name, var_type)
        else:
            success = self.function_directory.add_local_variable(var_name, var_type)
        
        if not success:
            self.add_error(
                f"La varuble '{var_name}' ya fue declarada, scope: {scope}"
            )
    
    # Uso de una variable
    def np_check_variable(self, var_name):
        var = self.function_directory.lookup_variable(var_name)

        if var is None:
            self.add_error(f"La variable '{var_name}' no existe")
            return None

        return var.var_type
    
    #Expresiones y operaciones
    # Verificacion de una operacion
    def np_check_operation(self, operator, left_operand, right_operand, left_type, right_type):

        if left_type is None or right_type is None:
            return None

        result_type = semantic_cube.get_result_type(operator, left_type, right_type)

        if result_type is None:
            self.add_error(
                f"Operacion invalida: {left_operand}({left_type}) {operator} {right_operand}({right_type})"
            )
            return None
        if self.debug:
            print(f"Resultado: {result_type}")
        return result_type
    
    # Verificacion de asignacion
    def np_check_assignment(self, var_name, expr_type):
        if self.debug:
            print(f"Verificando asignacion: {var_name} = <expr:{expr_type}>")
        
        # Checamos si la variable existe
        var = self.function_directory.lookup_variable(var_name)
        if var is None:
            self.add_error(f"La variable '{var_name}' no existe ")
            return False
        
        var_type = var.var_type
        
        # Verificar que los tipos sean compatibles mediante el cubo semantico
        result_type = semantic_cube.get_result_type('=', var_type, expr_type)
        
        if result_type is None:
            self.add_error(
                f"Tipo incompatible: no se puede asignar {expr_type} a {var_type}"
            )
            
            return False
        
        return True
    
    # Llamadas de funcion 
    # Inicio de una llamada de funcion
    def np_start_function_call(self, func_name):
        if self.debug:
            print(f"Llamando a la funcion: {func_name}")
        
        func = self.function_directory.get_function(func_name)
        if func is None:
            self.add_error(f"La funcion '{func_name}' no existe")
            return None
        
        return func
    
    # Verificacion de la llamada a una funcion
    def np_check_function_call(self, func_name, argument_types):
        if self.debug:
            print(f"Verificando llamada: {func_name}({', '.join(argument_types)})")
        
        func = self.function_directory.get_function(func_name)
        if func is None:
            # Ya el error fue registrado en np_fucntion_call
            return False
        
        expected_types = func.get_parameter_types()
        
        # Verificar número de argumentos
        if len(argument_types) != len(expected_types):
            self.add_error(
                f"Numero incorrecto de argumentos en la funcion '{func_name}': "
                f"se esperan {len(expected_types)} pero se recibieron {len(argument_types)}"
            )
            return False
        
        # Verificar los tipos de los argumentos
        for i, (arg_type, expected_type) in enumerate(zip(argument_types, expected_types)):
            if arg_type != expected_type:
                # Verificar si hay conversiones validas
                if not (expected_type == 'float' and arg_type == 'int'):
                    self.add_error(
                        f"Tipo incorrecto para el argumento {i+1} para la funcion '{func_name}': "
                        f"se espera {expected_type}, se recibio {arg_type}"
                    )
                    return False
        
        return True
    
    # Helpers
    # Determinar el tipo de literal
    def get_literal_type(self, value):
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        return None
    
    def print_symbol_tables(self):
        # Imprimir todas las tablas de simbolos
        self.function_directory.print_directory()
    
    def reset(self):
        # Reiniciar al analizador
        self.__init__()

