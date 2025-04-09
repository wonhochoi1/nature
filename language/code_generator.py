# nature/code_generator.py
import textwrap

def generate_document_code(functions):
    """
    For each FunctionDefinition in functions, generate a Python function.
    Returns the complete Python code as a string.
    """
    code_lines = ["# Auto-generated Python code from .nature document", ""]
    for func in functions:
        func_body = func.generated_code
        code_lines.append(f"def {func.name}():")
        indented_body = textwrap.indent(func_body, "    ")
        code_lines.append(indented_body)
        code_lines.append("")
    # Add a main block to run all functions.
    code_lines.append("if __name__ == '__main__':")
    for func in functions:
        code_lines.append(f"    print('Running {func.name}...')")
        code_lines.append("    try:")
        code_lines.append(f"        {func.name}()")
        code_lines.append("    except Exception as e:")
        code_lines.append(f"        print('Error in {func.name}:', e)")
        code_lines.append("        import traceback")
        code_lines.append("        traceback.print_exc()")
        code_lines.append("")
    return "\n".join(code_lines)
