import ply.yacc as yacc
from lex import tokens
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import intermediate_code_generator
from semantic_cube import semantic_cube
from excecution_memory import excecution_memory

# NOTOTOTOTA
# El primer indice siempre representa al resultado de la gramatica, por ende, podemos asignar cada token a un indice segun su orden de izquierda a derecha

# Símbolo de inicio
start = 'program'

# Analizador semántico global
semantic_analyzer = SemanticAnalyzer()

# Almacenamos a los tipos en un diccionario durante el parsing, almacenando al id del nodo como llave y al tipo de dato como valor
expression_types = {}

# <VARS>
def p_vars(p):
    'vars : VAR var_list'
    p[0] = ('vars', p[2])
    
# <B>
def p_var_list(p):
    'var_list : id_list COLON type SEMI_COLON var_list_prime'
    # Declaramos todas las variables de id_list
    var_type = p[3]
    id_list = p[1]
    
    # Determinar si la variableglobal o local
    is_global = (semantic_analyzer.current_function is None)
    
    for var_name in id_list:
        semantic_analyzer.np_declare_variable(var_name, var_type, is_global)
    
    p[0] = [('var_declaration', p[1], p[3])] + p[5]

# <B'>
def p_var_list_prime(p):
    '''var_list_prime : var_list
                      | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = []
        
# <A>
def p_id_list(p):
    'id_list : ID id_list_prime'
    p[0] = [p[1]] + p[2]

# <A'>
def p_id_list_prime(p):
    '''id_list_prime : COMMA id_list
                     | empty'''
    if len(p) == 3: # len(p) = <numero de simbolos en la produccion> + 1
        p[0] = p[2]
    else: 
        p[0] = []
        
# -------------------------------------------------------
# <EXP>
def p_exp(p):
    '''exp : exp PLUS termino
           | exp MINUS termino
           | termino'''
    if len(p) == 4:
        # Operacion binaria
        operator = p[2]
        
        # Metemos al operador a la cola antes de procesar al termino 
        intermediate_code_generator.push_operator(operator=operator)
        
        # Generamos al cuadruplo
        quad = intermediate_code_generator.generate_arithmetic_operation(semantic_cube=semantic_cube)
        
        left_type = expression_types.get(id(p[1]))
        right_type = expression_types.get(id(p[3]))
        
        # Verificar operacion
        result_type = semantic_analyzer.np_check_operation(
            operator, p[1], p[3], left_type, right_type
        )
        
        p[0] = (p[2], p[1], p[3])
        expression_types[id(p[0])] = result_type
    else:
        p[0] = p[1]
        expression_types[id(p[0])] = expression_types.get(id(p[1]))


# -------------------------------------------------------
# <TERMINO>
def p_termino(p):
    '''termino : termino ASTERISK factor
               | termino FORWARD_SLASH factor
               | factor'''
    if len(p) == 4:
        # Operacion binaria
        operator = p[2]
        
        # Metemos al operador a la pila de opeadores
        intermediate_code_generator.push_operator(operator=operator)
        
        # Generamos un cuadruplo 
        quad = intermediate_code_generator.generate_arithmetic_operation(semantic_cube=semantic_cube)
        
        left_type = expression_types.get(id(p[1]))
        right_type = expression_types.get(id(p[3]))
        
        # Verificar operacion
        result_type = semantic_analyzer.np_check_operation(
            operator, p[1], p[3], left_type, right_type
        )
        
        p[0] = (p[2], p[1], p[3])
        expression_types[id(p[0])] = result_type
    else:
        p[0] = p[1]
        expression_types[id(p[0])] = expression_types.get(id(p[1]))

# -------------------------------------------------------
# <Type>
def p_type(p):
    '''type : INT
            | FLOAT'''
    p[0] = p[1]
    
# ε
def p_empty(p):
    'empty :'
    pass 

# -------------------------------------------------------
# <CTE>
def p_cte(p):
    '''cte : CNT_INT 
           | CNT_FLOAT'''
    p[0] = p[1]
    # Guardar el tipo de literal
    literal_type = semantic_analyzer.get_literal_type(p[1])
    expression_types[id(p[0])] = literal_type

# -------------------------------------------------------
# <EXPRESSION>
def p_expression(p):
    'expression : exp expression_prime'
    if p[2] is not None:
        # Hay operador relacional
        operator, right_operand = p[2]
        
        left_type = expression_types.get(id(p[1]))
        right_type = expression_types.get(id(right_operand))
        
        # Verificar operacion relacional
        result_type = semantic_analyzer.np_check_operation(
            operator, p[1], right_operand, left_type, right_type
        )
        
        # Sacar los operandos de la pila (primero el derecho, luego el izquierdo)
        right_addr, _ = intermediate_code_generator.pop_operand()
        left_addr, _ = intermediate_code_generator.pop_operand()
        
        # Generamos un cuadruplo para procesar operadores relacionales
        temp = intermediate_code_generator.add_temp()
        temp_address = intermediate_code_generator.get_temp_address(name=temp, var_type="int")
        
        intermediate_code_generator.add_quad(operator=operator, arg1=left_addr, arg2=right_addr, result=temp_address)
        intermediate_code_generator.push_operand(operand=temp_address, operand_type=result_type)
        
        p[0] = (operator, p[1], right_operand)
        expression_types[id(p[0])] = result_type
    else:
        p[0] = p[1]
        expression_types[id(p[0])] = expression_types.get(id(p[1]))

# <EXPRESSION'>
def p_expression_prime(p):
    '''expression_prime : GREATER_THAN exp
                        | LOWER_THAN exp
                        | NOT_EQUAL exp
                        | empty'''
    if len(p) == 3:
        p[0] = (p[1], p[2])
    else:
        p[0] = None

# -------------------------------------------------------
# <F_CALL> - Llamada a funcion como statement (con ;)
def p_f_call(p):
    '''f_call : ID era L_PARENTHESIS R_PARENTHESIS gosub SEMI_COLON
              | ID era L_PARENTHESIS expression_list R_PARENTHESIS gosub SEMI_COLON'''
    
    func_name = p[1]
    
    # Verificamos que la funcion exista
    func = semantic_analyzer.np_start_function_call(func_name)
    
    # Continuar si la función existe
    if func is not None:
        if len(p) == 7:
            # Sin argumentos
            semantic_analyzer.np_check_function_call(func_name, [])
            p[0] = ('f_call', p[1], [])
        else:
            # Con argumentos
            arg_list = p[4]
            # Obtenemos los tipos de los argumentos
            arg_types = [expression_types.get(id(arg)) for arg in arg_list]
            # Filtramos valores nulos
            arg_types = [t for t in arg_types if t is not None]
            
            semantic_analyzer.np_check_function_call(func_name, arg_types)
            p[0] = ('f_call', p[1], arg_list)
    else:
        # Creamos el nodo aunque la funcion no exista
        if len(p) == 7:
            p[0] = ('f_call', p[1], [])
        else:
            p[0] = ('f_call', p[1], p[4])

# Llamada a funcion como expresion (sin ;) - para usar el valor de retorno
def p_f_call_expr(p):
    '''f_call_expr : ID era L_PARENTHESIS R_PARENTHESIS gosub
                   | ID era L_PARENTHESIS expression_list R_PARENTHESIS gosub'''
    
    func_name = p[1]
    
    # Verificamos que la funcion exista
    func = semantic_analyzer.np_start_function_call(func_name)
    
    if func is not None:
        if len(p) == 6:
            # Sin argumentos
            semantic_analyzer.np_check_function_call(func_name, [])
        else:
            # Con argumentos
            arg_list = p[4]
            arg_types = [expression_types.get(id(arg)) for arg in arg_list]
            arg_types = [t for t in arg_types if t is not None]
            semantic_analyzer.np_check_function_call(func_name, arg_types)
        
        # Obtener el tipo de retorno y la direccion de la variable de retorno
        return_type = intermediate_code_generator.get_function_return_type(func_name)
        return_address = intermediate_code_generator.get_function_return_address(func_name)
        
        if return_type and return_type != 'void' and return_address:
            # Copiamos el resultado a una variable temporal para evitar que se sobre escriba en doble recursion
            temp = intermediate_code_generator.add_temp()
            temp_address = intermediate_code_generator.get_temp_address(name=temp, var_type=return_type)
            intermediate_code_generator.add_quad(operator='=', arg1=return_address, arg2=None, result=temp_address)
            
            # Pushear la direccion de retorno como operando
            intermediate_code_generator.push_operand(temp_address, return_type)
        else:
            return_type = None
    else:
        return_type = None
    
    p[0] = ('f_call_expr', p[1])
    expression_types[id(p[0])] = return_type
        
# <A>
def p_expression_list(p):
    '''expression_list : expression expression_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# <A'>
