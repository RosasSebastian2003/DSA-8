# Tarea #3

### Scanner y Parser con PLY
---

## 1. Selección de Herramienta de Generación Automática

### Análisis de Herramientas Evaluadas

Anteriormente, investigue tres herramientas para elaborar compiladores, para ello, considere las siguientes 3 herramientas:

#### Flex y Bison
Flex genera escáneres léxicos basados en autómatas finitos deterministas, y Bison crea analizadores de sintaxis a partir de gramáticas libres de contexto 
- Conocimiento de C para el código de acciones
- Compilación separada de archivos intermedios
- Manejo de archivos `.l` y `.y` con sintaxis específica
- Proceso de compilación adicional con herramientas de C

Aunque son muy poderosas y eficientes, su integración con Python (el lenguaje seleccionado para este proyecto) requeriría bindings adicionales o comunicación entre procesos, lo cual añade complejidad innecesaria.

### Flex y Bison

Flex y Bison son las herramientas más para en el desarrollo de compiladores. Flex genera escáneres léxicos basados en autómatas finitos deterministas, y Bison crea analizadores de sintaxis a partir de gramáticas libres de contexto. 

Se requiere de conocimiento en C para el la definicion de las acciones de los puntos neuralgicos, compilación separada de archivos intermedios, manejo de archivos con extensión .l y .y, y un proceso de compilación adicional utilizando herramientas de C. 

### Lrparsing

Lrparsing ofrece un enfoque más moderno, us expresiones de Python para definir gramáticas. Esta herramienta proporciona un parser LR con tokenizador integrado, pre-compilación de gramática para optimizar el rendimiento, y mecanismos de recuperación de errores que permiten continuar el parseo incluso cuando se detectan problemas.

### PLY (Python Lex-Yacc) 

PLY es una implementación completamente desarrollada en Python sin dependencias externas, lo que facilita su instalación y uso. Usa la sintaxis y filosofía de Lex/Yacc, usa parseo LALR (Look-Ahead LR), tiene validación automática de entrada con reportes de errores , y no requiere archivos de entrada especiales ni compilación separada como Flex/Bison, implementa  cache de tablas de parseo que solo regenera las tablas cuando detecta cambios en la gramática, lo que optimiza el ciclo de desarrollo.

Decidi utilizar a PLY debido a que cuenta con bastante documentacion y cuenta con muchos ejemplos que facilitan la comprehencion de el proceso de elaboracion del parser.

---

## Estructura del Compilador

### lex.py - Analizador Léxico
Contiene la definición de tokens y expresiones regulares para el lenguaje.

Dentro de lex se define a la lista de tokens y a las expresiones del lenguaje, donde para PLY, se definen primero a las palabras reservadas en formato de un diccionario, donde la llave es palabra escrita de la manera en la que sera reconocida en el codigo, y el valor sera nombre del token que esperariamos. Luego creamos el arreglo de tokens que esperaremos, y le concatenamos a los valores de el diccionario de palabras reservadas, despues de esto procedemos a definir las expresiones regulares para cada token, donde primero definimos a las expresiones regulares de los caracteres individuales como variables, luego definimos a las expresiones regulares mas complicadas, como CNT_FLOAT, CNT_INT, ID, y CNT_STRING, espues inclui una regla gramaticar para ignorar espacios y tabs para que el programa no se detenga cuando detecte saltos de linea, lugo defini una regla que me de un conteo de lineas, y una regla para definir el manejo de errores del lexer, donde recibo e imprimo el error y luego salto al siguiente token.

#### `yacc.py` - Analizador Sintáctico
Implementa las reglas gramaticales y construye el Árbol de Sintaxis Abstracta (AST).

Primero defino el simbolo de inicio, este sera la gramatica que empiece el programa, luego defino las producciones de la gramatica, esto lo logro mediante escribir a las gramaticas libres de contexto en forma de docstrings que yacc usa para la formacion de las tablas y definir a p[0] (indice del resultado) como el indice que representa al valor semantico que queremos que represente ese simbolo en el arbol de parseo. Luego agrego una regla para el manejo de errores.

