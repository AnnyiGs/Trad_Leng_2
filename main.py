import sys
from lexer import Lexer, LexerError
from parser import Parser

def main():
    if len(sys.argv) < 2:
        print("❌ Debes indicar la ruta del archivo como argumento.")
        print("Ejemplo: python main.py samples/valid/correct.src")
        return

    ruta = sys.argv[1]

    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            codigo = f.read()
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo: {ruta}")
        return

    # ---------------- Lexer ----------------
    lexer = Lexer()
    try:
        tokens = list(lexer.tokenize(codigo))
    except LexerError as e:
        print(f"[ERROR LÉXICO]: {e}")
        return

    # ---------------- Parser ----------------
    parser = Parser(tokens)
    parser.parse()

    # ---------------- Resultados ----------------
    if parser.errors:
        print("[ERRORES ENCONTRADOS]:")
        for e in parser.errors:
            print("-", e)
    else:
        print("✅ Código válido")

if __name__ == "__main__":
    main()
