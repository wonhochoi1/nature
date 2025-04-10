use std::env;
use std::process::{self, Command};

mod interpreter;
mod module_manager;

fn main() {
    let args: Vec<String> = env::args().collect();
    
    if args.len() != 2 {
        eprintln!("Usage: nature <file.nature>");
        process::exit(1);
    }
    
    let file_path = &args[1];
    if !file_path.ends_with(".nature") {
        eprintln!("Error: File must have .nature extension");
        process::exit(1);
    }
    
    match run_file(file_path) {
        Ok(_) => (),
        Err(e) => {
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    }
}

fn run_file(file_path: &str) -> Result<(), Box<dyn std::error::Error>> {
    // First, use Python to parse and generate code
    let python_script = r#"
import os
import sys

# Add the current directory to Python path
sys.path.insert(0, os.getcwd())

# Import the functions we need
from language.utils import parse_nature_document
from language.parser import llm_generate_function_code
from language.code_generator import generate_document_code

# Read and process the file
with open('{}', 'r') as f:
    content = f.read()

# Parse the document
functions = parse_nature_document(content)

# Generate code for each function
for func in functions:
    func.generated_code = llm_generate_function_code(func.instructions)

# Generate the final code
generated_code = generate_document_code(functions)
print(generated_code)
"#;

    // Run Python script to get generated code
    let output = Command::new("python")
        .arg("-c")
        .arg(python_script.replace("{}", file_path))
        .output()?;

    if !output.status.success() {
        let error = String::from_utf8_lossy(&output.stderr);
        return Err(format!("Python error: {}", error).into());
    }

    let generated_code = String::from_utf8(output.stdout)?;
    
    // Now use our Rust interpreter to execute the code
    let mut interpreter = interpreter::Interpreter::new();
    interpreter.execute(&generated_code)?;
    
    Ok(())
}