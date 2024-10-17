# RPG Scripting Language
Nova Cash (nhc2118)

## Lexical Grammar

### Identifier
- Used to represent all keys. Must start with letter; can otherwise be any combination of letters, digits, and underscores.
- Regular expression: `[A-Za-z][A-Za-z0-9_]*`

### Integer
- Represents an integer value for keys that take numeric values.
- Regular expression: `[0-9]+`

### Float
- Represents a decimal value for keys that take numeric values.
- Regular expression: `[0-9]+(\.[0-9]+)?`

### String
- Represents a string value for keys that take any form of non-numeric value. Enclosed by double quotes and can contain any character, including escaped quotes.
- Regular expression: `"([^"\\]*(\\.)*)*"`

### Colon
- Separates keys from associated values when followed by whitespace, or from child keys when followed by newline.
- Regular expression: `:`

### Whitespace
- A sequence of one or more space characters. Primarily used in conjunction with colon to separate key-value pairs. A sequence of two space characters per hierarchy level denotes indentation.
- Regular expression: `[ ]+`

### Newline
- A newline character, used to denote a new key when following a value or a parent-child relationship when followed by indentation. Supports Unix-style and Windows-style (carriage return) newlines.
- Regular expression: `\n|\r\n`

### Comment
- Code comments are denoted by the # character, instructing the compiler to ignore any further text in the line.
- Regular expression: `\#.*`

## How to Run
1. Ensure Python 3 is installed. If for some reason it isn't, go to https://www.python.org/downloads/ (Windows, Mac) or follow https://docs.python.org/3/using/unix.html (Linux, BSD, etc.) If you have Docker installed but not Python, I would love to know why.

2. Ensure you have proper permissions to run the shell script. On Unix systems, you might need to take ownership (`chown`) and make the file executable with `chmod +x`. On Windows, you might (but shouldn't) have to run as administrator.

3. Execute `run_lexer.sh` if you're using a Unix shell (Mac, Linux, BSD, Cygwin/Git Bash on Windows) or `run_lexer.bat` (Windows). This will perform lexical analysis on the five example programs I have provided in `/Sample Programs`.

4. If you want to try your own example program, use `python lexer.py <file_path>`.

## How it Works
- Upon running the script, the provided program will be parsed into a Python string. The `scan()` loop will iterate through every character in the string, calling the appropriate function upon reading the first character of any token type.
- Each scanner function can be represented as a DFA, with the start state `S0` representing the neutral state of before `scan()` reads the start of the token.

### Identifier
- Start state `S0`, end state `S1`.
- Transitions:
    - `S0 -> S1`: first character is a letter `[A-za-z]`.
    - `S1 -> S1`: continue accepting letters, digits `[0-9]`, and underscores `_`.
    - `S1 -> halt`: any other character encountered.

### Number (Integer and Float)
- Start state `S0`, end states `S1` (integer), `S3` (float), `S4` (error).
- Transitions:
    - `S0 -> S1`: first character is a digit `[0-9]`.
    - `S1 -> S1`: continue accepting digits.
    - `S1 -> S2`: decimal encountered.
    - `S1 -> halt`: any other character encountered.
    - `S2 -> S3`: digit encountered after decimal.
    - `S2 -> S4`: any other character encountered after decimal.
    - `S3 -> S3`: continue accepting digits after decimal.
    - `S3 -> S4`: another decimal encountered.
    - `S3 -> halt`: any other character encountered.

### String
- Start state `S0`, end states `S3` (accepting), `S4` (error).
- Transitions:
    - `S0 -> S1`: first character is a double quote `"`.
    - `S1 -> S2`: escaped character (e.g., `\"`) encountered.
    - `S2 -> S1`: escaped character accepted.
    - `S1 -> S3`: closing double quote encountered.
    - `S1 -> S4`: newline or EOF encountered before closing quote. Lexical error: Unterminated string.

### Colon
- Start state `S0`, end state `S1`.
- `S0 -> S1`: input character is a colon `:`.

### Whitespace
- Start state `S0`, end state `S1`.
- Transitions:
    - `S0 -> S1`: first character is a space ` `.
    - `S1 -> S1`: continue accepting spaces.
    - `S1 -> halt`: any other character encountered.

### Newline
- Start state `S0`, end state `S1`.
- Transitions:
    - `S0 -> S1`: input character is a newline `\n`.
    - `S0 -> S2`: input character is a carriage return `\r`.
    - `S2 -> S1`: newline following carriage return.

### Comment
- Start state `S0`, end state `S1`.
- Transitions:
    - `S0 -> S1`: Input character is `#`.
    - `S1 -> halt`: newline or EOF encountered; discard prior read characters.

### Lexical Error
- Start state `S0`, end state `S1`.
- Transitions:
    - `S0 -> S1`: input character does not match any token.