#### Pruebas
Contiene casos de prueba exhaustivos para validar el funcionamiento del compilador, donde test_lexer.py contiene las pruebas del lexer y test_parse.py contiene las pruebas del parser, el cual emplea al lexer.

---

## Definición de Expresiones Regulares

### Palabras Reservadas

Defini a las palabras reservadas mediante un diccionario que mapea el texto de la palabra a su tipo de token:

```python
reserved_namespace = {
    'int'     : 'INT',
    'float'   : 'FLOAT',
    'var'     : 'VAR',
    'program' : 'PROGRAM',
    'void'    : 'VOID',
    'if'      : 'IF',
    'else'    : 'ELSE',
    'while'   : 'WHILE',
    'do'      : 'DO',
    'print'   : 'PRINT',
    'main'    : 'MAIN',
    'end'     : 'END',
}
```

### Tokens Simples

Los operadores y delimitadores se definen mediante expresiones regulares sencillas que se asignan a variables:

| Token | Expresión Regular | Descripción |
|-------|------------------|-------------|
| `COMMA` | `,` | Coma |
| `COLON` | `:` | Dos puntos |
| `SEMI_COLON` | `;` | Punto y coma |
| `L_CBRACKET` | `\{` | Llave izquierda |
| `R_CBRACKET` | `\}` | Llave derecha |
| `L_SBRACKET` | `\[` | Corchete izquierdo |
| `R_SBRACKET` | `\]` | Corchete derecho |
| `L_PARENTHESIS` | `\(` | Paréntesis izquierdo |
| `R_PARENTHESIS` | `\)` | Paréntesis derecho |
| `EQUAL` | `=` | Igual |
| `PLUS` | `\+` | Suma |
| `MINUS` | `-` | Resta |
| `ASTERISK` | `\*` | Multiplicación |
| `FORWARD_SLASH` | `/` | División |
| `NOT_EQUAL` | `!=` | Diferente de |
| `GREATER_THAN` | `>` | Mayor que |
| `LOWER_THAN` | `<` | Menor que |

### Tokens Complejos

Los tokens con patrones complejos se definen mediante funciones:

#### CNT_FLOAT
```python
def t_CNT_FLOAT(t):
    r'\d+\.\d+(e[+-]?\d+)?'
    t.value = float(t.value)
    return t
```

**Patrón:** Uno o más dígitos, seguido de punto decimal, uno o más dígitos, opcionalmente seguido de notación científica (e/E seguido de signo opcional y dígitos).

**Ejemplos válidos:** `3.14`, `2.5e10`, `1.0e-5`

#### CNT_INT
```python
def t_CNT_INT(t):
    r'\d+'
    t.value = int(t.value)
    return t
```
**Patrón:** Uno o más dígitos.

**Ejemplos válidos:** `0`, `42`, `1000`

#### CNT_STRING
```python
def t_CNT_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]  # Remover comillas
    return t
```
**Patrón:** Comillas dobles, seguidas de cualquier carácter excepto comillas o backslash (o secuencias de escape), terminando en comillas dobles.

**Ejemplos válidos:** `"hola"`, `"valor: 10"`, `"con \"escape\""`

#### ID
```python
def t_ID(t):
    r'[a-zA-Z_]\w*'
    t.type = reserved_namespace.get(t.value, 'ID')
    return t
```
**Patrón:** Letra o guión bajo, seguido de cero o más caracteres alfanuméricos o guiones bajos.

**Ejemplos válidos:** `x`, `variable1`, `_temp`, `miVariable`

### Manejo de Espacios y Comentarios

```python
# Ignorar espacios y tabs
t_ignore = ' \t'

# Contar líneas
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)
```

**Importante:** PLY evalúa las reglas revizando primero a las funciones definidas antes que otras funciones, luego a las expresiones regulares mas largas antes que a las cortas, y luego al orden de definicion en el codigo.
poreso, t_CNT_FLOAT debe definirse antes que t_CNT_INT, ya que 3.14 podría ser interpretado incorrectamente como 3, . , 14 y daria un error por el punto.

---

## Reglas Gramaticales

### Estructura del Programa
Primero se define a la gramatica que empieza al programa, esta es program

