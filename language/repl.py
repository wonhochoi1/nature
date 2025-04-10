# language/repl.py
import sys
from language.utils import load_nature_file, parse_nature_document
from language.code_generator import generate_document_code
from language.debugger import run_generated_code
from language.parser import llm_generate_function_code
from language.ast import FunctionDefinition
from language.importer import load_module


def load_global_imports(import_list):
    global_env = {}
    for module_name in import_list:
        global_env[module_name] = load_module(module_name)
    return global_env

def main():
    # Load instructions from a file if provided; otherwise, use REPL mode.
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        if not file_path.endswith(".nature"):
            print("Warning: It is recommended to use a '.nature' extension for natural language files.")
        document_text = load_nature_file(file_path)
    else:
        print("Enter your natural language instructions. Use 'function:' to start a function block,")
        print("and type 'run' (on a new line) to execute.")
        lines = []
        while True:
            try:
                line = input(">> ")
            except EOFError:
                break
            if line.strip().lower() == "run":
                break
            lines.append(line)
        document_text = "\n".join(lines)
    
    print("\n--- Loaded Document ---")
    print(document_text)


    # Parse the document into function definitions.
    functions = parse_nature_document(document_text)
    print("\n--- Parsed Function Definitions (AST) ---")
    for func in functions:
        print(func)
    
    # Generate code for each function using the LLM.
    for func in functions:
        func.generated_code = llm_generate_function_code(func.instructions)

    # Generate the full Python code for the document.
    full_code = generate_document_code(functions)
    print("\n--- Generated Python Code ---")
    print(full_code)
    
    # Execute the generated code.
    print("\n--- Executing Generated Code ---")
    run_generated_code(full_code, functions)

if __name__ == "__main__":
    main()
