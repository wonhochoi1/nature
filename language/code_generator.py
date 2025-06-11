# nature/code_generator.py
import textwrap
import importlib
import sys
import subprocess
from pathlib import Path

class ModuleManager:
    def __init__(self):
        self.global_env = {}
        self.loaded_modules = set()
        self.module_paths = [
            Path("Lib"),  # Standard library modules
            Path("Modules"),  # User modules
        ]
    
    def resolve_module(self, module_name):
        """Resolve a module name to its actual implementation."""
        # First check if it's a built-in module
        try:
            module = importlib.import_module(module_name)
            return module
        except ImportError:
            pass
        
        # Then check our module paths
        for base_path in self.module_paths:
            module_path = base_path / f"{module_name}.py"
            if module_path.exists():
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return module
        
        raise ImportError(f"Module {module_name} not found in standard library or module paths")
    
    def load_module(self, module_name):
        """Load a module into the global environment."""
        if module_name in self.loaded_modules:
            return
        
        try:
            module = self.resolve_module(module_name)
            self.global_env[module_name] = module
            self.loaded_modules.add(module_name)
        except ImportError as e:
            print(f"Warning: Could not load module {module_name}: {e}")

def extract_imports(code):
    """Extract all imports from the code."""
    imports = set()
    for line in code.split('\n'):
        line = line.strip()
        if line.startswith('import ') or line.startswith('from '):
            # Extract the module name
            if line.startswith('import '):
                module = line.split('import ')[1].split()[0]
            else:  # from ... import ...
                module = line.split('from ')[1].split()[0]
            imports.add(module)
    return imports

def generate_document_code(functions):
    """
    For each FunctionDefinition, generate a Python function.
    Also create a main block that calls each function while sharing a global context.
    """
    code_lines = ["# Auto-generated Python code from .nature document", ""]
    
    # Add ModuleManager class definition
    code_lines.append("class ModuleManager:")
    code_lines.append("    def __init__(self):")
    code_lines.append("        self.global_env = {}")
    code_lines.append("        self.loaded_modules = set()")
    code_lines.append("")
    code_lines.append("    def load_module(self, name):")
    code_lines.append("        if name not in self.loaded_modules:")
    code_lines.append("            try:")
    code_lines.append("                module = __import__(name)")
    code_lines.append("                self.global_env[name] = module")
    code_lines.append("                self.loaded_modules.add(name)")
    code_lines.append("            except ImportError as e:")
    code_lines.append("                print(f'Warning: Could not load module {name}: {e}')")
    code_lines.append("")
    
    # Initialize module manager and global environment
    code_lines.append("module_manager = ModuleManager()")
    code_lines.append("global_env = module_manager.global_env")
    code_lines.append("")
    
    # Collect all imports from all functions
    all_imports = set()
    for func in functions:
        if func.generated_code:
            all_imports.update(extract_imports(func.generated_code))
    
    # Load required modules
    for module in sorted(all_imports):
        code_lines.append(f"module_manager.load_module('{module}')")
    code_lines.append("")
    
    # Generate function definitions
    for i, func in enumerate(functions):
        func_body = func.generated_code
        # Clean up the function body
        func_body = "\n".join(line for line in func_body.split("\n") 
                            if not line.strip().startswith("It's not clear") and
                            not line.strip().startswith("Without more context") and
                            not line.strip().startswith("However") and
                            not line.strip().startswith("If") and
                            not line.strip().startswith("```") and
                            not line.strip().startswith("Output:"))
        
        # Basic cleanup of function body
        func_body = func_body.strip()
        
        # Remove imports from function body since they're handled by module_manager
        func_body = "\n".join(line for line in func_body.split("\n") 
                            if not line.strip().startswith("import") and 
                            not line.strip().startswith("from"))
        
        # Replace direct module references with global_env access
        for module in all_imports:
            func_body = func_body.replace(f"{module}.", f"global_env['{module}'].")
        
        # Replace function references with proper function calls
        for j, other_func in enumerate(functions):
            if j < i:  # Only replace references to previous functions
                func_body = func_body.replace(f"function_{j+1}()", f"global_env['function_{j+1}']")
                func_body = func_body.replace("previous_function()", f"global_env['function_{i}']")
                # Add more flexible function references
                func_body = func_body.replace(f"function {j+1}", f"global_env['function_{j+1}']")
                func_body = func_body.replace(f"function before this one", f"global_env['function_{i}']")
        
        # Fix indentation in the function body
        func_body = textwrap.dedent(func_body)  # Remove any common leading whitespace
        func_body = textwrap.indent(func_body, "    ")  # Add proper indentation
        
        code_lines.append(f"def {func.name}():")
        code_lines.append("    global global_env")
        code_lines.append(func_body)
        code_lines.append("")
    
    # Add a main block that calls all functions and stores their return values
    code_lines.append("if __name__ == '__main__':")
    code_lines.append("    try:")
    for func in functions:
        code_lines.append(f"        print('Running {func.name}...')")
        code_lines.append("        try:")
        code_lines.append(f"            result = {func.name}()")
        code_lines.append(f"            global_env['{func.name}'] = result")
        code_lines.append("            if result is not None:")
        code_lines.append("                print('Result:', result)")
        code_lines.append("        except Exception as e:")
        code_lines.append(f"            print('Error in {func.name}:', e)")
        code_lines.append("            import traceback")
        code_lines.append("            traceback.print_exc()")
        code_lines.append(f"            global_env['{func.name}_error'] = str(e)")
        code_lines.append("")
    code_lines.append("    except Exception as e:")
    code_lines.append("        print('Fatal error:', e)")
    code_lines.append("        import traceback")
    code_lines.append("        traceback.print_exc()")
    code_lines.append("        print('\\nPlease check your .nature file for syntax errors.')")
    code_lines.append("        print('Common issues include:')")
    code_lines.append("        print('1. Missing or incorrect function declarations')")
    code_lines.append("        print('2. Invalid references to previous functions')")
    code_lines.append("        print('3. Unsupported module imports')")
    code_lines.append("        print('\\nWould you like to see the generated code? (y/n)')")
    code_lines.append("        response = input().strip().lower()")
    code_lines.append("        if response == 'y':")
    code_lines.append("            print('\\nGenerated code:')")
    code_lines.append("            print('\\n'.join(code_lines))")
    
    return "\n".join(code_lines)
