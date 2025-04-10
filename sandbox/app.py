from flask import Flask, render_template, request, jsonify
import os
import sys
import traceback
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Add the project root to the Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

try:
    from language.utils import parse_nature_document
    from language.code_generator import generate_document_code
    from language.parser import llm_generate_function_code
except ImportError as e:
    print(f"Error importing language modules: {e}")
    print("Please ensure all dependencies are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/compile', methods=['POST'])
def compile_code():
    try:
        # Get the code from the request
        data = request.get_json()
        if not data or 'code' not in data:
            return jsonify({'error': 'No code provided'}), 400
        
        code = data['code']
        
        # Validate that code is not empty or None
        if not code or not isinstance(code, str):
            return jsonify({'error': 'Invalid code: must be a non-empty string'}), 400
        
        # Parse the document into functions
        functions = parse_nature_document(code)
        if not functions:
            return jsonify({'error': 'No valid functions found in the code. Make sure to use "function:" to start each function block.'}), 400
        
        # Generate code for each function using the LLM
        for func in functions:
            func.generated_code = llm_generate_function_code(func.instructions)
            if not func.generated_code or func.generated_code.startswith("# Error"):
                return jsonify({'error': f'Failed to generate code for function {func.name}'}), 400
        
        # Generate the final Python code
        python_code = generate_document_code(functions)
        
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
            exec(python_code, globals())
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
            'generated_code': python_code,
            'output': output_data['stdout'],
            'error': output_data['stderr']
        })
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        return jsonify({
            'error': f'Unexpected error: {str(e)}'
        }), 500

if __name__ == '__main__':
    # Check for required environment variables
    if not os.getenv('OPENAI_API_KEY'):
        print("Warning: OPENAI_API_KEY environment variable not set")
        print("Please set it before running the sandbox:")
        print("export OPENAI_API_KEY='your-api-key'")
    
    # Run the Flask app
    app.run(debug=True, port=5000) 