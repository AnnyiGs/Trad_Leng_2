import re
from collections import namedtuple

# Definición de un token como una tupla con tipo, valor, línea y columna
Token = namedtuple('Token', ['type', 'value', 'line', 'column'])

# Excepción personalizada para errores léxicos
class LexerError(Exception):
    pass

class Lexer:
    def __init__(self):
        # Texto a analizar
        self.text = ''
        self.pos = 0  # Posición actual en el texto
        self.line = 1  # Línea actual
        self.column = 1  # Columna actual

        # Especificación de tokens mediante expresiones regulares
        self.token_specification = [
            ('NUMBER',   r'\d+(\.\d+)?'),       # Números enteros o flotantes
            ('ID',       r'[A-Za-z_]\w*'),      # Identificadores
            ('ASSIGN',   r'='),                 # Operador de asignación
            ('SEMI',     r';'),                 # Punto y coma
            ('LPAREN',   r'\('),                # Paréntesis izquierdo
            ('RPAREN',   r'\)'),                # Paréntesis derecho
            ('LBRACE',   r'\{'),                # Llave izquierda
            ('RBRACE',   r'\}'),                # Llave derecha
            ('COLON',    r':'),                 # Dos puntos
            ('COMMA',    r','),                 # Coma
            ('OP',       r'[+\-*/]'),           # Operadores aritméticos
            ('NEWLINE',  r'\n'),                # Nueva línea
            ('SKIP',     r'[ \t]+'),            # Espacios y tabulaciones
            ('STRING',   r'"[^"\n]*"'),         # Cadenas entre comillas
            ('MISMATCH', r'.'),                 # Cualquier otro carácter no válido
        ]

        # Palabras reservadas del lenguaje
        self.keywords = {
            'var': 'VAR',
            'int': 'INT',
            'float': 'FLOAT',
            'string': 'STRING',
            'print': 'PRINT',
            'return': 'RETURN',
            'program': 'PROGRAM',
        }

        # Compilación de las expresiones regulares para mejorar el rendimiento
        self.regex = re.compile('|'.join(
            f'(?P<{name}>{pattern})' for name, pattern in self.token_specification
        ))

    # Método principal para tokenizar el texto
    def tokenize(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.column = 1

        # Iterar sobre el texto para identificar tokens
        while self.pos < len(self.text):
            match = self.regex.match(self.text, self.pos)
            if not match:
                raise LexerError(f"Carácter inesperado '{self.text[self.pos]}' en línea {self.line}, columna {self.column}")

            # Obtener el tipo de token y el valor
            token_type = match.lastgroup
            token_value = match.group(token_type)

            if token_type == 'NEWLINE':
                # Manejar nueva línea
                self.line += 1
                self.column = 1
            elif token_type == 'SKIP':
                # Ignorar espacios y tabulaciones
                pass
            elif token_type == 'MISMATCH':
                # Manejar caracteres no válidos
                raise LexerError(f"Carácter inesperado '{token_value}' en línea {self.line}, columna {self.column}")
            else:
                # Identificar palabras reservadas o devolver el token
                if token_type == 'ID' and token_value in self.keywords:
                    token_type = self.keywords[token_value]
                yield Token(token_type, token_value, self.line, self.column)

            # Actualizar posición y columna
            self.pos = match.end()
            self.column += len(token_value)