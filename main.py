import sys
from lexer import Lexer, LexerError
from parser import Parser

def main():
    print("\n\nSelecciona una opción:")
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
        print("\nIngresa el código a analizar. Finaliza con una línea vacía:")
        lineas = []
        while True:
            linea = input()
            if linea == "":
                break
            lineas.append(linea)
        codigo = "\n".join(lineas)
    else:
        print("\n❌ Opción no válida.")
        return

    print("\n--- Proceso de análisis iniciado ---")

    # ---------------- Lexer ----------------
    lexer = Lexer()
    print("\n[LEXER] Iniciando tokenización...")
    try:
        tokens = list(lexer.tokenize(codigo))
        print("\n[LEXER] Tokenización completada con éxito.")
        print("\n[LEXER] Tokens generados:")
        for token in tokens:
            print(f"  {token}")
    except LexerError as e:
        print(f"\n[ERROR LÉXICO]: {e}")
        return

    # ---------------- Parser ----------------
    print("\n\n[DEBUG] Tokens pasados al analizador sintáctico:")
    for token in tokens:
        print(f"  {token}")

    parser = Parser(tokens)
    print("\n[PARSER] Iniciando análisis sintáctico...")
    parser.parse()

    # ---------------- Resultados ----------------
    if parser.errors:
        print("\n[PARSER] Se encontraron errores sintácticos:")
        for e in parser.errors:
            print(f"  - {e}")
        print("\n❌ El archivo no es válido.")
    else:
        print("\n✅ El archivo es válido.")

    print("\n--- Proceso de análisis finalizado ---\n")

if __name__ == "__main__":
    main()
