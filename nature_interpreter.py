#!/usr/bin/env python3
"""
Nature language runtime
"""
import os
import sys
import sqlite3
import re
import math
import importlib.util

# Get the absolute path of this script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Add the project directory to Python path
sys.path.insert(0, script_dir)

# Check arguments
if len(sys.argv) < 2:
    print("Usage: ./nature <file.nature>")
    sys.exit(1)

file_path = sys.argv[1]

# Check if the file exists and has .nature extension
if not os.path.exists(file_path):
    print(f"Error: File {file_path} not found")
    sys.exit(1)

if not file_path.endswith(".nature"):
    print("Error: File must have .nature extension")
    sys.exit(1)

# Try to import the parser module
try:
    from language import parser
except ImportError:
    print("Warning: Could not import language.parser module. Using fallback patterns only.")
    parser = None

def parse_nature_file(file_path):
    """Parse a nature file into functions."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    functions = []
    current_function = None
    current_instructions = []
    
    # Parse each line
    for line in content.strip().split('\n'):
        line = line.strip()
        
        # Skip empty lines
        if not line:
            continue
        
        # If we encounter a function declaration
        if line.lower().startswith('function:'):
            # If we were already building a function, add it to our list
            if current_instructions:
                functions.append('\n'.join(current_instructions))
                current_instructions = []
            
            # Start a new function
            current_function = None
        else:
            # Add this line to the current function's instructions
            current_instructions.append(line)
    
    # Add the last function if there is one
    if current_instructions:
        functions.append('\n'.join(current_instructions))
    
    return functions

def execute_python_code(code, context=None):
    """Execute Python code with safety precautions."""
    if context is None:
        context = {}
    
    # Create a safe execution environment
    safe_globals = {
        "__builtins__": {
            "print": print,
            "range": range,
            "list": list,
            "len": len,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "min": min,
            "max": max,
            "sum": sum,
            "sorted": sorted,
            "abs": abs,
            "round": round,
            "pow": pow,
            "tuple": tuple,
            "set": set,
            "dict": dict,
            "zip": zip,
            "enumerate": enumerate,
            "map": map,
            "filter": filter,
            "any": any,
            "all": all,
            "format": format,
            "reversed": reversed,
            "isinstance": isinstance,
            "type": type,
        },
        "math": math,
        "re": re,
    }
    
    # Add context variables to execution environment
    safe_globals.update(context)
    
    # Create a local scope
    local_vars = {}
    
    # First check for syntax errors
    try:
        compile(code, '<string>', 'exec')
    except SyntaxError as e:
        print(f"Syntax error in generated code: {e}")
        if parser is not None and hasattr(parser, "llm_debug_suggestion"):
            debug_suggestion = parser.llm_debug_suggestion(
                "Fix Python syntax error",
                str(e),
                code
            )
            print(f"Debug suggestion: {debug_suggestion}")
            
            # Try to fix common syntax issues
            if hasattr(parser, "sanitize_code"):
                print("Attempting to fix code...")
                # Get the current function's instructions
                instructions = context.get("current_instructions", "Unknown instruction")
                code = parser.sanitize_code(code, instructions)
                print("Code fixed, retrying execution.")
                
                try:
                    # Try compiling again
                    compile(code, '<string>', 'exec')
                except SyntaxError as e:
                    print(f"Still has syntax errors after fixing: {e}")
                    return None
        else:
            return None
    
    try:
        # Execute the code
        exec(code, safe_globals, local_vars)
        
        # Return the result if available
        if "result" in local_vars:
            return local_vars["result"]
        else:
            return None
    except Exception as e:
        print(f"Error executing code: {e}")
        
        # Try to get debugging help if parser module is available
        if parser is not None and hasattr(parser, "llm_debug_suggestion"):
            debug_suggestion = parser.llm_debug_suggestion(
                "Fix Python runtime error",
                str(e),
                code
            )
            print(f"Debug suggestion: {debug_suggestion}")
        
        return None

def execute_function(instructions, context=None):
    """Execute a single function based on its instructions."""
    if context is None:
        context = {}
    
    function_id = context.get("current_function_id", "function_1")
    print(f"\nExecuting function: {function_id}")
    print(f"Instructions: {instructions[:100]}..." if len(instructions) > 100 else f"Instructions: {instructions}")
    
    # Store the current instructions in the context
    context["current_instructions"] = instructions
    
    result = None
    
    # Use the parser module if available
    if parser is not None:
        try:
            # First try using IR nodes
            print("Generating IR nodes from instructions...")
            ir_nodes = parser.llm_generate_ir_nodes(instructions, function_id)
            
            if ir_nodes and "nodes" in ir_nodes:
                for node in ir_nodes["nodes"]:
                    try:
                        # Handle different operation types
                        if node["operation_type"] == "PythonCode":
                            code = node["details"]["code"]
                            print(f"Executing generated code...")
                            result = execute_python_code(code, context)
                            context[node["id"]] = result
                        
                        elif node["operation_type"] == "SQLQuery":
                            query = node["details"]["query"]
                            params = node["details"].get("params", [])
                            
                            # Create in-memory SQLite database if not already in context
                            if "sqlite_conn" not in context:
                                context["sqlite_conn"] = sqlite3.connect(':memory:')
                            
                            cursor = context["sqlite_conn"].cursor()
                            if params:
                                cursor.execute(query, params)
                            else:
                                cursor.execute(query)
                            
                            # Fetch results if it's a SELECT query
                            if query.strip().upper().startswith("SELECT"):
                                result = cursor.fetchall()
                                print(f"SQL query results: {result}")
                            else:
                                print(f"SQL query executed: {query}")
                            
                            context["sqlite_conn"].commit()
                            context[node["id"]] = result
                        
                        elif node["operation_type"] == "Print":
                            value_ref = node["details"].get("value_ref")
                            if value_ref and value_ref in context:
                                print(f"Print result: {context[value_ref]}")
                                result = context[value_ref]
                            else:
                                print("Nothing to print (reference not found)")
                    except Exception as e:
                        print(f"Error executing node: {e}")
                
                # If we successfully executed the IR nodes, return the result
                if result is not None:
                    return result
        except Exception as e:
            print(f"Error with IR nodes: {e}")
        
        # If IR nodes failed or didn't produce a result, try direct code generation
        try:
            print("Trying direct code generation...")
            code = parser.llm_generate_function_code(instructions)
            if code:
                result = execute_python_code(code, context)
                if result is not None:
                    return result
        except Exception as e:
            print(f"Error with direct code generation: {e}")
    
    # If all else fails
    print(f"All LLM approaches failed. Using simple execution.")
    return f"Completed: {instructions}"

def execute_nature_file(file_path):
    """Execute a nature file."""
    functions = parse_nature_file(file_path)
    context = {}
    results = []
    
    # Process each function
    for i, instructions in enumerate(functions):
        function_id = f"function_{i+1}"
        context["current_function_id"] = function_id
        result = execute_function(instructions, context)
        results.append(result)
        context[f"{function_id}_result"] = result
    
    return results

try:
    # Execute the nature file
    execute_nature_file(file_path)
except Exception as e:
    print(f"Error executing file: {e}")
    sys.exit(1) 