def p_expression_list_prime(p):
    '''expression_list_prime : COMMA expression_list
                             | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []
        
# ERA
def p_era(p):
    'era : empty'
    # Obtenemos el nombre de la funcion desde el parser
    func_name = p[-1]
    intermediate_code_generator.begin_function_call(func_name=func_name)
    p[0] = None

# GOSUB - Genera los PARAMs y el GOSUB
def p_gosub(p):
    'gosub : empty'
    # Buscar el nombre de la funcion en el stack del parser
    func_name = None
    for item in reversed(p.stack):
        if hasattr(item, 'value') and isinstance(item.value, str) and item.value.isidentifier():
            if item.value not in ['if', 'else', 'while', 'do', 'print', 'main', 'end', 'program', 'var', 'void', 'int', 'float', 'return']:
                func_name = item.value
                break
    
    if func_name:
        # Obtenemos la informacion de la funcion para saber cuantos parametros pespera
        func_info = intermediate_code_generator.get_function_info(func_name)
        if func_info:
            param_count = len(func_info["param_addresses"])
            
            # Sacamos los argumentos de la pila (orden inverso)
            args = []
            for _ in range(param_count):
                operand, operand_type = intermediate_code_generator.pop_operand()
                if operand is not None:
                    args.append((operand, operand_type))
            
            # Revertir para obtener el orden correcto
            args.reverse()
            
            # Generar PARAMs
            for i, (operand, operand_type) in enumerate(args):
                if i < len(func_info["param_addresses"]):
                    param_address = func_info["param_addresses"][i]
                    intermediate_code_generator.add_quad("PARAM", operand, None, param_address)
        
        # Generar GOSUB
        intermediate_code_generator.end_function_call(func_name)
    
    p[0] = None
        
# -------------------------------------------------------
# <Body>
def p_body(p):
    '''body : L_CBRACKET R_CBRACKET
            | L_CBRACKET statement_list R_CBRACKET'''
    if len(p) == 3:
        p[0] = ('body', [])
    else:
        p[0] = ('body', p[2])

# <A> (statement_list)
def p_statement_list(p):
    '''statement_list : statement statement_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# <A'> (statement_list_prime)
