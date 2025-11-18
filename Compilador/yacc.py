import ply.yacc as yacc
from lex import tokens
from semantic_analyzer import SemanticAnalyzer
from intermediate_code_generator import intermediate_code_generator
from semantic_cube import semantic_cube

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
        left_operand = p[1]
        # Hay operador relacional
        operator, right_operand = p[2]
        left_type = expression_types.get(id(p[1]))
        right_type = expression_types.get(id(right_operand))
        
        # Verificar operacion relacional
        result_type = semantic_analyzer.np_check_operation(
            operator, p[1], right_operand, left_type, right_type
        )
        
        # Generamos un cuadruplo para procesar operadores relacionales
        temp = intermediate_code_generator.add_temp()
        intermediate_code_generator.add_quad(operator=operator,arg1=left_operand,arg2=right_operand,result=temp)
        intermediate_code_generator.push_operand(operand=temp, operand_type=result_type)
        
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
# <F_CALL>
def p_f_call(p):
    '''f_call : ID L_PARENTHESIS R_PARENTHESIS SEMI_COLON
              | ID L_PARENTHESIS expression_list R_PARENTHESIS SEMI_COLON'''
    
    func_name = p[1]
    
    # Verificamos que la funcion exista
    func = semantic_analyzer.np_start_function_call(func_name)
    
    # Continuar si la función existe
    if func is not None:
        if len(p) == 5:
            # Sin argumentos
            semantic_analyzer.np_check_function_call(func_name, [])
            p[0] = ('f_call', p[1], [])
        else:
            # Con argumentos
            arg_list = p[3]
            # Obtenemos los tipos de los argumentos
            arg_types = [expression_types.get(id(arg)) for arg in arg_list]
            # Filtramos valores nulos
            arg_types = [t for t in arg_types if t is not None]
            
            semantic_analyzer.np_check_function_call(func_name, arg_types)
            p[0] = ('f_call', p[1], p[3])
    else:
        # Creamos el nodo aunque la funcion no exista
        if len(p) == 5:
            p[0] = ('f_call', p[1], [])
        else:
            p[0] = ('f_call', p[1], p[3])
        
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
                 | print_stmt'''
    p[0] = p[1]

# -------------------------------------------------------
# <CONDITION>
def p_condition(p):
    """condition : IF L_PARENTHESIS expression R_PARENTHESIS body SEMI_COLON
                 | IF L_PARENTHESIS expression R_PARENTHESIS body ELSE body SEMI_COLON"""
    if len(p) == 7:
        # If sin else
       #intermediate_code_generator.end_if()
        
        p[0] = ('if', p[3], p[5], None)
    else:
        # if con else
        # p[1] = IF
        # p[2] = (
        # p[3] = expression
        # p[4] = )
        # p[5] = body (then)
        # p[6] = ELSE
        # p[7] = body (else)
        # p[8] = ;
        
        #intermediate_code_generator.end_else()
        p[0] = ('if', p[3], p[5], p[7])         
                 
# -------------------------------------------------------
# <CYCLE>
def p_cycle(p):
    'cycle : WHILE L_PARENTHESIS expression R_PARENTHESIS DO body SEMI_COLON'
    p[0] = ('while', p[3], p[6])
    
# -------------------------------------------------------
# <PRINT>
def p_print_stmt(p): 
    '''print_stmt : PRINT L_PARENTHESIS print_expression_list R_PARENTHESIS SEMI_COLON'''
    # Cuadruplos para print
    intermediate_code_generator.generate_print(len(p[3]))
    p[0] = ('print', p[3])

# <A> (print_expression_list)
def p_print_expression_list(p):
    '''print_expression_list : expression print_expression_list_prime 
                             | CNT_STRING print_expression_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

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
              | cte"""
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
            temp = intermediate_code_generator.add_temp()
            intermediate_code_generator.add_quad(operator="UMINUS", arg1=operand, arg2=None, result=temp)
            intermediate_code_generator.push_operand(operand=temp, operand_type=operand_type)
            
            # Menos unario
            p[0] = ('unary_minus', p[2])
            expression_types[id(p[0])] = expression_types.get(id(p[2]))
    else: 
        # ID o constante
        p[0] = p[1]
        
        if isinstance(p[1], str):
            # Si es ID, verificar que existe
            var_type = semantic_analyzer.np_check_variable(p[1])
            expression_types[id(p[0])] = var_type
            
            # Empujamos a la pila de operandos
            intermediate_code_generator.push_operand(operand=p[1], operand_type=var_type)
        else:
            # Si es constante, ya se asigno en p_cte
            var_type = expression_types.get(id(p[1]))
            expression_types[id(p[0])] = var_type
            
            # Empujamos a la pila de operandos
            intermediate_code_generator.push_operand(operand=p[1], operand_type=var_type)
        
# -------------------------------------------------------
# <FUNCS>
def p_funcs(p):
    """funcs : VOID ID L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET vars body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS R_PARENTHESIS L_SBRACKET vars body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS R_PARENTHESIS L_SBRACKET body R_SBRACKET SEMI_COLON"""
    
    func_name = p[2]
    
    # Finalizar funcion
    semantic_analyzer.np_end_function(func_name)
    
    if len(p) == 11:
        p[0] = ('func', p[2], p[4], p[7], p[8])
    elif len(p) == 10:
        if p[4] == ')':
            p[0] = ('func', p[2], [], p[6], p[7])
        else:
            p[0] = ('func', p[2], p[4], None, p[7])
    else:
        p[0] = ('func', p[2], [], None, p[6])


# Helper para inicio de funcion, se llama antes de procesar a los parametros
def np_aux_start_function(func_name):
    semantic_analyzer.np_start_function(func_name, 'void')

# <A> 
def p_param_list(p):
    '''param_list : ID COLON type param_list_prime'''
    # Agregar parametro
    param_name = p[1]
    param_type = p[3]
    
    semantic_analyzer.np_add_parameter(param_name, param_type)
    
    if p[4] is not None and len(p[4]) > 0:
        p[0] = [(p[1], p[3])] + p[4]
    else:
        p[0] = [(p[1], p[3])]


# <A'> 
def p_param_list_prime(p):
    """param_list_prime : COMMA param_list
                        | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = []

