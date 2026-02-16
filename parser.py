from collections import namedtuple

# Excepción personalizada para errores sintácticos
class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token

# Clase principal del analizador sintáctico
class Parser:
    # Nombres amigables para los tokens, usados en mensajes de error
    friendly_names = {
        'ID': 'identificador',
        'OP': 'operador',
        'SEMI': 'punto y coma',
        'LPAREN': 'paréntesis izquierdo "("',
        'RPAREN': 'paréntesis derecho ")"',
        'LBRACE': 'llave izquierda "{"',
        'RBRACE': 'llave derecha "}"',
        'COMMA': 'coma ","',
        'COLON': 'dos puntos ":"',
        'ASSIGN': 'signo de asignación "="',
        'PROGRAM': 'palabra reservada "program"',
        'VAR': 'palabra reservada "var"',
        'INT': 'tipo entero',
        'FLOAT': 'tipo flotante',
        'STRING': 'tipo cadena',
        'PRINT': 'palabra reservada "print"',
        'RETURN': 'palabra reservada "return"',
        'EOF': 'fin de archivo',
    }

    def __init__(self, tokens):
        self.tokens = tokens  # Lista de tokens generados por el analizador léxico
        self.pos = 0  # Posición actual en la lista de tokens
        self.current_token = self.tokens[self.pos]  # Token actual
        self.errors = []  # Lista de errores encontrados durante el análisis

    # Método para obtener un nombre amigable para un tipo de token
    def friendly(self, token_type):
        return self.friendly_names.get(token_type, token_type.lower())

    # Avanzar al siguiente token
    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            # Crear un token EOF ficticio al final
            self.current_token = namedtuple('Token', ['type','value','line','column'])(
                'EOF', '', self.current_token.line, self.current_token.column
            )

    # Verificar que el token actual sea del tipo esperado
    def expect(self, expected_type):
        if self.current_token.type == expected_type:
            self.advance()
        else:
            exp_friendly = self.friendly(expected_type)
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {exp_friendly} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # Método principal para iniciar el análisis sintáctico
    def parse(self):
        try:
            if self.current_token.type == 'PROGRAM':
                self.program_block()
            else:
                self.program_c_style()
        except ParserError:
            pass

        # Print errors if any
        if self.errors:
            print("[PARSER] Se encontraron errores sintácticos:")
            for e in self.errors:
                print(f"  - {e}")
        else:
            print("✅ El archivo es válido.")

    # Analizar un programa con la estructura "program { ... }"
    def program_block(self):
        self.expect('PROGRAM')
        self.expect('ID')
        self.expect('LBRACE')
        self.statements()
        self.expect('RBRACE')
        self.expect('EOF')

    # Analizar un programa con estilo C
    def program_c_style(self):
        while self.current_token.type != 'EOF':
            try:
                self.function_or_declaration()
            except ParserError as e:
                self.errors.append(str(e))
                self.advance()  # Evitar bucles infinitos en caso de error

    # Analizar una declaración de función o una declaración de variable
    def function_or_declaration(self):
        if self.current_token.type in ('INT', 'FLOAT', 'STRING'):
            next_token = self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None
            if next_token and next_token.type == 'ID':
                next_next = self.tokens[self.pos + 2] if self.pos + 2 < len(self.tokens) else None
                if next_next and next_next.type == 'LPAREN':
                    self.function_declaration()
                else:
                    self.variable_declaration()
            else:
                self.variable_declaration()
        else:
            raise ParserError("Se esperaba declaración o función", self.current_token)

    # Analizar una declaración de variable
    def variable_declaration(self):
        self.advance()  # Tipo de la variable
        self.expect('ID')
        self.expect('SEMI')

    # Analizar una declaración de función
    def function_declaration(self):
        self.advance()  # Tipo de retorno
        self.expect('ID')
        self.expect('LPAREN')
        self.parameter_list()
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.statements()
        self.expect('RBRACE')

    # Analizar una lista de parámetros
    def parameter_list(self):
        if self.current_token.type in ('INT', 'FLOAT', 'STRING'):
            self.advance()
            self.expect('ID')
            while self.current_token.type == 'COMMA':
                self.advance()
                self.advance()
                self.expect('ID')

    # Analizar una lista de sentencias
    def statements(self):
        while self.current_token.type not in ('RBRACE', 'EOF'):
            try:
                self.statement()
            except ParserError as e:
                self.errors.append(str(e))
                self.advance()

    # Analizar una sentencia individual
    def statement(self):
        if self.current_token.type == 'VAR':
            self.variable_declaration()
        elif self.current_token.type in ('INT', 'FLOAT', 'STRING'):
            self.variable_declaration()
        elif self.current_token.type == 'ID':
            self.assignment_or_function_call()
        elif self.current_token.type == 'PRINT':
            self.print_statement()
        elif self.current_token.type == 'RETURN':
            self.return_statement()
        else:
            expected = "declaración o instrucción"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # Analizar una asignación o llamada a función
    def assignment_or_function_call(self):
        self.advance()  # ID
        if self.current_token.type == 'ASSIGN':
            self.advance()
            self.expression()
            self.expect('SEMI')
        elif self.current_token.type == 'LPAREN':
            self.function_call()
            self.expect('SEMI')
        else:
            expected = "signo '=' o '('"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} después de identificador pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # Analizar una llamada a función
    def function_call(self):
        self.expect('LPAREN')
        self.argument_list()
        self.expect('RPAREN')

    # Analizar una lista de argumentos
    def argument_list(self):
        if self.current_token.type not in ('RPAREN',):
            self.expression()
            while self.current_token.type == 'COMMA':
                self.advance()
                self.expression()

    # Analizar una expresión
    def expression(self):
        self.term()
        while self.current_token.type == 'OP' and self.current_token.value in ('+', '-'):
            self.advance()
            self.term()

    # Analizar un término
    def term(self):
        self.factor()
        while self.current_token.type == 'OP' and self.current_token.value in ('*', '/'):
            self.advance()
            self.factor()

    # Analizar un factor
    def factor(self):
        if self.current_token.type == 'ID':
            self.advance()
            if self.current_token.type == 'LPAREN':
                self.function_call()
        elif self.current_token.type in ('NUMBER', 'STRING'):
            self.advance()
        elif self.current_token.type == 'LPAREN':
            self.advance()
            self.expression()
            self.expect('RPAREN')
        else:
            expected = "expresión"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)
