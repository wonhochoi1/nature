# nature/ast.py

class FunctionDefinition:
    def __init__(self, instructions, name):
        self.instructions = instructions  # The natural language instructions
        self.name = name                  # Function name (e.g., function_1)
        self.generated_code = None        # Python code generated from the instructions

    def generate_code(self, llm_generate_function_code):
        # Calls the LLM-based parser to obtain the function's body code.
        self.generated_code = llm_generate_function_code(self.instructions)
        return self.generated_code

    def __repr__(self):
        return f"FunctionDefinition(name='{self.name}', instructions='''{self.instructions}''')"
