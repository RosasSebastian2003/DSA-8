import ply.yacc as yacc
from lex import tokens

# Simbolo de inicio
start = 'program'

# <VARS>
# Las expresiones factorizadas se deben de separar en forma de otras funciones

def p_vars(p):
    'vars : VAR var_list'
    p[0] = ('vars', p[2])
    
# <B>
def p_var_list(p):
    'var_list : id_list COLON type SEMI_COLON var_list_prime'
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
# Cambie mi enfoque de factorizacion a recursion izquierda debido a que el desarrollo del enfoque de factorizacion era mas complicado que el de recursion izquierda
def p_exp(p):
    '''exp : exp PLUS termino
           | exp MINUS termino
           | termino'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3]) # Construccion del AST
    else:
        p[0] = p[1]
        
# -------------------------------------------------------

# <TERMINO>
# Cambie mi enfoque de factorizacion a recursion izquierda debido a que el desarrollo del enfoque de factorizacion era mas complicado que el de recursion izquierda
def p_termino(p):
    '''termino : termino ASTERISK factor
               | termino FORWARD_SLASH factor
               | factor'''
    if len(p) == 4:
        p[0] = (p[2], p[1], p[3]) # Construccion del AST
    else:
        p[0] = p[1]

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

# -------------------------------------------------------

# <EXPRESSION>
def p_expression(p):
    'expression : exp expression_prime'
    if p[2] is not None:
        p[0] = (p[2][0], p[1], p[2][1])  
    else:
        p[0] = p[1]

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
        # Body con statements: { ... }
        p[0] = ('body', p[2])

# <A> (statement_list) → STATEMENT A'
def p_statement_list(p):
    '''statement_list : statement statement_list_prime'''
    if p[2] is not None and len(p[2]) > 0:
        p[0] = [p[1]] + p[2]
    else:
        p[0] = [p[1]]

# <A'> (statement_list_prime) → ε | A
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
        # if sin else
        # p[1] = IF
        # p[2] = (
        # p[3] = expression
        # p[4] = )
        # p[5] = body
        # p[6] = ;
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
        p[0] = p[2]
    
    elif len(p) == 3:
        if p[1] == '+':
            p[0] = p[2]
        else: 
            p[0] = ('unary_minus', p[2])
    else: 
        p[0] = p[1]
        
# -------------------------------------------------------
# <FUNCS>
def p_funcs(p):
    """funcs : VOID ID L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET vars body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS param_list R_PARENTHESIS L_SBRACKET body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS R_PARENTHESIS L_SBRACKET vars body R_SBRACKET SEMI_COLON
             | VOID ID L_PARENTHESIS R_PARENTHESIS L_SBRACKET body R_SBRACKET SEMI_COLON"""
    
    if len(p) == 11:
        p[0] = ('func', p[2], p[4], p[7], p[8])
    elif len(p) == 10:
        if p[4] == ')':
            p[0] = ('func', p[2], [], p[6], p[7])
        else:
            p[0] = ('func', p[2], p[4], None, p[7])
        p[0] = ('func', p[2], [], None, p[6])

# <A> 
def p_param_list(p):
    '''param_list : ID COLON type param_list_prime'''
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
        # Recursión: más funciones
        p[0] = p[1]
    else:
        # Epsilon: fin de la lista
        p[0] = []

# -------------------------------------------------------
# <ASSIGN>
def p_assign(p):
    'assign : ID EQUAL expression SEMI_COLON'
    p[0] = ('assign', p[1], p[3])

# -------------------------------------------------------
# Manejo de errores
def p_error(p):
    if p:
        print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineno}")
    else:
        print("Syntax error: Unexpected end of file (EOF)")

parser = yacc.yacc()