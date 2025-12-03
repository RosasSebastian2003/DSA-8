class VirtualMachine:
    def __init__(self):
        self.memory = {
            'global': {},      # Variables globales (1000-2999)
            'local': {},       # Variables locales (3000-4999) - por contexto
            'temp': {},        # Temporales (5000-6999) - por contexto
            'const': {}        # Constantes (7000-9999)
        }
        
        # Pila de contextos de ejecucion para llamadas a funcion
        # Cada contexto tiene su propia memoria local y temporal
        self.execution_stack = []
        
        # Contexto actual de ejecucion
        self.current_context = None
        
        # Instruction Pointer - apunta al cuadruplo actual
        self.ip = 0
        
        # Lista de cuadruplos a ejecutar
        self.quads = []
        
        # Directorio de funciones para consultar informacion
        self.function_directory = None
        
        # Flag para detener la ejecucion
        self.running = False
        
        self.address_ranges = {
            'global_int': (1000, 1999),
            'global_float': (2000, 2999),
            'local_int': (3000, 3999),
            'local_float': (4000, 4999),
            'temp_int': (5000, 5999),
            'temp_float': (6000, 6999),
            'const_int': (7000, 7999),
            'const_float': (8000, 8999),
            'const_string': (9000, 9999)
        }
    
    # Determina el segmento de memoria basado en la direccion virtual
    def get_segment(self, address):
        if 1000 <= address <= 1999:
            return 'global', 'int'
        elif 2000 <= address <= 2999:
            return 'global', 'float'
        elif 3000 <= address <= 3999:
            return 'local', 'int'
        elif 4000 <= address <= 4999:
            return 'local', 'float'
        elif 5000 <= address <= 5999:
            return 'temp', 'int'
        elif 6000 <= address <= 6999:
            return 'temp', 'float'
        elif 7000 <= address <= 7999:
            return 'const', 'int'
        elif 8000 <= address <= 8999:
            return 'const', 'float'
        elif 9000 <= address <= 9999:
            return 'const', 'string'
        else:
            raise RuntimeError(f"Direccion de memoria invalida: {address}")
    
    # Obtener el valor almacenado en una direccion virtual
    def get_value(self, address):
        if address is None:
            return None
            
        segment, var_type = self.get_segment(address)
        
        if segment == 'global' or segment == 'const':
            # Variables globales y constantes estan en memoria principal
            if address in self.memory[segment]:
                return self.memory[segment][address]
            else:
                # Valor por defecto segun tipo
                return 0 if var_type in ['int', 'float'] else ""
        else:
            # Locales y temporales estan en el contexto actual
            if self.current_context and address in self.current_context[segment]:
                return self.current_context[segment][address]
            elif address in self.memory[segment]:
                # Fallback a memoria principal (para main)
                return self.memory[segment][address]
            else:
                return 0 if var_type in ['int', 'float'] else ""
    
    
    def set_value(self, address, value):
        if address is None:
            return
            
        segment, var_type = self.get_segment(address)
        
        # Conversion de tipo si es necesario
        if var_type == 'int' and isinstance(value, float):
            value = int(value)
        elif var_type == 'float' and isinstance(value, int):
            value = float(value)
        
        if segment == 'global' or segment == 'const':
            self.memory[segment][address] = value
        else:
            if self.current_context:
                self.current_context[segment][address] = value
            else:
                self.memory[segment][address] = value
    
    def load_quads(self, quads):
        # Cargamos los cuadruplos a ejecutar
        self.quads = quads
        self.ip = 0
        
        # Verificar que exista el cuadruplo END
        has_end = any(q[0] == 'END' for q in quads)
        if not has_end and len(quads) > 0:
            print("Advertencia: No se encontro cuadruplo END. El programa podria no terminar correctamente.")
    
    def reset(self):
        """Reinicia la maquina virtual"""
        self.memory = {
            'global': {},
            'local': {},
            'temp': {},
            'const': {}
        }
        self.execution_stack = []
        self.current_context = None
        self.ip = 0
        self.quads = []
        self.running = False
        if hasattr(self, 'pending_context'):
            del self.pending_context
    
    # Cargamos las constantes del compilador a la memoria
    def load_constants(self, const_dict):
        for (value, _), address in const_dict.items():
            self.memory['const'][address] = value
    
    # Crea un nuevo contexto de ejecucion para una llamada a funcion
    def create_context(self, func_name):
        context = {
            'name': func_name,
            'local': {},
            'temp': {},
            'return_address': self.ip  # Donde regresar despues de la llamada
        }
        return context
    
    def push_context(self, context):
        # Guarda el contexto actual y activa el nuevo
        if self.current_context:
            self.execution_stack.append(self.current_context)
        self.current_context = context
    
    def pop_context(self):
        # Restaura el contexto anterior
        if self.execution_stack:
            self.current_context = self.execution_stack.pop()
        else:
            self.current_context = None
    
    def execute(self):
        # Ejecuta los cuadruplos cargados
        self.running = True
        self.ip = 0
        
        # Proteccion contra loops infinitos
        max_iterations = 100000
        iteration_count = 0
        
        while self.running and self.ip < len(self.quads):
            iteration_count += 1
            if iteration_count > max_iterations:
                print(f"\nError: Posible loop infinito detectado despues de {max_iterations} iteraciones")
                print(f"IP actual: {self.ip}, Cuadruplo: {self.quads[self.ip]}")
                break
                
            quad = self.quads[self.ip]
            operator, arg1, arg2, result = quad
            
            # Dispatch de operaciones
            if operator == '+':
                self.exec_add(arg1, arg2, result)
            elif operator == '-':
                self.exec_sub(arg1, arg2, result)
            elif operator == '*':
                self.exec_mult(arg1, arg2, result)
            elif operator == '/':
                self.exec_div(arg1, arg2, result)
            elif operator == '=':
                self.exec_assign(arg1, result)
            elif operator == '>':
                self.exec_greater(arg1, arg2, result)
            elif operator == '<':
                self.exec_less(arg1, arg2, result)
            elif operator == '!=':
                self.exec_not_equal(arg1, arg2, result)
            elif operator == 'GOTO':
                self.exec_goto(result)
                continue  # No incrementar instruction pointer
            elif operator == 'GOTOF':
                if self.exec_gotof(arg1, result):
                    continue  # Salto realizado, no incrementar instruction pointer
            elif operator == 'GOTOT':
                if self.exec_gotot(arg1, result):
                    continue
            elif operator == 'PRINT':
                self.exec_print(arg1)
            elif operator == 'UMINUS':
                self.exec_uminus(arg1, result)
            elif operator == 'ERA':
                self.exec_era(arg1)
            elif operator == 'PARAM':
                self.exec_param(arg1, result)
            elif operator == 'GOSUB':
                self.exec_gosub(arg1, result)
                continue  # El IP se maneja en gosub
            elif operator == 'ENDFUNC':
                self.exec_endfunc()
                continue
            elif operator == 'END':
                self.running = False
                continue
            else:
                print(f"Operador desconocido: {operator}")
            
            self.ip += 1
    
    
    # Operaciones aritmeticas
    # result = arg1 + arg2
    def exec_add(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, val1 + val2)
    
    # Resta: result = arg1 - arg2
    def exec_sub(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, val1 - val2)
    
     # Multiplicacion: result = arg1 * arg2
    def exec_mult(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, val1 * val2)
    
    # result = arg1 / arg2
    def exec_div(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        if val2 == 0:
            raise RuntimeError("Error: Division por cero")
        self.set_value(result, val1 / val2)
    
    # Menos unario: result = -arg1
    def exec_uminus(self, arg1, result):
        val = self.get_value(arg1)
        self.set_value(result, -val)
    
    # Operaciones relacionales
    # result = 1 si arg1 > arg2, sino 0
    def exec_greater(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, 1 if val1 > val2 else 0)
    
    # result = 1 si arg1 < arg2, sino 0
    def exec_less(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, 1 if val1 < val2 else 0)
    
    # result = 1 si arg1 != arg2, sino 0
    def exec_not_equal(self, arg1, arg2, result):
        val1 = self.get_value(arg1)
        val2 = self.get_value(arg2)
        self.set_value(result, 1 if val1 != val2 else 0)
    
    # Asignacion
    def exec_assign(self, arg1, result):
        """Asignacion: result = arg1"""
        val = self.get_value(arg1)
        self.set_value(result, val)
    
    # Control de flujo
    # GOTO
    def exec_goto(self, target):
        self.ip = target
    
    # GOTOF
    def exec_gotof(self, condition, target):
        """Salto si falso (condicion == 0)"""
        val = self.get_value(condition)
        if val == 0:
            self.ip = target
            return True
        return False
    
    # GOTOT
    def exec_gotot(self, condition, target):
        val = self.get_value(condition)
        if val != 0:
            self.ip = target
            return True
        return False
    
    # Etrada/salida
    # Imprimir el valor de arg1
    def exec_print(self, arg1):
        val = self.get_value(arg1)
        # Si es string, remover comillas
        if isinstance(val, str) and val.startswith('"') and val.endswith('"'):
            val = val[1:-1]
        print(val, end=' ')
    
    # Funciones
    # Preparamos el espacio de memora para la funcion y creamos un nuevo contexto de ejecucion
    def exec_era(self, func_name):
        context = self.create_context(func_name)
        # Guardamos el contexto pendiente (se activara en GOSUB)
        self.pending_context = context
    
    # Pasamos un argumento al parametro de la funcion 
    def exec_param(self, arg_address, param_address):
        value = self.get_value(arg_address)
        # Guardamos en el contexto pendiente
        if hasattr(self, 'pending_context'):
            segment, _ = self.get_segment(param_address)
            self.pending_context[segment][param_address] = value
    
    # GOSUB
    # Saltamos a la funcion y activamos el contexto
    def exec_gosub(self, func_name, start_address):
        if hasattr(self, 'pending_context'):
            self.pending_context['return_address'] = self.ip + 1
            self.push_context(self.pending_context)
            del self.pending_context
        
        self.ip = start_address
    
    # ENDFUNC
    # Termina la ejecucion de la funcion, restaura el contexto anterior y regresa a la direccion de retorno
    def exec_endfunc(self):
        return_address = self.current_context['return_address']
        self.pop_context()
        self.ip = return_address
    
    # Helpers
    def print_memory_state(self):
        """Imprime el estado actual de la memoria (para debugging)."""
        print("\n=== Estado de Memoria ===")
        print("Global:", self.memory['global'])
        print("Constantes:", self.memory['const'])
        if self.current_context:
            print("Contexto actual:", self.current_context['name'])
            print("  Local:", self.current_context['local'])
            print("  Temp:", self.current_context['temp'])
        print("========================\n")


# Singleton de la maquina virtual
virtual_machine = VirtualMachine()