# RPG Scripting Language
Nova Cash (nhc2118) [Team Nova]

## How to Install
1. You should use a Unix environment. Mac, Linux, BSD, etc. users should have no problems. Windows users will need to use Windows Subsystem for Linux (WSL) or a virtual machine. I did not want to deal with accounting for setting up a C++ development environment on Windows.  You can manually execute each step on any system with Python and a C++ compiler installed, but my shell script only supports these systems.

2. Ensure Python 3 is installed. If for some reason it isn't, go to https://www.python.org/downloads/ (Mac) or follow https://docs.python.org/3/using/unix.html (Linux, BSD, etc.)

3. To run the final generated code, ensure gcc is installed. All Linux systems should have it installed. Mac users can install Homebrew (https://brew.sh/) and execute `brew install gcc`.

4. Ensure you have proper permissions to run the shell script. Take ownership using `chown` and make the file executable with `chmod +x`.


## How it Works
1. Define an entity in the language. The syntax is identical to YAML, but with a specific subset of valid entries:
- An entity must have a `name` (string). Code generation will fail without one.
- All entities have the following `attributes` (int): `hp`, `p_attack`, `m_attack`, `p_defense`, `m_defense`, `speed`, `level`, `exp`. Any undefined attributes are assigned a default value of 1.
- All entities must have an `idle` `sprite` (string), but an arbitrary number of additional sprites can be declared. If an idle sprite is not defined, a default sprite will be assigned.
- All entities must have `behavior`, which includes the `ai_script` and an arbitrary number of `attack`s. At least one `attack` must be defined with the following structure: 
  - `target` (string, "single", "multi", "row", or "all"), `damage_type` (string, "physical" or "magical"), `modifier` (float, >= 0), `mod_type` (string, "additive" or "multiplicative"), `effect` (string), `effect_chance` (float, 0 <= n <= 1).
  - If `ai_script` is not defined, a default AI script will be assigned. `basic_attack` will be generated with default values if it is not present, including if no attacks are present at all. Additionally, any undefined variables composing an `attack` will be assigned default values.

2. Run the shell script. The shell script will take in an entity script as user input. The entity script will be fed to `lexer.py` for tokenization, and the tokenized output will be written to a file `<filename>_tokenized.txt` in the `/Temp` folder in the program directory. Consult `lexer_README.md` for more detail on how it works.

3. The tokenized output will be fed to `parser.py` for parsing. The Abstract Syntax Tree (AST) will be written to a file `<filename>_ast.txt` in the `/Temp` folder. Consult `parser_README.md` for more detail on how it works.

4. The AST will be fed to `generator.py` for code generation. All functions and variables that should be present in the final code are checked for existence and type-correctness. Any caught errors will prevent code generation and be displayed to the user. Undefined entries that have a default value will be assigned one. Once the AST is processed, the program will generate a C++ class `<filename>.cpp` that matches the structure of the original entity script.

5. The shell script will compile the generated C++ code, which includes various getter methods and a main function for testing.

6. Execute the C++ program. It should print out (roughly) the original entity script, showing that the YAML-like structure has been successfully translated to working C++.

## Demo
https://youtu.be/IpwDT4-JwL8