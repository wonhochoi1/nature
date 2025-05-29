use std::env;
use std::fs;
use std::process;
use anyhow::{anyhow, Result};
use tracing::{info, warn, error};

mod interpreter;
mod module_manager;
mod python_executor;
mod ir;
mod graph_executor;
mod translator;

fn main() {
    // Initialize tracing for better logging
    tracing_subscriber::fmt::init();
    
    // Parse command line arguments
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
            error!("Error: {}", e);
            eprintln!("Error: {}", e);
            process::exit(1);
        }
    }
}

fn run_file(file_path: &str) -> Result<()> {
    // Read the nature file content
    let content = fs::read_to_string(file_path)
        .map_err(|e| anyhow!("Failed to read file: {}", e))?;
    
    info!("Translating file: {}", file_path);
    
    // Create our translator
    let translator = translator::Translator::new();
    
    // Translate the nature code to our IR
    let graph = translator.translate(&content)?;
    
    info!("Generated IR graph with {} nodes", graph.nodes.len());
    
    // Create our graph executor
    let executor = graph_executor::GraphExecutor::new();
    
    // Execute the graph
    info!("Executing IR graph");
    let result = executor.execute_graph(&graph)?;
    
    // Print the final result
    info!("Execution complete");
    
    // Print any final results
    println!("{}", result.to_string());
    
    Ok(())
}

// Legacy function for backward compatibility
#[allow(dead_code)]
fn run_file_legacy(file_path: &str) -> Result<()> {
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

    // Use our Python executor
    let python_executor = python_executor::PythonExecutor::new();
    let generated_code = python_executor.execute_with_stdout(&python_script.replace("{}", file_path))?;
    
    // Now use our Rust interpreter to execute the code
    let mut interpreter = interpreter::Interpreter::new();
    
    // Convert any errors from the interpreter to anyhow errors to ensure Send + Sync compatibility
    if let Err(e) = interpreter.execute(&generated_code) {
        return Err(anyhow!("Interpreter error: {}", e));
    }
    
    Ok(())
}