### Implementación
```python
def p_program(p):
    """program : PROGRAM ID SEMI_COLON vars func_list MAIN body END
               | PROGRAM ID SEMI_COLON func_list MAIN body END
               | PROGRAM ID SEMI_COLON vars MAIN body END
               | PROGRAM ID SEMI_COLON MAIN body END"""
    
    if len(p) == 9:
        p[0] = ('program', p[2], p[4], p[5], p[7])
    elif len(p) == 8:
        if isinstance(p[4], tuple) and p[4][0] == 'vars':
            p[0] = ('program', p[2], p[4], [], p[6])
        elif isinstance(p[4], list):
            p[0] = ('program', p[2], None, p[4], p[6])
        else:
            p[0] = ('program', p[2], None, [], p[5])
    else:
        p[0] = ('program', p[2], None, [], p[5])
```

### Variables

```
<VARS> → var <var_list>
<var_list> → <id_list> : <type> ; <var_list'>
<var_list'> → <var_list> | ε
<id_list> → id <id_list'>
<id_list'> → , <id_list> | ε
<type> → int | float
```

Permite declarar multiples variables del mismo tipo y declaraciones consecuticas.

### Expresiones Aritméticas

```
<EXP> → <EXP> + <TERMINO>
      | <EXP> - <TERMINO>
      | <TERMINO>

<TERMINO> → <TERMINO> * <FACTOR>
          | <TERMINO> / <FACTOR>
          | <FACTOR>

<FACTOR> → ( <EXPRESION> )
         | + id | + <CTE>
         | - id | - <CTE>
         | id
         | <CTE>

<CTE> → cte_int | cte_float
```

### Precedencia de operadores
1. `+`, `-` (suma, resta)
2. `*`, `/` (multiplicación, división)
3. Operadores unarios `+`, `-`
4. Paréntesis `( )`

### Expresiones

```
<EXPRESION> → <EXP> <EXPRESION'>
<EXPRESION'> → > <EXP>
             | < <EXP>
             | != <EXP>
             | ε
```

### Condiciones y ciclos

#### Condicional
```
<CONDITION> → if ( <EXPRESION> ) <Body> ;
            | if ( <EXPRESION> ) <Body> else <Body> ;
```

#### Ciclo 
```
<CYCLE> → while ( <EXPRESION> ) do <Body> ;
```

### Funciones

```
<FUNCS> → void id ( <param_list> ) [ [<VARS>] <Body> ] ; <func_list'>
<func_list'> → <FUNCS> | ε

<param_list> → id : <type> <param_list'>
<param_list'> → , <param_list> | ε
```
Se permiten definiciones de variables locales

### Statements

```
<Body> → { <statement_list> }
       | { }

<statement_list> → <statement> <statement_list'>
<statement_list'> → <statement_list> | ε

<statement> → <assign>
            | <condition>
            | <cycle>
            | <f_call>
            | <print_stmt>

<assign> → id = <EXPRESION> ;

<f_call> → id ( [<expression_list>] ) ;

<print_stmt> → print ( <print_expression_list> ) ;
<print_expression_list> → (<expression> | cte_string) <print_list'>
<print_list'> → , <print_expression_list> | ε
```

---

## Plan de Pruebas y Casos de Prueba

### Analisis Lexivo

Se creo un archivo de python donde se incluyo un string y un print que arroja a los tokens detectados, la linea donde se encontro y su valor, corrio de manera exitosa y sin errores, todos los tokens fueron detectadis correctamente.

### Casos de Prueba del Análisis Sintáctico

#### Test 1: Programa Mínimo
Se debe de verificar la estructura básica de un programa.

**Entrada:**
```
program test1;
main {
}
end
```

**AST Esperado:**
```python
('program', 'test1', None, [], ('body', []))
```

#### Test 2: Programa con Variables
Se debe de validar declaración de variables globales.

**Entrada:**
```
program test2;
var
    x : int;
    y, z : float;
main {
}
end
```

**AST Esperado:**
```python
('program', 'test2',
  ('vars', [
    ('var_declaration', ['x'], 'int'),
    ('var_declaration', ['y', 'z'], 'float')
  ]),
  [],
  ('body', [])
)
```

#### Test 3: Expresiones Aritméticas
Se debe de verificar precedencia y asociatividad de operadores.

