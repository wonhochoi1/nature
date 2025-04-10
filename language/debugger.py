# language/debugger.py
import traceback
from language.parser import llm_debug_suggestion

def run_generated_code(full_code, functions):
    """
    Executes the generated code in a shared globals environment.
    Each function call is wrapped so that if an error occurs, the user is prompted
    whether to see debugging suggestions from the LLM.
    """
    # Create a dedicated dictionary for globals, including a shared context.
    exec_globals = {"global_context": {}}
    try:
        exec(full_code, exec_globals)
    except Exception as e:
        error_message = traceback.format_exc()
        print("An error occurred during execution:")
        print(error_message)
        
        # Try to identify which function failed based on the error message
        failed_func = None
        for func in functions:
            if func.name in error_message:
                failed_func = func
                break
        
        # If we couldn't identify the failed function, use the last one
        # (since errors often occur in later functions that depend on earlier ones)
        if failed_func is None and functions:
            failed_func = functions[-1]
        
        if failed_func:
            suggestion = llm_debug_suggestion(failed_func.instructions, error_message, failed_func.generated_code)
            print("\nLLM Debug Suggestion:")
            print(suggestion)
            
            # Now, prompt the user interactively to see if they want more debugging help:
            choice = input("Would you like further debugging suggestions? (Y/n): ").strip().lower()
            if choice in ("y", "yes", ""):
                # Offer suggestions for each function
                for func in functions:
                    print(f"\nLLM Debug Suggestion for {func.name}:")
                    suggestion = llm_debug_suggestion(func.instructions, error_message, func.generated_code)
                    print(suggestion)
                    
                    # Ask if they want to see suggestions for the next function
                    if func != functions[-1]:
                        continue_choice = input("See suggestions for next function? (Y/n): ").strip().lower()
                        if continue_choice not in ("y", "yes", ""):
                            break