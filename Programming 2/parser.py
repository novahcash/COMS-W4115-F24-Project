import sys
import json

class ParserError(Exception):
    pass

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current_token(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else ('EOF', None)
    
    def advance(self):
        self.pos += 1

    def expect(self, token_type):
        token = self.current_token()
        if token[0] == token_type:
            self.advance()
            return token
        else:
            raise ParserError(f"Expected token {token_type} but found {token[0]} at position {self.pos}")
     
    def parse(self):
        entries = self.parse_entries()
        self.expect('EOF')
        return {'type': 'SCRIPT', 'body': entries}
    
    def parse_entries(self):
        entries = []
        while True:
            token = self.current_token()
            if token[0] in ('DEDENT', 'EOF'):
                break
            elif token[0] == 'NEWLINE':
                self.advance()
                continue
            elif token[0] == 'IDENTIFIER':
                entries.append(self.parse_entry())
            else:
                break
        return entries
    
    def parse_entry(self):
        key = self.parse_key()
        self.expect('COLON')

        token = self.current_token()
        if token[0] == 'WHITESPACE':
            if len(token[1]) != 1:
                raise ParserError(f"Expected exactly one whitespace after COLON at position {self.pos}")
            self.advance()

            token = self.current_token()
            if token[0] == 'NEWLINE':
                raise ParserError(f"Unexpected NEWLINE after WHITESPACE at position {self.pos}")
            
            value = self.parse_value()

            token = self.current_token()
            if token[0] == 'NEWLINE':
                self.advance()

            return {'type': 'ENTRY', 'key': key, 'value': value}
        elif token[0] == 'NEWLINE':
            self.advance()

            token = self.current_token()
            if token[0] == 'INDENT':
                self.advance()

                nested_entries = self.parse_entries()
                self.expect('DEDENT')

                return {'type': 'ENTRY', 'key': key, 'value': [{'type': 'INDENT'}] + nested_entries + [{'type': 'DEDENT'}]}
            else:
                return {'type': 'ENTRY', 'key': key, 'value': []}
        else:
            raise ParserError(f"Expected exactly one whitespace or a newline after COLON at position {self.pos}")
    
    def parse_key(self):
        token = self.expect('IDENTIFIER')
        return {'type': 'KEY', 'value': token[1]}
    
    def parse_value(self):
        token_type, token_value = self.current_token()
        if token_type in {'INTEGER', 'FLOAT', 'STRING', 'IDENTIFIER'}:
            self.advance()
            return {'type': token_type, 'value': token_value}
        else:
            raise ParserError(f"Unexpected token {token_type} for value at position {self.pos}")

def parse_token_line(line):
    line = line.strip()[1:-1]
    parts = line.split(',', 1)
    token_type = parts[0].strip().strip("'\"")
    token_value = parts[1].strip().strip("'\"")
    return (token_type, token_value)

def process_indent(tokens):
    proc_tokens, indent_stack = [], [0]
    i = 0

    while i < len(tokens):
        token_type, token_value = tokens[i]
        if token_type == 'NEWLINE':
            proc_tokens.append((token_type, token_value))
            ws_len = 0
            i += 1

            while i < len(tokens) and tokens[i][0] == 'WHITESPACE':
                ws_len += len(tokens[i][1])
                i += 1
            
            current_indent = indent_stack[-1]
            if ws_len > current_indent:
                indent_stack.append(ws_len)
                proc_tokens.append(('INDENT', ''))
            elif ws_len < current_indent:
                while indent_stack and ws_len < indent_stack[-1]:
                    indent_stack.pop()
                    proc_tokens.append(('DEDENT', ''))

                if ws_len != indent_stack[-1]:
                    raise ParserError(f"Inconsistent indentation at token {i}")
        else:
            proc_tokens.append((token_type, token_value))
            i += 1

    while len(indent_stack) > 1:
        indent_stack.pop()
        proc_tokens.append(('DEDENT', ''))

    return proc_tokens

def read_file(path):
    try:
        with open(path, 'r') as file:
            lines = file.readlines()
            tokens = [parse_token_line(line) for line in lines]
            tokens = process_indent(tokens)
        return tokens
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{path}' not found.")
    except Exception as err:
        raise ValueError(f"Failed to read tokens from file: {err}")
    
def main(path):
    try:
        tokens = read_file(path)
        parser = Parser(tokens)
        ast = parser.parse()
        
        print("Abstract Syntax Tree (AST):")
        print(json.dumps(ast, indent=4))
    except Exception as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python parser.py <file_path>")
        sys.exit(1)
    path = sys.argv[1]
    main(path)