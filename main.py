import sys
from lexer import Lexer, LexerError
from parser import Parser

def main():
    print("Selecciona una opción:")
    print("1. Ingresar la ruta de un archivo para analizar.")
    print("2. Ingresar el código directamente en la consola.")

    opcion = input("Opción (1/2): ")

    if opcion == "1":
        ruta = input("Por favor, ingresa la ruta del archivo a analizar: ")
        try:
            with open(ruta, 'r', encoding='utf-8') as f:
                codigo = f.read()
        except FileNotFoundError:
            print(f"❌ No se encontró el archivo: {ruta}")
            print("Verifica que la ruta sea correcta y que el archivo exista.")
            return
    elif opcion == "2":
        print("Ingresa el código a analizar. Finaliza con una línea vacía:")
        lineas = []
        while True:
            linea = input()
            if linea == "":
                break
            lineas.append(linea)
        codigo = "\n".join(lineas)
    else:
        print("❌ Opción no válida.")
        return

    print("\n--- Proceso de análisis iniciado ---")

    # ---------------- Lexer ----------------
    lexer = Lexer()
    print("[LEXER] Iniciando tokenización...")
    try:
        tokens = list(lexer.tokenize(codigo))
        print("[LEXER] Tokenización completada con éxito.")
        print("[LEXER] Tokens generados:")
        for token in tokens:
            print(f"  {token}")
    except LexerError as e:
        print(f"[ERROR LÉXICO]: {e}")
        return

    # ---------------- Parser ----------------
    parser = Parser(tokens)
    print("[PARSER] Iniciando análisis sintáctico...")
    parser.parse()

    # ---------------- Resultados ----------------
    if parser.errors:
        print("[PARSER] Se encontraron errores sintácticos:")
        for e in parser.errors:
            print(f"  - {e}")
        print("❌ El archivo no es válido.")
    else:
        print("✅ El archivo es válido.")

    print("--- Proceso de análisis finalizado ---")

if __name__ == "__main__":
    main()