# -------------------------------------------------------
# <Program>
def p_program(p):
    """program : PROGRAM ID SEMI_COLON vars func_list MAIN body END
               | PROGRAM ID SEMI_COLON func_list MAIN body END
               | PROGRAM ID SEMI_COLON vars MAIN body END
               | PROGRAM ID SEMI_COLON MAIN body END"""
    
    # Iniciar programa
    program_name = p[2]
    semantic_analyzer.np_start_program(program_name)
    
    if len(p) == 9:
        p[0] = ('program', p[2], p[4], p[5], p[7])
    elif len(p) == 8:
        if p[4] == 'main':
            p[0] = ('program', p[2], None, [], p[5])
        elif isinstance(p[4], tuple) and p[4][0] == 'vars':
            p[0] = ('program', p[2], p[4], [], p[6])
        else:
            p[0] = ('program', p[2], None, p[4], p[6])

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


# -------------------------------------------------------
# <ASSIGN>
def p_assign(p):
    'assign : ID EQUAL expression SEMI_COLON'
    
    var_name = p[1]
    expr_type = expression_types.get(id(p[3]))
    
    # Verificar asignacion
    semantic_analyzer.np_check_assignment(var_name, expr_type)
    
    # Generamos un cuadruplo
    intermediate_code_generator.generate_assignation(var_name=var_name)
    
    p[0] = ('assign', p[1], p[3])


# -------------------------------------------------------
# Manejo de errores
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
    else:
        print("Syntax error: Unexpected end of file (EOF)")


# Crear el parser
parser = yacc.yacc()