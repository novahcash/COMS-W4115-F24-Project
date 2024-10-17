@echo off
echo Running lexer on sample programs...

echo Running lexer on basic_program.txt...
python lexer.py "Sample Programs\basic_program.txt"
echo.

echo Running lexer on proposal_example_program.txt...
python lexer.py "Sample Programs\proposal_example_program.txt"
echo.

echo Running lexer on unterminated_string_program.txt...
python lexer.py "Sample Programs\unterminated_string_program.txt"
echo.

echo Running lexer on invalid_float_program.txt...
python lexer.py "Sample Programs\invalid_float_program.txt"
echo.

echo Running lexer on tabs_as_whitespace_program.txt...
python lexer.py "Sample Programs\tabs_as_whitespace_program.txt"
echo.

echo Lexer execution completed.