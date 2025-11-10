from lex import lexer

test_code = """
program test;
var x, y : int;
var z : float;

main {
    x = 10;
    y = 20;
    z = 3.14;

    if (x != y) {
        print("Los numeros son diferentes");
    } else {
        print("Los numeros son iguales");
    }

    while (x > 0) {
        x = x - 1;
    }
}
end
"""

lexer.input(test_code)

print("ANÁLISIS LÉXICO")

for tok in lexer:
    print(f"Token: {tok.type:15} | Valor: {tok.value:20} | Línea: {tok.lineno}")

