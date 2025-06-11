# language/utils.py
from .ast import FunctionDefinition

def load_nature_file(file_path):
    """Reads a .nature file and returns its content."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return ""

def parse_nature_document(document_text):
    """
    Parse a complete document into separate function definitions.
    Functions start with a line that begins with "function:".
    Everything following that line (until the next "function:" or end-of-file) 
    is part of that function.
    """
    functions = []
    current_function_lines = []
    current_function_name = None
    func_counter = 0

    lines = document_text.splitlines()
    for line in lines:
        line_strip = line.strip()
        if line_strip.lower().startswith("function:"):
            if current_function_lines and current_function_name:
                instructions = "\n".join(current_function_lines).strip()
                functions.append(FunctionDefinition(
                    name=current_function_name,
                    instructions=instructions,
                    generated_code=None  # Will be set later
                ))
            func_counter += 1
            current_function_name = f"function_{func_counter}"
            # Optionally capture extra text after "function:".
            extra = line_strip[9:].strip()
            current_function_lines = [extra] if extra else []
        else:
            if line_strip:
                current_function_lines.append(line_strip)
    
    # Handle the last function
    if current_function_lines and current_function_name:
        instructions = "\n".join(current_function_lines).strip()
        functions.append(FunctionDefinition(
            name=current_function_name,
            instructions=instructions,
            generated_code=None  # Will be set later
        ))
    
    return functions