def p_statement_list_prime(p):
    '''statement_list_prime : statement_list
                            | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = []        
        
# -------------------------------------------------------
# <STATEMENT>
def p_statement(p):
    '''statement : assign
                 | condition
                 | cycle
                 | f_call
                 | print_stmt
                 | return_stmt_inline''' # Permite utilizar el valor de una funcion con retorno sin asignarlo antes a una variable 
    p[0] = p[1]

# Return como statement (dentro del body de una funcion)
def p_return_stmt_inline(p):
    '''return_stmt_inline : RETURN expression SEMI_COLON'''
    func_name = semantic_analyzer.current_function
    if func_name is None:
        semantic_analyzer.add_error("La declaracion de 'return' debe estar dentro de una funcion")
        p[0] = None
        return

    expr_type = expression_types.get(id(p[2]))
    
    # Verificar tipo de retorno
    semantic_analyzer.np_check_function_return(func_name, expr_type)
    
    # Generar cuadruplo de retorno
    operand, operand_type = intermediate_code_generator.pop_operand()
    intermediate_code_generator.generate_return(func_name, operand)
    
    p[0] = ('return', p[2])

# -------------------------------------------------------
# <CONDITION>
def p_condition(p):
    '''condition : IF L_PARENTHESIS expression R_PARENTHESIS if_condition body else_part SEMI_COLON'''
    p[0] = ('if', p[3], p[6], p[7])

def p_if_condition(p):
    '''if_condition : empty'''
    # Se ejecuta DESPUÉS de evaluar la expresión
    intermediate_code_generator.begin_if()
    p[0] = None

def p_else_part(p):
    '''else_part : begin_else body end_else
                 | end_if_no_else'''
    if len(p) == 4:
        # Con else
        p[0] = p[2]
    else:
        # Sin else
        p[0] = None

# Puntos neurálgicos para else
def p_begin_else(p):
    'begin_else : ELSE'
    intermediate_code_generator.begin_else()
    p[0] = p[1]

def p_end_else(p):
    'end_else : empty'
    intermediate_code_generator.end_else()
    p[0] = None

def p_end_if_no_else(p):
    'end_if_no_else : empty'
    # Cuando no hay else, llenar el salto del if
    intermediate_code_generator.end_if()
    p[0] = None
                 
# -------------------------------------------------------
# <CYCLE>
def p_cycle(p):
    'cycle : WHILE begin_while while_expression R_PARENTHESIS DO body end_while SEMI_COLON'
    p[0] = ('while', p[3], p[6])

# Guardamos la posicion antes de la expresion 
def p_begin_while(p):
    'begin_while : L_PARENTHESIS'
    intermediate_code_generator.begin_while()
    p[0] = p[1]

def p_while_expression(p):
    'while_expression : expression'
    intermediate_code_generator.generate_while_condition()
    p[0] = p[1]

def p_end_while(p):
    'end_while : empty'
    intermediate_code_generator.end_while()
    p[0] = None
    
# -------------------------------------------------------
# <PRINT>
def p_print_stmt(p): 
    '''print_stmt : PRINT L_PARENTHESIS print_expression_list R_PARENTHESIS SEMI_COLON'''
    # Cuadruplos para print
    intermediate_code_generator.generate_print(len(p[3]))
    p[0] = ('print', p[3])

# <A> (print_expression_list)
def p_print_expression_list(p):
    '''print_expression_list : print_item print_expression_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# Agregamos una nueva regla para manejar a los items de print 
