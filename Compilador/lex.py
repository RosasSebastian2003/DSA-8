import ply.lex as lex

# Se tiene que definir una lista con las palabras reservadas para luego concatenarlas con la lista de tokens 
reserved_namespace = {
    'int' : 'INT',
    'float' : 'FLOAT',
    'var' : 'VAR',
    'program' : 'PROGRAM',
    'void' : 'VOID',
    'if' : 'IF',
    'else' : 'ELSE',
    'while' : 'WHILE',
    'do' : 'DO',
    'print' : 'PRINT',
    'main' : 'MAIN',
    'end' : 'END',
}

# Listar los nombres de los tokens 
tokens = [
    'COMMA',
    'COLON',
    'SEMI_COLON',
    'L_CBRACKET',
    'R_CBRACKET',
    'EQUAL',
    'ID',
    'CNT_INT',
    'CNT_FLOAT',
    'PLUS',
    'MINUS',
    'ASTERISK',
    'FORWARD_SLASH',
    'NOT_EQUAL',
    'GREATER_THAN',
    'LOWER_THAN',
    'L_PARENTHESIS',
    'R_PARENTHESIS',
    'CNT_STRING'
] + list(reserved_namespace.values()) # Concatenamos la lista de palabras reservadas a la lista de tokens

# Expresiones regulares para tokens sencillos, las palabras reservadas se definen por separado mediante un diccionario, r es un literal para raw string 
t_COMMA = r','
t_COLON = r':'
t_SEMI_COLON = r';'

t_L_CBRACKET = r'{'
t_R_CBRACKET = r'}'

t_EQUAL = r'='
t_PLUS = r'\+'
t_MINUS = r'-'
t_ASTERISK = r'\*'
t_FORWARD_SLASH = r'/'
t_NOT_EQUAL = r'!='

t_GREATER_THAN = r'>'
t_LOWER_THAN = r'<'

t_L_PARENTHESIS = r'\('
t_R_PARENTHESIS = r'\)'

#Expresiones regulares mas complejas 
#Como la expresion regular es la primera linea de la funcion, y no esta asignada a nada, Python trata a esta linea como un docstring, PLY lee el docstring utilizando a t_INT.__doc__ y lo usa como expresion regular
def t_CNT_FLOAT(t):
    r'[0-9]+\.[0-9]+(e[-+]?[0-9]+)?'
    t.value = float(t.value)
    return t

def t_CNT_INT(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_CNT_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = str(t.value)
    return t

def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved_namespace.get(t.value, 'ID')  # Verificar si es palabra reservada
    return t

# Otras reglas de gramatica
# Ignorar espacios y tabs
t_ignore = ' \t'

# Regla para contar el numero de lineas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
    
# Regla para manejar errores 
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)
    
# Construir el lexer 
lexer = lex.lex()