# nature/ast.py
# Using a standard class instead of dataclass to avoid import issues
class FunctionDefinition:
    """Represents a parsed function in a Nature document."""
    def __init__(self, name, instructions, generated_code=None):
        self.name = name              # Function name (e.g., function_1)
        self.instructions = instructions  # The natural language instructions
        self.generated_code = generated_code  # Python code generated from the instructions

    def __repr__(self):
        return f"FunctionDefinition(name='{self.name}', instructions='''{self.instructions}''')"
