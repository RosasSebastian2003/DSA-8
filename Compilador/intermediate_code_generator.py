from semantic_cube import SemanticCube
from excecution_memory import excecution_memory

class IntermediateCodeGenerator:
    def __init__(self):
        self.quads = []
        
        # Pilas
        self.operator_stack = []
        self.operand_stack = []
        
        self.type_stack = []
        
        # Aqui guardamos el salto pendiente previo a evaluar una condicion (if, while)
        self.jump_stack = [] 
        
        self.temp_var_counter = 0 # Contador de variables temporales
        
        self.function_table = {}  # Tabla de funciones {nombre_funcion: Function}
        self.argument_stack = []  # Pila para manejar argumentos en llamadas a funciones
        self.param_counter = 0  # Contador de argumentos en llamadas a funciones
        self.call_stack = []      # Pila para manejar llamadas a funciones
        self.current_function = None  # Nombre de la funcion actual siendo procesada
        
    # Agregar un operador a la pila
    def push_operator(self, operator):
        self.operator_stack.append(operator)
    
    # Eliminamos uno de los operadores de la fila de operadores, primero revizamos si existe
    # si existe, eliminamos el elemento de la pila y lo arrojamos
    # si no existe, arrojamos un nulo
    def pop_operator(self):
        if self.operator_stack:
            return self.operator_stack.pop()

        return None

    # Retornamos el elemento mas nuevo de la pila, usamos el indice -1 ya que corresponde al ultimo elemento agregado
    def peak_operator(self):
        if self.operator_stack:
            return self.operator_stack[-1]
        return None
    
    def push_operand(self, operand, operand_type):
        self.operand_stack.append(operand)
        self.type_stack.append(operand_type)
        
    def pop_operand(self):
        if self.operand_stack and self.type_stack:
            operand = self.operand_stack.pop()
            operand_type = self.type_stack.pop()
            
            return operand, operand_type

        return None, None
    
    def push_jump(self, position):
        self.jump_stack.append(position)
    
    def pop_jump(self):
        if self.jump_stack:
            return self.jump_stack.pop()

        return None
    
    def add_temp(self):
        self.temp_var_counter += 1
        return f"t{self.temp_var_counter}"
        
    def add_quad(self, operator, arg1, arg2, result):
        quad = (operator, arg1, arg2, result)
        self.quads.append(quad)
        
        # Indice en el cual se almaceno el cuadruplo agregado
        return len(self.quads) - 1
    
    # Lo utilizamos cuando tenemos que llenar un cuadruplo vacio, como al final de un if
    def fill_quad(self, position, value):
        if 0 <= position < len(self.quads):
            quad = self.quads[position]
            
            self.quads[position] = (quad[0], quad[1], quad[2], value)
    
    # La utilizamos cuando necesitamos la siguiente posicion o la posicion actual
    def get_current_position(self):
        return len(self.quads)
    
    # Cuadruplo para operaciones aritmeticas, se utiliza al cubo semantico para validar tipos
    def generate_arithmetic_operation(self, semantic_cube: SemanticCube):
        if not self.operator_stack:
            return None
        
        operator = self.pop_operator()
        
        # El procesamiento se lleva a cabo de izquierda a derecha, por lo que podemos asumir que el ultimo operador en evaluarse es el de la derecha 
        # Teniendo 'a + b', tenemos que el proceso seria:
        # operand_stack.append(a)
        # type_stack.append(int)
        
        # operator_stack.append(+)
        
        # operand_stack.append(b)
        # type_stack.append(int)
        
        # Por ende, podemos asumir que el operando de la derecha es el elemento mas reciente en la pila
        right, right_type = self.pop_operand()
        left, left_type = self.pop_operand()
        
        # Usamos al cubo semantico para validar el tipo del resulrado final
        result_type = semantic_cube.get_result_type(operator=operator, left_type=left_type, right_type=right_type)
        
        if result_type is None:
            print(f"Error: Operacion invalida {left_type} {operator} {right_type}")
            return None
        
        # Generamos una nueva variable temporal para almacenar el resultado de la operacion 
        temp = self.add_temp()
        temp_address = self.get_temp_address(name=temp, var_type=result_type)
        
        # Creamos un cuadruplo
        self.add_quad(operator=operator, arg1=left, arg2=right, result=temp_address)
        
        # Guardamos el resultado en la pila de operandos
        self.push_operand(operand= temp_address, operand_type=result_type)
        
        return temp_address
    
    # No todas las operaciones necesitan a los 4 argumentos ya que no necesariamente retornan algo
    # En ocaciones los resultados dentro de un cuadruplo pueden representar a un salto 
    def generate_assignation(self, var_name):
        exp_operand, exp_type = self.pop_operand()
        self.add_quad(operator="=", arg1=exp_operand, arg2=None, result=var_name) 
        #                  asignacion    valor a asignar              variable destino
        
    def generate_print(self, expression_array):
        expressions = []
        
        for i in range(expression_array):
            operand, operand_type = self.pop_operand()
            expressions.append(operand)
            
        expressions.reverse()
        
        for expression in expressions:
            self.add_quad(operator="PRINT", arg1=expression, arg2=None, result=None)
            #                  accion            expresion                   no hay retorno
    
    # Generamos un GOTOF (Go To False) al inicio del if y marcamos una posicion 
    # la cual sera llenada una vez que sepamos como se evalua la condicion
    def begin_if(self):
        condition, condition_type = self.pop_operand()
        
        # Evaluamos el cuadruplo con -1 para señalarlo como un salto, 
        # indicando asi que sera evaluado una vez que se evalue la condicion
        pending = self.add_quad("GOTOF", condition, None, -1)
        
        self.push_jump(pending)
    
    # Completamos el salto pendiente, para entonces ya sabemos a que evaluo la condicion
    def end_if(self):
        pending = self.pop_jump()
        current_position = self.get_current_position()
        
        # Llenamos el salto pendiente con el cuadruplo evaluado 
        self.fill_quad(position=pending, value=current_position)
        
    def begin_else(self):
        # Generamos un GOTO (Go To) para saltar al else
        # Aun no sabemos donde terminara el else
        goto_pos = self.add_quad("GOTO", None, None, -1)
        
        # Completamos el GOTOF del if de este else, para entonces sabemos que debemos de saltar a este else 
        # si la condicion del if evalua a falso
        gotof_pos = self.pop_jump()
        current_pos = self.get_current_position()
        self.fill_quad(position=gotof_pos, value=current_pos)
        
        # Guardamos el GOTO pendiente en la cola de saltos 
        self.push_jump(goto_pos)
        
    # Completamos el cuadruplo pendiente de else 
    def end_else(self):
        goto_pos = self.pop_jump()
        current_pos = self.get_current_position()
        self.fill_quad(position=goto_pos ,value=current_pos)
    
    # Generamos un marcador que nos lleve a un punto previo a la condicion
    def begin_while(self):
        current_pos = self.get_current_position()
        self.push_jump(position=current_pos)
        
    # Generamos un GOTOF para el while, esto representara la condicion bajo la cual ejecutara nuestro ciclo
    def generate_while_condition(self):
        condition, cond_type = self.pop_operand()
        
        gotof_pos = self.add_quad(operator="GOTOF", arg1=condition, arg2=None, result=-1)
        self.push_jump(position=gotof_pos)
    
    # Generamos un GOTO para marcar la salida del while
    def end_while(self):
        gotof_pos = self.pop_jump()
        return_pos = self.pop_jump()
        
        self.add_quad(operator="GOTO", arg1=None, arg2=None,result=return_pos) # Salto al inicio del ciclo 
        
        current_position = self.get_current_position()
        self.fill_quad(position=gotof_pos, value=current_position)
    
    # Agregamos el operador de parentesis a la pila de operadores, este servira como flag al momento en que encontremos al parentesis de cierre
    def open_parenthesis(self):
        self.operator_stack.append("(")
    
    
    def close_parenthesis(self, semantic_cube: SemanticCube):
        # Iteramos a travez de la pila de operadores utilizando a "(" como flag,
        # donde el punto neuralgico generate_arithmetic_operation toma y procesa a las operaciones dentro del parentesis 
        # y consume a los operadores hasta llegar a la apertura del parentesis, donde se detendra la ejecucion del while
        while self.operator_stack and self.peak_operator() != "(":
            self.generate_arithmetic_operation(semantic_cube=semantic_cube)
        
        # Eliminamos a la apertura del parentesis de la pila de operadores
        if self.operator_stack and self.peak_operator() == "(":
            self.pop_operator()
    
    # Declaracion de funciones - registrar en tabla
    def register_function(self, func_name):
        start_address = self.get_current_position()
        
        # Registramos a la funcion en la tabla de funciones junto con sus recursos
        # Almacenamos la cantidad de variables locales y temporales que utiliza la funcion 
        # y la informacion de sus parametros
        self.function_table[func_name] = {
            "start_address": start_address,
            "param_addresses": [],
            "param_types": [],
            "local_vars": 0,
            "temp_vars": 0
        }
        
        print(f"Funcion {func_name} registrada en direccion {start_address}")
    
    # Agregar un parametro a la funcion en la tabla de funciones
    def add_function_param(self, func_name, param_address, param_type):
        if func_name in self.function_table:
            self.function_table[func_name]["param_addresses"].append(param_address)
            self.function_table[func_name]["param_types"].append(param_type)
            print(f"Parametro agregado a {func_name}: {param_address} ({param_type})")
            
    def end_function(self, func_name):
        # Generamos un cuadruplo ENDFUNC 
        self.add_quad(operator="ENDFUNC", arg1=None, arg2=None, result=None)
        print(f"Funcion {func_name} finalizada")
        
    # Iniciamos una llamada de funcion
    # Generamos un cuadruplo ERA para reservar espacio de la memoria para llamar a la funcion
    def begin_function_call(self, func_name):
        if self.current_function is not None:
            self.call_stack.append({
                "function_name": self.current_function,
                "param_counter": self.param_counter,
                "arguments": self.argument_stack.copy()
            })
            self.argument_stack = []
            
        self.current_function = func_name
        self.param_counter = 0
        
        # Generamos un cuadruplo ERA 
        self.add_quad(operator="ERA", arg1=func_name, arg2=None, result=None)
        
        print(f"Llamando a la funcion: {func_name}")
    
    # Procesamos un argumento para la llamada de la funcion
    # una vez procesado, enviamos el parametro mediante un cuadruplo PARAM
    def process_function_argument(self, argument_address, argument_type):
        if self.current_function is None:
            print("Error: No se puede procesar un argumento si no hay una funcion activa")
            return
        
        # Comprobamos que la funcion exista en la tabla de funciones
        func_info = self.function_table.get(self.current_function)
        if func_info is None:
            print(f"Error: La funcion {self.current_function} no existe en la tabla de funciones")
            return
            
        # Verificamos que la cantidad de argumentos no exceda a la cantidad de parametros esperados
        expected_params = len(func_info["param_addresses"])
        if self.param_counter >= expected_params:
            print(f"Error: Demasiados argumentos para la funcion {self.current_function}, se esperam {expected_params}")
            return
        
        # Obtenemos la direccion del parametro correspondiente 
        param_address = func_info["param_addresses"][self.param_counter]
        
        # Generamos un cuadruplo PARAM
        self.add_quad(operator="PARAM", arg1=argument_address, arg2=None, result=param_address)
        self.param_counter += 1
        print(f"Argumento procesado para {self.current_function}: {argument_address} -> {param_address}")
    
    # Verificamos la llamada de la funcion    
    def verify_function_call(self, func_name, arg_count):
        func_info = self.function_table.get(func_name)
        
        if func_info is None:
            print(f"Error: La funcion {func_name} no existe en la tabla de funciones")
            return False
        
        expected_params = len(func_info["param_addresses"])
        if arg_count != expected_params:
            print(f"Error: Numero incorrecto de argumentos en la funcion {func_name}, se esperan {expected_params} pero se recibieron {arg_count}")
            return False
    
    def end_function_call(self, func_name):
        # Generamos un cuadruplo GOSUB para saltar a la funcion
        func_info = self.function_table.get(func_name)
        
        if func_info is None:
            print(f"Error: La funcion {func_name} no existe en la tabla de funciones")
            return 
        
        start_address = func_info["start_address"]
        
        # Generamos el cuadruplo GOSUB
        self.add_quad(operator="GOSUB", arg1=func_name, arg2=None, result=start_address)
        print(f"Llamada a funcion {func_name} finalizada, GOSUB a {start_address})")
        
        # Restauramos el estado previo a la llamada de funcion
        if self.call_stack:
            saved_state = self.call_stack.pop()
            self.current_function = saved_state["function_name"]
            self.param_counter = saved_state["param_counter"]
            self.argument_stack = saved_state["arguments"]
        else:
            self.current_function = None
            self.param_counter = 0
            self.argument_stack = [] 
    
    def begin_main(self):
        # Llenamos el GOTO pendiente de la posicion 0 al finalizar el analisis    
        if len(self.quads) > 0 and self.quads[0][0] == 'GOTO' and self.quads[0][3] == -1:
            self.fill_quad(0, self.get_current_position())
            print(f"Main Start: GOTO inicial apunta a {self.get_current_position()}")
    
    def start_program(self):
        # Generamos un GOTO al inicio del main
        goto_pos = self.add_quad("GOTO", None, None, -1)
        print(f"Programa iniciado: GOTO al main {goto_pos}")
        
    def end_program(self):
        # Generamos un cuadruplo END para finalizar el programa
        self.add_quad("END", None, None, None)
        print("Programa finalizado: END")
    
    # Helpers
    # Llenamos las partes vacias del cuadruplo con strings vacios
    def evaluate_nil_string(self, val):
        if not val:
            return " "
        else:
            return str(val)
        
    def get_temp_address(self, name, var_type):
        return excecution_memory.add_temp(var_type=var_type, name=name)
    
    # Obtenemos la informacion de una funcion
    def get_function_info(self, func_name):
        return self.function_table.get(func_name)
        
    def print_quads(self):
        if not self.quads:
            print("No se generaron cuadruplos")

        for i, quad in enumerate(self.quads):
            operator, arg1, arg2, result = quad
            
            print(f"{i}: ({operator}, {self.evaluate_nil_string(val=arg1)}, {self.evaluate_nil_string(val=arg2)}, {self.evaluate_nil_string(val=result)})")
            
    def print_function_table(self):
        print("Tabla de Funciones")
        
        for name, info in self.function_table.items():
            print(f"Funcion: {name}")
            print(f"Direccion de inicio: {info["start_address"]}")
            print(f"Direcciones de los parametros: {info["param_addresses"]}")
            print(f"Tipos de los parametros: {info["param_types"]}")
            
    def reset(self):
        self.quads.clear()
        self.operator_stack.clear()
        self.operand_stack.clear()
        self.type_stack.clear()
        self.jump_stack.clear()
        self.function_table.clear()
        self.argument_stack.clear()
        self.call_stack.clear()
        
        self.temp_var_counter = 0
        self.param_counter = 0
        self.current_function = None
        


intermediate_code_generator = IntermediateCodeGenerator()