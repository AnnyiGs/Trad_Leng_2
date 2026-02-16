from collections import namedtuple

# Excepción personalizada para errores sintácticos
class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token

# Clase para representar nodos del árbol sintáctico abstracto
class ASTNode:
    def __init__(self, type, value=None, children=None):
        self.type = type
        self.value = value
        self.children = children if children else []

    def __repr__(self):
        return self._to_string()

    def _to_string(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.type}: {self.value}\n"
        for child in self.children:
            if child is not None:  # Asegurarse de que el hijo no sea None
                result += child._to_string(level + 1)
        return result

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
                ast = self.program_block()
            else:
                ast = self.program_c_style()
            print("\n--- Árbol Sintáctico Abstracto (AST) ---")
            print(ast)
            return ast
        except ParserError:
            pass

    # Analizar un programa con la estructura "program { ... }"
    def program_block(self):
        self.expect('PROGRAM')
        program_name = self.current_token.value
        self.expect('ID')
        self.expect('LBRACE')
        statements = self.statements()
        self.expect('RBRACE')
        self.expect('EOF')
        return ASTNode("Program", program_name, statements)

    # Analizar una lista de sentencias
    def statements(self):
        nodes = []
        while self.current_token.type not in ('RBRACE', 'EOF'):
            try:
                nodes.append(self.statement())
            except ParserError as e:
                self.errors.append(str(e))
                self.advance()
        return nodes

    # Analizar una sentencia individual
    def statement(self):
        if self.current_token.type == 'VAR':
            return self.variable_declaration()
        elif self.current_token.type in ('INT', 'FLOAT', 'STRING'):
            return self.variable_declaration_cstyle()
        elif self.current_token.type == 'ID':
            return self.assignment_or_function_call()
        elif self.current_token.type == 'PRINT':
            return self.print_statement()
        elif self.current_token.type == 'RETURN':
            return self.return_statement()
        else:
            expected = "declaración o instrucción"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # Analizar una declaración de variable
    def variable_declaration(self):
        self.expect('VAR')
        var_name = self.current_token.value
        self.expect('ID')
        self.expect('COLON')
        var_type = self.current_token.type
        if var_type in ('INT', 'FLOAT', 'STRING'):
            self.advance()
        else:
            expected = "tipo (int, float, string)"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)
        self.expect('SEMI')
        return ASTNode("VariableDeclaration", var_name, [ASTNode("Type", var_type)])