**Entrada:**
```
program test3;
var
    x, y, z : int;
main {
    x = 5 + 3;
    y = x * 2;
    z = (x + y) / 2;
}
end
```

**AST Esperado (fragmento de `z`):**
```python
('assign', 'z',
  ('/', ('+', 'x', 'y'), 2)
)
```

#### Test 4: Condicional If Simple
Se debe de validar estructura if sin else.

**Entrada:**
```
program test4;
var
    x : int;
main {
    x = 10;
    if (x > 5) {
        x = x + 1;
    };
}
end
```

**AST Esperado:**
```python
('if',
  ('>', 'x', 5),           # condición
  ('body', [               # then
    ('assign', 'x', ('+', 'x', 1))
  ]),
  None                     # sin else
)
```

#### Test 5: Condicional If-Else
Se debe de validar estructura if-else completa.

**Entrada:**
```
program test5;
var
    x : int;
main {
    x = 3;
    if (x > 5) {
        x = 10;
    } else {
        x = 0;
    };
}
end
```

#### Test 6: Ciclo While
Se debe de verificar estructura de ciclos.

**Entrada:**
```
program test6;
var
    x : int;
main {
    x = 0;
    while (x < 10) do {
        x = x + 1;
    };
}
end
```

**AST Esperado:**
```python
('while',
  ('<', 'x', 10),          # condición
  ('body', [               # cuerpo del ciclo
    ('assign', 'x', ('+', 'x', 1))
  ])
)
```

#### Test 7: Función Print
Se debe de validar impresión de expresiones y strings.

**Entrada:**
```
program test7;
var
    x : int;
main {
    x = 42;
    print(x);
    print("El valor es:", x);
}
end
```

**AST Esperado:**
```python
('print', ['x'])
('print', ['El valor es:', 'x'])
```

#### Test 8: Declaración de Funciones
Se debe de verificar sintaxis de funciones con parámetros y variables locales.

**Entrada:**
```
program test8;
void myFunc(a : int, b : int) [
    var
        result : int;
    {
        result = a + b;
    }
];
main {
}
end
```

**AST Esperado:**
```python
('func', 'myFunc',
  [('a', 'int'), ('b', 'int')],  # parámetros
  ('vars', [                      # variables locales
    ('var_declaration', ['result'], 'int')
  ]),
  ('body', [                      # cuerpo
    ('assign', 'result', ('+', 'a', 'b'))
  ])
)
```

#### Test 9: Programa Completo
Se debe de validar integración de todas las características del lenguaje.

**Entrada:**
```
program completo;
var
    x, y : int;
    z : float;

void calcular(a : int, b : int) [
    var
        resultado : int;
    {
        resultado = a + b;
    }
];

main {
    x = 10;
    y = 20;
    z = 3.14;

    if (x < y) {
        print("x es menor que y");
    } else {
        print("x es mayor o igual que y");
    };

    while (x < 100) do {
        x = x + 1;
    };

    calcular(x, y);
}
end
```

### Casos de Prueba de Errores Sintácticos

#### Error 1: Falta Punto y Coma
**Entrada:**
```
program test1
var
    x : int;
main {
}
end
```

**Salida:**
```
Syntax error at token VAR ('var') on line 2
```

#### Error 2: Falta Dos Puntos en Declaración
**Entrada:**
```
program test2;
var
    x int;
main {
}
end
```

**Salida:**
```
Syntax error at token INT ('int') on line 3
```

#### Error 3: Falta Punto y Coma en Asignación
**Entrada:**
```
program test3;
var
    x : int;
main {
    x = 5
}
end
```

**Salida:**
```
Syntax error at token R_CBRACKET ('}') on line 6
```

#### Error 4: Paréntesis Sin Cerrar
**Entrada:**
```
program test4;
var
    x : int;
main {
    if (x > 5 {
        x = 10;
    };
}
end
```

**Salida:**
```
Syntax error at token L_CBRACKET ('{') on line 5
```

#### Error 5: Falta Palabra Clave 'end'
**Entrada:**
```
program test5;
main {
    x = 5;
}
```

**Salida:**
```
Syntax error: Unexpected end of file (EOF)
```