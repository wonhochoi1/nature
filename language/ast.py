# nature/ast.py
from dataclasses import dataclass

@dataclass
class FunctionDefinition:
    """Represents a parsed function in a Nature document."""
    name: str                  # Function name (e.g., function_1)
    instructions: str          # The natural language instructions
    generated_code: str        # Python code generated from the instructions

    def __repr__(self):
        return f"FunctionDefinition(name='{self.name}', instructions='''{self.instructions}''')"
