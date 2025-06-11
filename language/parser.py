# nature/parser.py
import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from typing import List
from .ast import FunctionDefinition

# Load environment variables from .env file
load_dotenv()

# Get the API key and verify it exists
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set. Please check your .env file.")

# Initialize OpenAI client with the API key
client = OpenAI(api_key=api_key)

def llm_generate_function_code(nl_instructions):
    prompt = f"""
You are an expert programmer. Convert the following natural language function instructions into a valid Python code snippet that implements them. 
Do not include the function definition line (i.e. "def function_1():") or extra commentary—just the body code indented as needed. and take care of all imports.

Important rules:
1. For SQL operations:
   - Always use proper connection handling with try/finally
   - Return query results before closing connections
   - Use proper string quotes for SQL statements
   - Include proper error handling

2. For function interactions:
   - When one function needs to use another function's result, use return statements
   - Don't just print results - return them so other functions can use them
   - Handle the global_context properly

3. General rules:
   - Include all necessary imports
   - Use proper indentation
   - Handle errors appropriately
   - Return values instead of just printing them

Example 1 (SQL):
  create a SQL table called "Books" with an id, title, and price
  add a book called "1987" for $4.44
  add a book called "Learning Geology" for $30
  return this table

Output:
    import sqlite3
    conn = sqlite3.connect(':memory:')
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE Books (
            id INTEGER PRIMARY KEY,
            title text,
            price real
        )''')
        c.execute("INSERT INTO Books VALUES (1, '1987', 4.44)")
        c.execute("INSERT INTO Books VALUES (2, 'Learning Geology', 30)")
        conn.commit()
        c.execute("SELECT * FROM Books")
        return c.fetchall()
    finally:
        conn.close()

Example 2 (Function Interaction):
Input:
  print the table from function_1

Output:
    print(function_1())
Now, produce the Python code for the function:
{nl_instructions}
"""
    try:
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0)
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
        response = client.chat.completions.create(model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7)
        suggestion = response.choices[0].message.content.strip()
        return suggestion
    except Exception as e:
        print("Error during LLM debugging suggestion:", e)
        return "Could not generate debugging suggestion."
