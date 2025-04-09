# nature/parser.py
import os
import json
from dotenv import load_dotenv
import openai

load_dotenv()

openai.api_key = os.environ.get("OPENAI_API_KEY")

def llm_generate_function_code(nl_instructions):
    prompt = f"""
You are an expert programmer. Convert the following natural language function instructions into a valid Python code snippet that implements them. 
Do not include the function definition line (i.e. "def function_1():") or extra commentary—just the body code indented as needed.

Example:

Input: 
  create an array of numbers from 1-4
  sort this array

Output (example):
    numbers = list(range(1, 5))
    numbers.sort()
    print(numbers)

Now, produce the Python code for the function:
{nl_instructions}
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        code = response.choices[0].message.content.strip()
        return code
    except Exception as e:
        print("Error during function code generation:", e)
        return "# Error generating code"

def llm_debug_suggestion(nl_instructions, error_message, generated_code):
    prompt = f"""
You have received the following natural language function instructions:

{nl_instructions}

The generated Python code was:
{generated_code}

However, when running the code an error occurred:
{error_message}

What do you think might be wrong? Ask clarifying questions for details or suggest a correction. Respond in plain text.
"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        print("Error during LLM debugging suggestion:", e)
        return "Could not generate debugging suggestion."
