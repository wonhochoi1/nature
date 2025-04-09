from flask import Flask, render_template, request, jsonify
import sys
import os

# Add the parent directory to sys.path to import nature modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from language.utils import parse_nature_document
from language.code_generator import generate_document_code
from language.parser import llm_generate_function_code
from language.debugger import run_generated_code

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    nature_code = request.json.get('code', '')
    
    try:
        # Parse the document into function definitions
        functions = parse_nature_document(nature_code)
        
        # Generate code for each function using the LLM
        for func in functions:
            func.generated_code = llm_generate_function_code(func.instructions)
        
        # Generate the full Python code for the document
        full_code = generate_document_code(functions)
        
        # Create a dictionary to capture output
        output_data = {'stdout': '', 'stderr': ''}
        
        # Custom stdout/stderr redirector
        class OutputRedirector:
            def __init__(self, output_dict, stream_name):
                self.output_dict = output_dict
                self.stream_name = stream_name
                
            def write(self, text):
                self.output_dict[self.stream_name] += text
                
            def flush(self):
                pass
        
        # Save original stdout/stderr
        original_stdout = sys.stdout
        original_stderr = sys.stderr
        
        # Redirect stdout/stderr
        sys.stdout = OutputRedirector(output_data, 'stdout')
        sys.stderr = OutputRedirector(output_data, 'stderr')
        
        try:
            # Execute the generated code
            exec(full_code, globals())
            success = True
        except Exception as e:
            output_data['stderr'] += f"Execution error: {str(e)}\n"
            success = False
        finally:
            # Restore stdout/stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr
        
        return jsonify({
            'success': success,
            'generated_code': full_code,
            'output': output_data['stdout'],
            'error': output_data['stderr']
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'generated_code': '',
            'output': '',
            'error': f"Compilation error: {str(e)}"
        })

if __name__ == '__main__':
    app.run(debug=True) 