def p_print_item(p):
    '''print_item : expression
                  | CNT_STRING'''
    if isinstance(p[1], str) and p[1].startswith('"'):
        # Agregamos al string como constante
        const_address = excecution_memory.add_const(p[1], 'string')
        intermediate_code_generator.push_operand(const_address, 'string')
    p[0] = p[1]

# <A'> (print_expression_list_prime)
def p_print_expression_list_prime(p):
    '''print_expression_list_prime : COMMA print_expression_list
                                   | empty'''
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

# -------------------------------------------------------
# <Factor>
def p_factor(p):
    """factor : L_PARENTHESIS expression R_PARENTHESIS 
              | PLUS ID
              | PLUS cte
              | MINUS ID
              | MINUS cte
              | ID
              | cte
              | f_call_expr"""
    if len(p) == 4:
        # Parentesis
        # Abrimos a los parentesis antes de procesar la gramatica
        intermediate_code_generator.open_parenthesis()
        p[0] = p[2]
        expression_types[id(p[0])] = expression_types.get(id(p[2]))
        intermediate_code_generator.close_parenthesis(semantic_cube=semantic_cube)
    
    elif len(p) == 3:
        # Unario
        # No le generamos un cuadruplo ya que matematicamente no tiene un efecto
        if p[1] == '+':
            p[0] = p[2]
            expression_types[id(p[0])] = expression_types.get(id(p[2]))
        else: 
            operand, operand_type = intermediate_code_generator.pop_operand()
            
            # Creamos una direccion de memoria para la temporal creada
            temp = intermediate_code_generator.add_temp()
            temp_address = intermediate_code_generator.get_temp_address(name=temp, var_type=operand_type)
            
            intermediate_code_generator.add_quad(operator="UMINUS", arg1=operand, arg2=None, result=temp_address)
            intermediate_code_generator.push_operand(operand=temp_address, operand_type=operand_type)
            
            # Menos unario
            p[0] = ('unary_minus', p[2])
            expression_types[id(p[0])] = expression_types.get(id(p[2]))
    else: 
        # ID, constante, o f_call_expr
        p[0] = p[1]
        
        # Si es una tupla de f_call_expr, el tipo ya fue asignado
        if isinstance(p[1], tuple) and p[1][0] == 'f_call_expr':
            # El tipo ya fue asignado en p_f_call_expr
            expression_types[id(p[0])] = expression_types.get(id(p[1]))
        elif isinstance(p[1], str):
            # Si es ID, verificar que existe
            var_type = semantic_analyzer.np_check_variable(p[1])
            expression_types[id(p[0])] = var_type
            
            # Generamos la direccion de memoria y la empujamos a la pila de operandos
            var_address = excecution_memory.var_dict.get(p[1])
            intermediate_code_generator.push_operand(operand=var_address, operand_type=var_type)
        else:
            # Si es constante, ya se asigno en p_cte
            var_type = expression_types.get(id(p[1]))
            expression_types[id(p[0])] = var_type
            
            # Generamos la direccion de memoria y empujamos a la pila de operandos
            const_address = excecution_memory.add_const(value=p[1], value_type=var_type)
            intermediate_code_generator.push_operand(operand=const_address, operand_type=var_type)
        
