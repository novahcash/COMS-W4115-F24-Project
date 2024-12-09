import os
import sys

class Lexer:
    def __init__(self, input):
        self.input = input
        self.length = len(input)
        self.pos = 0
        self.tokens = []

    def is_letter(self, char):
        return 'a' <= char <= 'z' or 'A' <= char <= 'Z'
    
    def is_digit(self, char):
        return '0' <= char <= '9';

    def is_whitespace(self, char):
        return char == ' '
    
    def is_newline(self, char):
        return char == '\n' or char == '\r'
    
    def peek(self):
        if self.pos < self.length:
            return self.input[self.pos]
        return None
    
    def advance(self):
        self.pos += 1
        return self.peek()

    def add_token(self, type, val):
        self.tokens.append((type, val))

    def scan_identifier(self):
        start_pos = self.pos
        while self.peek() is not None and (self.is_letter(self.peek()) or self.is_digit(self.peek()) or self.peek() == '_'):
            self.advance()
        id = self.input[start_pos:self.pos]
        self.add_token("IDENTIFIER", id)

    def scan_number(self):
        start_pos = self.pos
        decimal = False

        while self.peek() is not None and self.is_digit(self.peek()) or self.peek() == '.':
            if self.peek() == '.':
                if decimal:
                    self.add_token("LEXICAL_ERROR", "Invalid float.")
                    return
                decimal = True
            self.advance()

        if decimal and not self.is_digit(self.input[self.pos - 1]):
            self.add_token("LEXICAL_ERROR", "Invalid float.")
            return
        
        num = self.input[start_pos:self.pos]
        self.add_token("FLOAT" if decimal else "INTEGER", num)

    def scan_string(self):
        self.advance()       
        start_pos = self.pos
        while self.peek() is not None:
            if self.peek() == '\n' or self.peek() == '\r':
                self.add_token("LEXICAL_ERROR", "String not terminated.")
                return

            if self.peek() == '\\':
                self.advance()
                if self.peek() is not None:
                    self.advance()
            elif self.peek() == '"':
                break
            else:
                self.advance()

        if self.peek() == '"':
            string = self.input[start_pos:self.pos]
            self.advance()
            self.add_token("STRING", string)
        else:
            self.add_token("LEXICAL_ERROR", "String not terminated.")

    def scan_colon(self):
        self.add_token("COLON", ':')
        self.advance()
        
    def scan_whitespace(self):
        start_pos = self.pos
        while self.peek() is not None and self.is_whitespace(self.peek()):
            self.advance()
        space = self.input[start_pos:self.pos]
        self.add_token("WHITESPACE", space)
        
    def scan_newline(self):
        if self.peek() == '\r':
            self.advance()
        if self.peek() == '\n':
            self.advance()
        self.add_token("NEWLINE", '\n')

    # Skip comments entirely
    def scan_comment(self):
        while self.peek() is not None and not self.is_newline(self.peek()):
            self.advance()
    
    def scan(self):
        while self.peek() is not None:
            char = self.peek()

            if self.is_letter(char):
                self.scan_identifier()
            elif self.is_digit(char):
                self.scan_number()
            elif char == '"':
                self.scan_string()
            elif char == ':':
                self.scan_colon()
            elif char == ' ':
                self.scan_whitespace()
            elif char == '\r' or char == '\n':
                self.scan_newline()
            elif char == '#':
                self.scan_comment()
            else:
                self.add_token("LEXICAL_ERROR", f"Unexpected character '{char}'")
                self.advance()
        return self.tokens
    
def read_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"File '{path}' not found.")
    return data;

def main(path):
    try:
        program = read_file(path)
        lexer = Lexer(program)
        
        tokens = lexer.scan()
        
        os.makedirs("Temp", exist_ok=True)
        filename = os.path.basename(path).rsplit('.', 1)[0]
        output_path = os.path.join("Temp", f"{filename}_tokenized.txt")

        with open(output_path, 'w') as output_file:
            for token in tokens:
                output_file.write(f"{token}\n")
            
    except Exception as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python lexer.py <file_path>")
        sys.exit(1)
    path = sys.argv[1]
    main(path)