from semantic_cube import semantic_cube
from semantic_analyzer import SemanticAnalyzer
from yacc import parser, semantic_analyzer
from lex import lexer

print("PRUEBAS DEL CUBO SEMANTICO\n")

# Pruebas del cubo
print("Test 1: int + int")
print(f"Resultado: {semantic_cube.get_result_type('+', 'int', 'int')}\n")

print("Test 2: int + float")
print(f"Resultado: {semantic_cube.get_result_type('+', 'int', 'float')}\n")

print("Test 3: int / int")
print(f"Resultado: {semantic_cube.get_result_type('/', 'int', 'int')}\n")

print("Test 4: float > int")
print(f"Resultado: {semantic_cube.get_result_type('>', 'float', 'int')}\n")

print("Test 5: Operacion invalida (no existe)")
print(f"Resultado: {semantic_cube.get_result_type('+', 'string', 'int')}\n")

print("\nPRUEBAS DEL ANALIZADOR SEMANTICO\n")

analyzer = SemanticAnalyzer()

print("Test 1: Declarar variable global")
analyzer.np_start_program("test")
analyzer.np_declare_variable('x', 'int', is_global=True)
print()

print("Test 2: Declarar variable duplicada (error esperado)")
analyzer.np_declare_variable('x', 'float', is_global=True)
print()

print("Test 3: Declarar funcion")
analyzer.np_start_function('suma', 'void')
analyzer.np_add_parameter('a', 'int')
analyzer.np_add_parameter('b', 'int')
analyzer.np_end_function('suma')
print()

print("Test 4: Operacion valida")
tipo_resultado = analyzer.np_check_operation('+', 'x', 'y', 'int', 'float')
print(f"Resultado de operacion: {tipo_resultado}\n")

print("Test 5: Asignacion valida")
analyzer.np_check_assignment('x', 'int')
print()

print("\nPRUEBAS INTEGRADAS (PARSER + ANALIZADOR)\n")

test_programa = """program test;
var
    x : int;
    y : float;
main {
    x = 5;
    y = x + 3;
}
end"""

print("Test 1: Programa simple con asignaciones")
semantic_analyzer.reset()
resultado = parser.parse(test_programa, lexer=lexer)
print(f"AST: {resultado}\n")

if semantic_analyzer.has_errors():
    print("Errores encontrados:")
    semantic_analyzer.print_errors()
else:
    print("Sin errores semanticos\n")

test_con_error = """program test2;
var
    x : int;
    x : float;
main {
}
end"""

print("Test 2: Programa con variable duplicada (error esperado)")
semantic_analyzer.reset()
resultado = parser.parse(test_con_error, lexer=lexer)
if semantic_analyzer.has_errors():
    print("Errores esperados:")
    semantic_analyzer.print_errors()
