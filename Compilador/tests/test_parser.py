import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from intermediate_code_generator import intermediate_code_generator
from yacc import parser

print("ANÁLISIS SINTÁCTICO\n")

program_w_vars = """program test1;
var
    x : int;
    y, z : float;
main {
}
end"""

print("Test 1: Programa con variables")
print(parser.parse(program_w_vars))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_ids = """program test2;
var
    x : int;
main {
    x = 5;
}
end"""

print("Test 2: Programa con asignaciones")
print(parser.parse(parser_w_ids))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_expressions = """program test3;
var
    x, y, z : int;
main {
    x = 5 + 3;
    y = x * 2;
    z = (x + y) / 2;
}
end"""

print("Test 3: Programa con expresiones aritméticas")
print(parser.parse(parser_w_expressions))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_if = """program test4;
var
    x : int;
main {
    x = 10;
    if (x > 5) {
        x = x + 1;
    };
}
end"""

print("Test 4: Programa con if")
print(parser.parse(parser_w_if))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_if_else = """program test5;
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
end"""

print("Test 5: Programa con if-else")
print(parser.parse(parser_w_if_else))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_loop = """program test6;
var
    x : int;
main {
    x = 0;
    while (x < 10) do {
        x = x + 1;
    };
}
end"""

print("Test 6: Programa con while")
print(parser.parse(parser_w_loop))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_print = """program test7;
var
    x : int;
main {
    x = 42;
    print(x);
}
end"""

print("Test 7: Programa con print")
print(parser.parse(parser_w_print))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

parser_w_func = """program test8;
void myFunc(a : int, b : int) [
    var
        result : int;
    {
        result = a + b;
    }
];
main {
}
end"""

print("Test 8: Programa con función")
print(parser.parse(parser_w_func))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()

full_program = """program completo;
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
end"""

print("Test 9: Programa completo")
print(parser.parse(full_program))
print("\n Cuadruplos generados")
intermediate_code_generator.print_quads()
intermediate_code_generator.reset()
print()


print("PRUEBAS DE ERRORES SINTÁCTICOS")
print()

error1 = """program test1
var
    x : int;
main {
}
end"""

print("Error 1: Falta punto y coma después de program")
print(parser.parse(error1))
print()

error2 = """program test2;
var
    x int;
main {
}
end"""

print("Error 2: Falta dos puntos en declaración de variable")
print(parser.parse(error2))
print()

error3 = """program test3;
var
    x : int;
main {
    x = 5
}
end"""

print("Error 3: Falta punto y coma en asignación")
print(parser.parse(error3))
print()

error4 = """program test4;
var
    x : int;
main {
    if (x > 5 {
        x = 10;
    };
}
end"""

print("Error 4: Paréntesis sin cerrar en if")
print(parser.parse(error4))
print()

error5 = """program test5;
main {
    x = 5;
}"""

print("Error 5: Falta palabra clave 'end'")
print(parser.parse(error5))
