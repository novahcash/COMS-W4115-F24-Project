# RPG Scripting Language
Nova Cash (nhc2118) [Team Nova]

## Context-Free Grammar: Production Rules
Script: Start symbol; represents the entire script, consisting of one or more Entries and the end of file.

`Script -> Entries EOF`

Entries: A sequence of one or more Entry symbols.

`Entries -> Entry Entries | Entry`

Entry: A key-value pair separated by a colon and followed by a newline, or a Key followed by a colon and newline, then a nested block of Entries.

`Entry -> Key COLON Value NEWLINE | Key COLON NEWLINE INDENT Entries DEDENT`

Key: An identifier.

`Key -> IDENTIFIER`

Value: An integer, float, or string value.

`Value -> INTEGER | FLOAT | STRING`

## How to Run
1. Ensure Python 3 is installed. If for some reason it isn't, go to https://www.python.org/downloads/ (Windows, Mac) or follow https://docs.python.org/3/using/unix.html (Linux, BSD, etc.)

2. Ensure you have proper permissions to run the shell script. On Unix systems, you might need to take ownership (`chown`) and make the file executable with `chmod +x`. On Windows, you might (but shouldn't) have to run as administrator.

3. Execute `run_parser.sh` if you're using a Unix shell (Mac, Linux, BSD, Cygwin/Git Bash on Windows) or `run_parser.bat` (Windows). This will parse and output the generated Abstract Syntax Tree for each of the five example programs I have provided tokens for in `/Sample Tokens`. Check `/Sample Programs` for the corresponding program code.

4. If you want to try your own example program, run the lexer and paste or pipe the output into a text file, then use `python parser.py <file_path>`.

## Demo
https://youtu.be/kCnQCDpTv3k

## Notes
My lexer's handling of comments adds superfluous newlines that messed with the parser. I have removed comments from my tokenized sample programs and did not implement comment handling in the parser. Whenever it is time to combine the project parts, I plan to revise the lexer to ignore comments completely instead of tokenizing them.