import os
import importlib.util

def load_module(module_name):
    """Resolves a module from Nature's Lib or Modules."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    lib_path = os.path.join(base_dir, "..", "lib", f"{module_name}.nature")
    modules_path = os.path.join(base_dir, "..", "modules")

    if os.path.exists(lib_path):
        with open(lib_path, "r") as f:
            code = f.read()
        # Compile the Nature module (using your own parser/compiler)
        module_env = compile_nature_module(code)
        return module_env
    else:
        # For native modules, use Python's mechanisms
        try:
            module_file = os.path.join(modules_path, f"_{module_name}.so")
            spec = importlib.util.spec_from_file_location(module_name, module_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            raise ImportError(f"Module '{module_name}' not found: {e}")

def compile_nature_module(code):
    """Stub function to compile a Nature module from code."""
    module_env = {}
    # Here you would parse and compile the code.
    # For this example, we simply exec the code.
    exec(code, module_env)
    return module_env
