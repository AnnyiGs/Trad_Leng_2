from collections import namedtuple

# Nodo del árbol sintáctico abstracto
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
            if child is not None:  # Ensure child is not None
                result += child._to_string(level + 1)
        return result

    def to_string(self, level=0):
        indent = "  " * level
        result = f"{indent}{self.type}: {self.value}\n"
        for child in self.children:
            result += child.to_string(level + 1)
        return result

class ParserError(Exception):
    def __init__(self, message, token):
        super().__init__(message)
        self.token = token

class Parser:
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
        self.tokens = tokens
        self.pos = 0
        self.current_token = self.tokens[self.pos]
        self.errors = []

    def friendly(self, token_type):
        return self.friendly_names.get(token_type, token_type.lower())

    def advance(self):
        self.pos += 1
        if self.pos < len(self.tokens):
            self.current_token = self.tokens[self.pos]
        else:
            self.current_token = namedtuple('Token', ['type','value','line','column'])('EOF','',self.current_token.line,self.current_token.column)

    def expect(self, expected_type):
        if self.current_token.type == expected_type:
            self.advance()
        else:
            exp_friendly = self.friendly(expected_type)
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {exp_friendly} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # ---------------- Programa principal ----------------
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

    def program_block(self):
        self.expect('PROGRAM')
        program_name = self.current_token.value
        self.expect('ID')
        self.expect('LBRACE')
        statements = self.statements()
        self.expect('RBRACE')
        self.expect('EOF')
        return ASTNode("Program", program_name, statements)

    def program_c_style(self):
        nodes = []
        while self.current_token.type != 'EOF':
            try:
                nodes.append(self.function_or_declaration())
            except ParserError as e:
                self.errors.append(str(e))
                self.advance()
        return ASTNode("ProgramCStyle", children=nodes)

    # ---------------- Bloque de sentencias ----------------
    def statements(self):
        nodes = []
        while self.current_token.type not in ('RBRACE','EOF'):
            try:
                nodes.append(self.statement())
            except ParserError as e:
                self.errors.append(str(e))
                self.advance()
        return nodes

    def statement(self):
        if self.current_token.type == 'VAR':
            return self.variable_declaration()
        elif self.current_token.type in ('INT','FLOAT','STRING'):
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

    # ---------------- Declaraciones ----------------
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

    def variable_declaration_cstyle(self):
        self.advance()  # tipo
        self.expect('ID')
        self.expect('SEMI')

    # ---------------- Funciones y declaraciones ----------------
    def function_or_declaration(self):
        if self.current_token.type in ('INT','FLOAT','STRING'):
            next_token = self.tokens[self.pos+1] if self.pos+1 < len(self.tokens) else None
            if next_token and next_token.type == 'ID':
                next_next = self.tokens[self.pos+2] if self.pos+2 < len(self.tokens) else None
                if next_next and next_next.type == 'LPAREN':
                    self.function_declaration()
                else:
                    self.variable_declaration_cstyle()
            else:
                self.variable_declaration_cstyle()
        else:
            raise ParserError("Se esperaba declaración o función", self.current_token)

    def function_declaration(self):
        self.advance()  # tipo
        self.expect('ID')
        self.expect('LPAREN')
        self.parameter_list()
        self.expect('RPAREN')
        self.expect('LBRACE')
        self.statements()
        self.expect('RBRACE')

    def parameter_list(self):
        if self.current_token.type in ('INT','FLOAT','STRING'):
            self.advance()
            self.expect('ID')
            while self.current_token.type == 'COMMA':
                self.advance()
                if self.current_token.type in ('INT','FLOAT','STRING'):
                    self.advance()
                    self.expect('ID')
                else:
                    msg = f"[SINTÁCTICO] Se esperaba tipo en lista de parámetros en línea {self.current_token.line}, columna {self.current_token.column}"
                    self.errors.append(msg)
                    raise ParserError(msg, self.current_token)

    # ---------------- Asignación o llamada a función ----------------
    def assignment_or_function_call(self):
        id_name = self.current_token.value
        self.advance()  # ID
        if self.current_token.type == 'ASSIGN':
            self.advance()
            expr = self.expression()
            self.expect('SEMI')
            return ASTNode("Assignment", id_name, [expr])
        elif self.current_token.type == 'LPAREN':
            args = self.function_call()
            self.expect('SEMI')
            return ASTNode("FunctionCall", id_name, args)
        else:
            expected = "signo '=' o '('"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} después de identificador pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)

    # ---------------- Print ----------------
    def print_statement(self):
        self.expect('PRINT')
        self.expect('LPAREN')
        self.expression()
        self.expect('RPAREN')
        self.expect('SEMI')

    # ---------------- Return ----------------
    def return_statement(self):
        self.expect('RETURN')
        self.expression()
        self.expect('SEMI')

    # ---------------- Llamadas a funciones ----------------
    def function_call(self):
        self.expect('LPAREN')
        args = self.argument_list()
        self.expect('RPAREN')
        return args

    def argument_list(self):
        args = []
        if self.current_token.type not in ('RPAREN',):
            args.append(self.expression())
            while self.current_token.type == 'COMMA':
                self.advance()
                args.append(self.expression())
        return args

    # ---------------- Expresiones ----------------
    def expression(self):
        left = self.term()
        while self.current_token.type == 'OP' and self.current_token.value in ('+', '-'):
            op = self.current_token.value
            self.advance()
            right = self.term()
            left = ASTNode("BinaryOp", op, [left, right])
        return left

    def term(self):
        left = self.factor()
        while self.current_token.type == 'OP' and self.current_token.value in ('*', '/'):
            op = self.current_token.value
            self.advance()
            right = self.factor()
            left = ASTNode("BinaryOp", op, [left, right])
        return left

    def factor(self):
        if self.current_token.type == 'ID':
            id_name = self.current_token.value
            self.advance()
            if self.current_token.type == 'LPAREN':
                args = self.function_call()
                return ASTNode("FunctionCall", id_name, args)
            return ASTNode("Identifier", id_name)
        elif self.current_token.type in ('NUMBER', 'STRING'):
            value = self.current_token.value
            self.advance()
            return ASTNode("Literal", value)
        elif self.current_token.type == 'LPAREN':
            self.advance()
            expr = self.expression()
            self.expect('RPAREN')
            return expr
        else:
            expected = "expresión"
            found_friendly = self.friendly(self.current_token.type)
            msg = f"[SINTÁCTICO] Se esperaba {expected} pero se encontró {found_friendly} en línea {self.current_token.line}, columna {self.current_token.column}"
            self.errors.append(msg)
            raise ParserError(msg, self.current_token)
