# nature/debugger.py
import traceback
from language.parser import llm_debug_suggestion

def run_generated_code(full_code, functions):
    """Executes the generated code. If errors occur, uses the LLM to suggest fixes."""
    try:
        exec(full_code, globals())
    except Exception as e:
        error_message = traceback.format_exc()
        print("An error occurred during execution:")
        print(error_message)
        # For now, we only debug the first function in the list.
        if functions:
            func = functions[0]
            suggestion = llm_debug_suggestion(func.instructions, error_message, func.generated_code)
            print("\nLLM Debug Suggestion:")
            print(suggestion)
        else:
            print("No function context available for debugging.")
