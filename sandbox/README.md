# Nature Language Web Sandbox

A simple web-based compiler and executor for the Nature language.

## Features

- Write Nature language code in a web interface
- Compile to Python code using OpenAI's API
- Execute the generated code
- View the output and any errors
- View the generated Python code

## Setup and Running

### Using Conda Environment (Recommended)

If you've set up the conda environment using the setup scripts in the project root:

1. Activate the environment:
   ```
   conda activate nature-env
   ```

2. Set your OpenAI API key

3. Run the web server:
   ```
   python app.py
   ```

### Manual Setup

1. Make sure you have the required dependencies installed:
   ```
   pip install flask openai python-dotenv
   ```

2. Set your OpenAI API key using one of the methods described above.

3. Run the web server:
   ```
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

## Example Usage

You can write Nature language code like this:

```
function:
    create an array of numbers from 1 to 10
    calculate the sum of these numbers
    print the result
```

The system will:
1. Parse the natural language instructions
2. Generate Python code using OpenAI's API
3. Execute the code
4. Display the results

## How It Works

1. The web interface sends your Nature code to the server
2. The server uses the Nature language parser to understand the instructions
3. OpenAI's API is used to generate Python code from the natural language
4. The generated code is executed in a sandboxed environment
5. The output, any errors, and the generated Python code are returned to the browser 