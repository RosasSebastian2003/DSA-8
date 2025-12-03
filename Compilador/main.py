import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from intermediate_code_generator import intermediate_code_generator
from excecution_memory import excecution_memory
from yacc import parser, semantic_analyzer
from virtual_machine import virtual_machine

class Compiler:
    def __init__(self):
        self.parser = parser
        self.semantic_analyzer = semantic_analyzer
        self.intermediate_code_generator = intermediate_code_generator
        self.excecution_memory = excecution_memory
        self.virtual_machine = virtual_machine
        self.debug = False
        
    def compile(self, code):
        if self.debug:
            print(f"Compilando...:\n{code}\n")
        # Reset de todos los componentes
        self.intermediate_code_generator.reset()
        self.semantic_analyzer.reset()
        self.excecution_memory.reset()
        
        try:
            result = self.parser.parse(code)
            if self.debug:
                print(f"Resultado del parseo: {result}")
            if result is None:
                print("Error: No se pudo parsear el codigo")
                return False
            
            if self.semantic_analyzer.has_errors():
                print("Errores semanticos encontrados:")
                self.semantic_analyzer.print_errors()
                return False
            
            return True  # Compilación exitosa
            
        except Exception as e:
            print(f"Error durante la compilacion: {e}")
            return False
    
    def print_quads(self):
        self.intermediate_code_generator.print_quads()
        
    def print_function_table(self):
        self.intermediate_code_generator.print_function_table()
    
    def print_memory(self):
        print("\nMemoria: ")
        print("Variables:", self.excecution_memory.var_dict)
        print("Constantes:", self.excecution_memory.const_dict)
        print("\n")
        
    def enable_debug(self):
        self.debug = True
        self.intermediate_code_generator.debug = True
    
    def run(self):
        # Cargar cuádruplos (usar 'quads', no 'quadruples')
        self.virtual_machine.load_quads(self.intermediate_code_generator.quads)
        self.virtual_machine.load_constants(self.excecution_memory.const_dict)
        
        try:
            self.virtual_machine.execute()
        except Exception as e:
            print(f'Error durante la ejecucion: {e}')
            
    def compile_and_run(self, code):
        if self.compile(code):
            if self.debug:
                print("MODO DEBUG")
                self.print_function_table()
                self.print_quads()
                self.print_memory()
                
            self.run()


def main():
    compiler = Compiler()
    
    # Determinar el codigo fuente a usar
    if len(sys.argv) > 1:
        # Leer desde archivo
        file = sys.argv[1]
        
        # Flag de debug
        if "--debug" in sys.argv or "-d" in sys.argv:
            compiler.enable_debug()
        try:
            with open(file, 'r') as f:
                code = f.read()
        except FileNotFoundError:
            print(f"Error: No se encontro el archivo '{file}'")
            return
    else:
        # Programa de ejemplo
        code = """program ejemplo;
        var
            x, y : int;
        main {
            x = 5;
            y = 10;
            print("Suma:", x + y);
        }
        end"""
        print("Usando programa de ejemplo")
        
    # Compilar
    compiler.compile_and_run(code=code)


if __name__ == "__main__":
    main()