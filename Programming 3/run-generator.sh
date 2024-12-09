#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Function to display usage information
usage() {
    echo "Usage: $0 <filename>.txt"
    exit 1
}

# Check if exactly one argument is provided
if [ "$#" -ne 1 ]; then
    echo "Error: Invalid number of arguments."
    usage
fi

# Input file
INPUT_FILE="$1"

# Check if the input file exists and is a regular file
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: File '$INPUT_FILE' does not exist."
    exit 1
fi

# Extract the base filename without the extension
BASENAME=$(basename "$INPUT_FILE" .txt)

# Define the Temp directory path
TEMP_DIR="./Temp"

# Create the Temp directory if it doesn't exist
mkdir -p "$TEMP_DIR"

# Paths for intermediate and output files
TOKENIZED_FILE="$TEMP_DIR/${BASENAME}_tokenized.txt"
AST_FILE="$TEMP_DIR/${BASENAME}_ast.txt"
CPP_FILE="${BASENAME}.cpp"
EXECUTABLE="./${BASENAME}"

# Step 1: Tokenization using lexer.py
echo "Step 1: Tokenizing '$INPUT_FILE'..."
python lexer.py "$INPUT_FILE" > "$TOKENIZED_FILE"
echo "Tokenized output written to '$TOKENIZED_FILE'."

# Step 2: Parsing using parser.py
echo "Step 2: Parsing '$TOKENIZED_FILE'..."
python parser.py "$TOKENIZED_FILE" > "$AST_FILE"
echo "Abstract Syntax Tree (AST) written to '$AST_FILE'."

# Step 3: Code Generation using generator.py
echo "Step 3: Generating C++ code from '$AST_FILE'..."
python generator.py "$AST_FILE"
echo "C++ code generated in '$CPP_FILE'."

# Check if the C++ file was generated
if [ ! -f "$CPP_FILE" ]; then
    echo "Error: C++ file '$CPP_FILE' was not generated."
    exit 1
fi

# Step 4: Compilation using g++
echo "Step 4: Compiling '$CPP_FILE'..."
g++ "$CPP_FILE" -o "$BASENAME"
echo "Compilation successful. Executable '$BASENAME' created."

# Step 5: Execution of the compiled program
echo "Step 5: Executing './$BASENAME'..."
"$EXECUTABLE"

echo "Pipeline completed successfully."

# Exit the script successfully
exit 0

