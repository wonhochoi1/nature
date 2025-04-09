# Nature

A natural language based coding language.

## About Nature

Nature is a proof of concept for a natural language programming language that:

- Accepts blocks of natural language instructions (e.g., functions starting with "function:" followed by verb-led commands)
- Uses OpenAI's API to understand and convert natural language to valid Python code
- Generates runnable Python code from natural language instructions
- Provides a REPL and file-based workflow (with .nature extension)
- Catches runtime errors and guides users with AI-powered suggestions

## Installation

### Using Conda (Recommended)

1. Clone this repository
2. Run the setup script to create a conda environment with all dependencies:

   **On macOS/Linux:**
   ```
   chmod +x setup_conda_env.sh
   ./setup_conda_env.sh
   ```

   **On Windows:**
   ```
   setup_conda_env.bat
   ```

3. Activate the environment:
   ```
   conda activate nature-env
   ```

4. Set your OpenAI API key:
   
   **On macOS/Linux:**
   ```
   export OPENAI_API_KEY=your_api_key_here
   ```
   
   **On Windows:**
   ```
   set OPENAI_API_KEY=your_api_key_here
   ```

### Manual Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as above

## Usage

### Web Sandbox

The sandbox provides a web interface to test Nature code:

```
cd sandbox
python app.py
```

Then open your browser to http://localhost:5000

### Command Line REPL

```
python -m language.repl
```

### Running a Nature File

```
python -m language.repl path/to/your/file.nature
```

## Examples

You can find example Nature code in the `examples/` directory.
