import ply.yacc as yacc
from lex import tokens

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
    '''var_list_prime: var_list
                     | empty'''
    if len(p) == 2 and p[1] is not None:
        p[0] = p[1]
    else:
        p[0] = []
    
# <A>
def p_id_list(p):
    'id_list: ID id_list_prime'
    p[0] = [p[1]] = p[2]

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

# <ASSIGN>
def p_assign(p):
    'assign : id EQUAL expression SEMI_COLON'
    p[0] = ('assign', p[1], p[3])

# -------------------------------------------------------

# Manejo de errores 
def p_error(p): 
    if p: 
        print(f"Syntax error at token {p.type} ('{p.value}') on line {p.lineo}")
    else: 
        print("SYNTAX ERROR")