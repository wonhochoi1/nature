# language/utils.py
"""
Utility functions for parsing Nature language documents.
"""
from dataclasses import dataclass
from typing import List

@dataclass
class Function:
    """A function in a Nature document."""
    instructions: str

def load_nature_file(file_path):
    """Load the contents of a nature file."""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return ""

def parse_nature_document(content: str) -> List[Function]:
    """
    Parse a Nature document into functions.
    A Nature document consists of one or more 'function:' blocks.
    """
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
                if current_function is None:
                    current_function = Function(instructions='\n'.join(current_instructions))
                functions.append(current_function)
                current_instructions = []
            
            # Start a new function
            current_function = None
        else:
            # Add this line to the current function's instructions
            current_instructions.append(line)
    
    # Add the last function if there is one
    if current_instructions:
        if current_function is None:
            current_function = Function(instructions='\n'.join(current_instructions))
        functions.append(current_function)
    
    return functions
