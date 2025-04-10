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

5. Install Rust (if not already installed):
   ```
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

6. Build the Nature binary:
   ```
   cargo build --release
   ```

7. Install the Nature command:
   ```
   ./install.sh
   ```

### Manual Installation

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set your OpenAI API key as above

3. Install Rust and build the binary as described above

## Usage

### Running a Nature File

The simplest way to run a Nature file is using the `nature` command:

```
nature examples/demo.nature
```

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

## Examples

You can find example Nature code in the `examples/` directory. Here's a simple example:

```nature
function:
    create a SQL table called "Books" with an id, title, and price
    add a book called "1987" for $4.44
    add a book called "Learning Geology" for $30
    return this table
function:
    print the table from function_1
```

## Development

### Building from Source

1. Make sure you have Rust installed
2. Clone the repository
3. Build the release version:
   ```
   cargo build --release
   ```
4. The binary will be available at `target/release/nature`

### Project Structure

- `language/`: Python implementation for parsing and code generation
- `src/`: Rust implementation for the runtime environment
- `examples/`: Example Nature files
- `sandbox/`: Web interface for testing
