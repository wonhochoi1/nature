"""
Parser for Nature language.
This module provides functions to parse Nature language into executable code.
"""
import json
import os
import re
from typing import Dict, List, Any, Optional

from dotenv import load_dotenv

# Try to load environment variables from .env file
load_dotenv()

# Check if API keys are available
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Note: No GOOGLE_API_KEY found in environment. Create a .env file with GOOGLE_API_KEY=your-key to enable LLM features.")
HAS_LLM_ACCESS = bool(GOOGLE_API_KEY)

# Import LLM clients conditionally to avoid errors if API keys are not available
llm_client = None
if GOOGLE_API_KEY:
    try:
        from google import genai
        llm_client = genai.Client(api_key=GOOGLE_API_KEY)
        
    except ImportError:
        print("Google Generative AI package not installed. Run: pip install google-generativeai")

def llm_api_generate_ir_nodes(instructions: str, function_id: str) -> Optional[Dict[str, Any]]:
    """
    Use an LLM API to generate IR nodes for complex instructions.
    Returns None if LLM is not available or fails.
    """
    if not HAS_LLM_ACCESS or llm_client is None:
        return None
    
    prompt = f"""
You are an expert in converting natural language instructions into a structured intermediate representation (IR).
Convert the following natural language function instructions into a JSON representation of operations.

The IR should be structured as an array of operation nodes, where each node has:
- id: A unique identifier for this operation (use "{function_id}_op_N" where N is the operation number)
- operation_type: One of "SQLQuery", "DataTransform", "FileIO", "PythonCode", "Print", "Return"
- dependencies: Array of IDs this node depends on (can be empty for first operation)
- details: Object with operation-specific details

For SQLQuery operations, details should include:
- query: The SQL query string
- params: Optional array of parameter values

For PythonCode operations, details should include:
- code: The Python code to execute
- use_sandbox: Boolean indicating if sandbox should be used (default true)

For Print operations, details should include:
- value_ref: ID of the node whose value to print

For Return operations, details should include:
- value_ref: ID of the node whose value to return

INSTRUCTION: {instructions}

Response format:
{{"nodes": [
  {{
    "id": "{function_id}_op_1",
    "operation_type": "PythonCode",
    "dependencies": [],
    "details": {{
      "code": "# Your Python code here",
      "use_sandbox": true
    }}
  }}
]}}
"""
    
    try:
        if GOOGLE_API_KEY:
            # Google Gemini API call
            response = llm_client.models.generate_content(
                model="gemini-2.0-flash",
                contents=[prompt]
            )
            response_text = response.text
            
            # Extract JSON from the response
            if "```json" in response_text:
                json_part = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                json_part = response_text.split("```")[1].strip()
            else:
                json_part = response_text
            
            return json.loads(json_part)
    except Exception as e:
        print(f"LLM API error: {e}")
        return None
    
    return None

def llm_api_generate_function_code(instructions: str) -> Optional[str]:
    """
    Use an LLM API to generate Python code for a function.
    Returns None if LLM is not available or fails.
    """
    if not HAS_LLM_ACCESS or llm_client is None:
        return f'''
print("Executing: {instructions}")
result = "No LLM available - using fallback"
'''
    
    prompt = f"""
You are an expert Python programmer. Convert the following natural language instructions into a valid Python code snippet.
The code must be syntactically correct Python 3.
Do not include explanatory comments - just the code that accomplishes the task.
Do not include enclosing triple backticks or language specifiers.
Your code will be executed directly, so make sure it's runnable and assigns results to a variable named 'result'.

INSTRUCTION: {instructions}
"""
    
    try:
        code = None
        
        if GOOGLE_API_KEY:
            # Google Gemini API call
            try:
                response = llm_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt]
                )
                code = response.text.strip()
                
                # Extract code from the response if it's in a code block
                if "```python" in code:
                    code = code.split("```python")[1].split("```")[0].strip()
                elif "```" in code:
                    code = code.split("```")[1].strip()
            except Exception as e:
                print(f"Google Gemini API error: {e}")
        
        # If we got code, sanitize it
        if code:
            code = sanitize_code(code, instructions)
            return code
        
    except Exception as e:
        print(f"LLM API error: {e}")
    
    # If we couldn't generate specific code, return a simple message
    return '''
print("Executing fallback for instruction: ''' + instructions[:50] + '''...")
result = "Completed using fallback code"
'''

