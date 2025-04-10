use std::collections::HashMap;
use std::error::Error;
use std::process::Command;
use crate::module_manager::{ModuleManager, Value};

pub struct Interpreter {
    module_manager: ModuleManager,
    variables: HashMap<String, Value>,
}

impl Interpreter {
    pub fn new() -> Self {
        Interpreter {
            module_manager: ModuleManager::new(),
            variables: HashMap::new(),
        }
    }

    pub fn execute(&mut self, code: &str) -> Result<(), Box<dyn Error>> {
        // Execute the Python code
        let output = Command::new("python")
            .arg("-c")
            .arg(code)
            .output()?;

        if !output.status.success() {
            let error = String::from_utf8_lossy(&output.stderr);
            return Err(format!("Python execution error: {}", error).into());
        }

        // Print the output
        let stdout = String::from_utf8_lossy(&output.stdout);
        println!("{}", stdout);

        Ok(())
    }

    pub fn evaluate_expression(&mut self, _expr: &str) -> Result<Value, Box<dyn Error>> {
        // TODO: Implement expression evaluation
        Ok(Value::Null)
    }

    pub fn call_function(&mut self, _name: &str, _args: Vec<Value>) -> Result<Value, Box<dyn Error>> {
        // TODO: Implement function calling
        Ok(Value::Null)
    }

    pub fn get_variable(&self, name: &str) -> Option<&Value> {
        self.variables.get(name)
    }

    pub fn set_variable(&mut self, name: String, value: Value) {
        self.variables.insert(name, value);
    }
} 