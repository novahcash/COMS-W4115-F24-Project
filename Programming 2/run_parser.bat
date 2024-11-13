@echo off
echo Running parser on sample tokenized programs...

echo Running parser on basic_program.txt...
python parser.py "Sample Tokens\basic_program.txt"
echo.

echo Running parser on proposal_example_program.txt...
python parser.py "Sample Tokens\proposal_example_program.txt"
echo.

echo Running parser on very_nested_program.txt...
python parser.py "Sample Tokens\very_nested_program.txt"
echo.

echo Running parser on improperly_indented_program.txt...
python parser.py "Sample Tokens\improperly_indented_program.txt"
echo.

echo Running parser on improper_key_value_program.txt...
python parser.py "Sample Tokens\improper_key_value_program.txt"
echo.

echo Parser execution completed.