# -------------------------------------------------------
# <FUNCS>
# Funciones pueden ser void o tener tipo de retorno (int/float)
# El return ahora es un statement dentro del body
def p_funcs(p):
    """funcs : func_type ID func_start L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET vars body R_SBRACKET func_end SEMI_COLON
             | func_type ID func_start L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET body R_SBRACKET func_end SEMI_COLON
             | func_type ID func_start L_PARENTHESIS R_PARENTHESIS L_SBRACKET vars body R_SBRACKET func_end SEMI_COLON
             | func_type ID func_start L_PARENTHESIS R_PARENTHESIS L_SBRACKET body R_SBRACKET func_end SEMI_COLON"""

    func_name = p[2]

    # Finalizar funcion
    semantic_analyzer.np_end_function(func_name)

    if len(p) == 13:
        # Con params y vars
        p[0] = ('func', p[1], p[2], p[5], p[8], p[9])
    elif len(p) == 12:
        if p[5] == ')':
            # Sin params, con vars
            p[0] = ('func', p[1], p[2], [], p[7], p[8])
        else:
            # Con params, sin vars
            p[0] = ('func', p[1], p[2], p[5], None, p[8])
    else:
        # Sin params ni vars
        p[0] = ('func', p[1], p[2], [], None, p[7])

# Tipo de retorno de funcion
def p_func_type(p):
    """func_type : VOID
                 | INT
                 | FLOAT"""
    p[0] = p[1]


# Helper para inicio de funcion, se llama antes de procesar a los parametros
def np_aux_start_function(func_name):
    semantic_analyzer.np_start_function(func_name, 'void')

# <A>
def p_param_list(p):
    '''param_list : ID COLON type param param_list_prime'''
    # El parametro ya fue agregado en p_param
    param_name = p[1]
    param_type = p[3]
    
    if p[5] is not None and len(p[5]) > 0:
        p[0] = [(p[1], p[3])] + p[5]
    else:
        p[0] = [(p[1], p[3])]


def p_param(p):
    '''param : empty'''
    # Obtener nombre y tipo del parametro
    param_name = p[-3]  # ID
    param_type = p[-1]  # type
    
    # Agregar parametro al semantic analyzer
    semantic_analyzer.np_add_parameter(param_name, param_type)
    
    # Obtener direccion del parametro y registrarla
    param_address = excecution_memory.var_dict.get(param_name)
    
    # Obtener nombre de la funcion actual
    func_name = semantic_analyzer.current_function
    if func_name and param_address:
        intermediate_code_generator.add_function_param(func_name, param_address, param_type)
    
    p[0] = None
    
