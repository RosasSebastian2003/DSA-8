class ExcecutionMemory:
    def __init__(self):
        # Contadores para asignar a la siguiente direccion disponible
        self.memory_counters = {
            'global_int' : 1000,
            'global_float' : 2000,
            'local_int' : 3000,
            'local_float' : 4000,
            'temp_int' : 5000,
            'temp_float' : 6000,
            'const_int' : 7000,
            'const_float' : 8000,
            'const_string' : 9000
        }
        
        # Diccionario con los limites superiores para cada grupo
        self.assignment_limits = {
            'global_int' : 1999,
            'global_float' : 2999,
            'local_int' : 3999,
            'local_float' : 4999,
            'temp_int' : 5999,
            'temp_float' : 6999,
            'const_int' : 7999,
            'const_float' : 8999,
            'const_string' : 9999
        }
        
        # Definimos un mapa donde almacenaremos a la direccion de memoria como llave y al valor al que corresponde como valor, esto puede ser un id o un literal
        self.debug_memory = {}
        
        # Mapa para almacenar variables usando su nombre como llave y su direccion como valor 
        # Este diccionario nos sirve para tener un lookup rapido de variables, lo cual es necesario ya que el programa consulta a la memoria constantemente
        # El diccionario tiene complejidad lineal para busqueda, lo que nos permite realizar consultas rapidas, si iteraramos un arreglo, tendriamos un tiempo de busqueda O(n),
        # por lo que la velocidad de ejecucion de nuestro programa dependeria de que tan grande sea este
        self.var_dict = {}
        
        # Mantenemos un diccionario de constantes para evitar la duplicacion de constantes
        # Utilizaremos una tupla como llave, donde guardaremos al valor de la constante y su tipo, esto nos permitira diferenciar entre valores similares 
        # como 5 y 5.0, donde 5 es un entero y 5.0 es un float, por lo que deben de recibir direcciones de memoria distintas
        self.const_dict = {}
        
    def assign_address(self, scope, var_type, id=None):
        # Revizamos si aun tenemos espacio disponible en la memoria 
            
        key = f"{scope}_{var_type}"
            
        if self.memory_counters[key] > self.assignment_limits[key]:
            print(f"Memoria excedida para {key}")
            return -1
        
        # Asignamos una direccion de memoria dependiendo del tipo de la variable y su alcance y aumentamos el contador 
        address = self.memory_counters[key]
        self.memory_counters[key] += 1
        
        if id != None:
            self.debug_memory[address] = id
            
            if scope == "global" or scope == "local":
                self.var_dict[id] = address
        
        return address
    
    def add_variable(self, var_name, var_type, scope="global"):
        if var_name in self.var_dict:
            print(f"La variable {var_name} ya fue declarada")
            return 

        address = self.assign_address(scope=scope, var_type=var_type, id=var_name)
        
        return address
        
    def add_const(self, value, value_type):
        key = (value, value_type)
        
        if key in self.const_dict:
            return self.const_dict[key]
        
        # Si la constante aun no existe
        address = self.assign_address(scope="const", var_type=value_type, id=str(value))
        self.const_dict[key] = address
        
        return address
    
    def add_temp(self, var_type, name):
        return self.assign_address(scope='temp', var_type=var_type, id=name)
    
    def reset(self):
        self.__init__()
        
excecution_memory = ExcecutionMemory()