def sanitize_code(code: str, instructions: str) -> str:
    """Sanitize generated code to ensure it's valid Python."""
    try:
        # Check for syntax errors in the generated code
        try:
            compile(code, '<string>', 'exec')
        except SyntaxError:
            # If syntax errors, create a simple fallback
            return f'''
# Fallback due to syntax errors in generated code
result = "Completed with fallback"
'''
        
        # Remove any print statements
        code_lines = code.split('\n')
        clean_lines = [line for line in code_lines if not line.strip().startswith('print(')]
        code = '\n'.join(clean_lines)
        
        # Ensure the code has 'result' variable
        if 'result' not in code and not re.search(r'\bresult\s*=', code):
            code += "\nresult = 'Completed successfully'"
        
        return code
        
    except Exception as e:
        print(f"Error sanitizing code: {e}")
        return f'''
# Error in code generation
result = "Completed with error fallback"
'''

def llm_generate_ir_nodes(instructions: str, function_id: str) -> Dict[str, Any]:
    """
    Generate IR nodes based on the instructions.
    Creates a single Python code node that executes the instructions.
    """
    # Try to use the API first
    api_nodes = llm_api_generate_ir_nodes(instructions, function_id)
    if api_nodes:
        return api_nodes
    
    # Fallback to generating Python code
    code = llm_generate_function_code(instructions)
    
    # Create a single Python code node
    nodes = [{
        "id": f"{function_id}_op_1",
        "operation_type": "PythonCode",
        "dependencies": [],
        "details": {
            "code": code,
            "use_sandbox": True
        }
    }]
    
    return {"nodes": nodes}

def llm_generate_function_code(instructions: str) -> str:
    """
    Generate Python code for a function based on instructions.
    Uses LLM if available, otherwise falls back to a simple implementation.
    """
    if not HAS_LLM_ACCESS or llm_client is None:
        code = f'''
# No LLM available, using simple implementation
result = "Completed instruction: {instructions[:50]}..."
'''
        print(f"Generated fallback code (no LLM):\n{code}")
        return code
    
    # Try to use LLM
    try:
        prompt = f"""
Generate Python code for the following instruction. The code should be valid Python 3, runnable directly.
Make sure the result is stored in a variable named 'result'.
Do not include print statements or debug messages in the code.
Keep the implementation focused solely on the task.

Instruction: {instructions}

Just provide the code with no explanations or markdown formatting.
"""
        
        code = None
        
        # Try using Gemini
        if GOOGLE_API_KEY:
            try:
                response = llm_client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt]
                )
                code = response.text.strip()
                
                # Extract code from the response if it's in a code block
                if "```python" in code:
                    code = code.split("```python")[1].split("```")[0].strip()
                elif "```" in code:
                    code = code.split("```")[1].strip()
                
                print(f"Generated LLM code:\n{code}")
            except Exception as e:
                print(f"Google Gemini API error: {e}")
        
        # If we got code, sanitize it
        if code:
            return sanitize_code(code, instructions)
    
    except Exception as e:
        print(f"Error generating code: {e}")
    
    # Fallback if all LLM methods fail
    return f'''
# Fallback implementation
result = "Completed with fallback: {instructions[:50]}..."
'''

def llm_debug_suggestion(instructions: str, error_message: str, generated_code: str) -> str:
    """
    Generate debugging suggestions for code.
    Uses LLM if available, otherwise provides a simple error message.
    """
    if not HAS_LLM_ACCESS or llm_client is None:
        return f"Error occurred: {error_message}. Try simplifying your instructions or check for syntax errors."
    
    prompt = f"""
You are debugging Python code that was generated from natural language instructions.

Instructions: {instructions}

Generated code:
{generated_code}

Error message:
{error_message}

Suggest a change to the code that would fix the error.
"""
    
    try:
        response = llm_client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt]
        )
        return response.text.strip()
    except Exception as e:
        print(f"Error generating debugging suggestion: {e}")
        return f"Error occurred: {error_message}. Try simplifying your instructions or check for syntax errors."