# <A'> 
def p_param_list_prime(p):
    """param_list_prime : COMMA param_list
                        | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []
        
def p_func_start(p):
    '''func_start : empty'''
    func_name = p[-1]  # ID está en p[-1]
    func_type = p[-2]  # func_type está en p[-2]
    
    # Iniciar funcion con el tipo de retorno
    semantic_analyzer.np_start_function(func_name, func_type)
    intermediate_code_generator.register_function(func_name, func_type)
    p[0] = None
    
def p_func_end(p):
    'func_end : empty'
    # Usar el current_function del semantic_analyzer
    func_name = semantic_analyzer.current_function
    if func_name:
        intermediate_code_generator.end_function(func_name)  # Genera ENDFUNC
    p[0] = None


# -------------------------------------------------------
# <Program>
def p_program(p):
    """program : PROGRAM ID SEMI_COLON program_start vars func_list MAIN main_start body program_end END
               | PROGRAM ID SEMI_COLON program_start func_list MAIN main_start body program_end END
               | PROGRAM ID SEMI_COLON program_start vars MAIN main_start body program_end END
               | PROGRAM ID SEMI_COLON program_start MAIN main_start body program_end END"""
    
    # Iniciar programa
    program_name = p[2]
    semantic_analyzer.np_start_program(program_name)
    
    # len(p) = número de símbolos + 1
    if len(p) == 12:
        # vars + func_list
        # PROGRAM ID ; program_start vars func_list MAIN main_start body program_end END
        # 1       2  3 4             5    6         7    8          9    10          11
        p[0] = ('program', p[2], p[5], p[6], p[9])
    elif len(p) == 11:
        # func_list sin vars  O  vars sin func_list
        if isinstance(p[5], tuple) and p[5][0] == 'vars':
            # vars sin func_list
            # PROGRAM ID ; program_start vars MAIN main_start body program_end END
            # 1       2  3 4             5    6    7          8    9           10
            p[0] = ('program', p[2], p[5], [], p[8])
        else:
            # func_list sin vars
            # PROGRAM ID ; program_start func_list MAIN main_start body program_end END
            # 1       2  3 4             5         6    7          8    9           10
            p[0] = ('program', p[2], None, p[5], p[8])
    elif len(p) == 10:
        # Sin vars ni func_list
        # PROGRAM ID ; program_start MAIN main_start body program_end END
        # 1       2  3 4             5    6          7    8           9
        p[0] = ('program', p[2], None, [], p[7])

# <A> 
def p_func_list(p):
    '''func_list : funcs func_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        # Hay más funciones
        p[0] = [p[1]] + p[2]
    else:
        # Solo una función
        p[0] = [p[1]]

# <A'> 
def p_func_list_prime(p):
    """func_list_prime : func_list
                       | empty"""
    if len(p) == 2 and p[1] is not None:
        # Recursion, mas funciones
        p[0] = p[1]
    else:
        p[0] = []

# Inicio del programa 
def p_program_start(p):
    'program_start : empty'
    intermediate_code_generator.start_program()
    p[0] = None

# Cierre del programa 
def p_main_start(p):
    'main_start : empty'
    intermediate_code_generator.begin_main()
    p[0] = None
    
def p_program_end(p):
    'program_end : empty'
    intermediate_code_generator.end_program()
    p[0] = None

# -------------------------------------------------------
# <ASSIGN>
def p_assign(p):
    'assign : ID EQUAL expression SEMI_COLON'
    
    var_name = p[1]
    expr_type = expression_types.get(id(p[3]))
    
    # Verificar asignacion
    semantic_analyzer.np_check_assignment(var_name, expr_type)
    
    # Generamos un cuadruplo
    var_address = excecution_memory.var_dict.get(var_name)
    intermediate_code_generator.generate_assignation(var_name=var_address)
    
    p[0] = ('assign', p[1], p[3])


# -------------------------------------------------------
# Excepcion para errores de sintaxis
class SyntaxError(Exception):
    pass

# Manejo de errores
def p_error(p):
    if p:
        error_msg = f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}"
        print(error_msg)
        raise SyntaxError(error_msg)
    else:
        error_msg = "Syntax error: Unexpected end of file (EOF)"
        print(error_msg)
        raise SyntaxError(error_msg)


# Crear el parser
parser = yacc.yacc()