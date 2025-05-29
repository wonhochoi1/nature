use anyhow::{anyhow, Result};
use cached::proc_macro::cached;
use pyo3::prelude::*;
use pyo3::types::{PyDict, PyList};
use std::sync::Arc;
use std::collections::HashMap;
use std::sync::Mutex;

/// Wrapper around PyO3 for safely executing Python code
pub struct PythonExecutor {
    // We'll use a mutex to ensure thread safety when interacting with Python
    context: Arc<Mutex<HashMap<String, PyObject>>>,
}

impl PythonExecutor {
    pub fn new() -> Self {
        PythonExecutor {
            context: Arc::new(Mutex::new(HashMap::new())),
        }
    }

    /// Execute Python code and return the result
    pub fn execute(&self, code: &str) -> Result<String> {
        Python::with_gil(|py| {
            // Execute the code
            let locals = PyDict::new(py);
            
            // Add any context variables to the locals
            let context = self.context.lock().unwrap();
            for (key, value) in context.iter() {
                locals.set_item(key, value.clone_ref(py))?;
            }
            
            match py.run(code, None, Some(locals)) {
                Ok(_) => {
                    // Try to extract any 'result' variable that might have been set
                    if let Some(result) = locals.get_item("result") {
                        if let Ok(string_result) = result.extract::<String>() {
                            return Ok(string_result);
                        }
                    }
                    
                    // If there's no result, just return OK
                    Ok("".to_string())
                }
                Err(e) => {
                    Err(anyhow!("Python execution error: {}", e))
                }
            }
        })
    }

    /// Execute Python code and capture stdout
    pub fn execute_with_stdout(&self, code: &str) -> Result<String> {
        Python::with_gil(|py| {
            // Set up stdout capture
            let sys = py.import("sys")?;
            let io = py.import("io")?;
            let stdout = io.getattr("StringIO")?.call0()?;
            
            // Save original stdout
            let orig_stdout = sys.getattr("stdout")?;
            
            // Redirect stdout
            sys.setattr("stdout", stdout)?;
            
            // Create a clean locals dict
            let locals = PyDict::new(py);
            
            // Add context variables
            let context = self.context.lock().unwrap();
            for (key, value) in context.iter() {
                locals.set_item(key, value.clone_ref(py))?;
            }
            
            // Execute the code
            let result = match py.run(code, None, Some(locals)) {
                Ok(_) => {
                    // Get the captured stdout
                    let captured = stdout.call_method0("getvalue")?;
                    let output = captured.extract::<String>()?;
                    
                    // Check if there's a result variable
                    if let Some(result_var) = locals.get_item("result") {
                        if let Ok(result_str) = result_var.extract::<String>() {
                            if !result_str.is_empty() {
                                return Ok(format!("{}{}", output, result_str));
                            }
                        }
                    }
                    
                    Ok(output)
                }
                Err(e) => {
                    Err(anyhow!("Python execution error: {}", e))
                }
            };
            
            // Restore original stdout
            sys.setattr("stdout", orig_stdout)?;
            
            result
        })
    }
    
    /// Store a value in the Python context
    pub fn set_value(&self, name: &str, value: PyObject) {
        let mut context = self.context.lock().unwrap();
        context.insert(name.to_string(), value);
    }
    
    /// Get a value from the Python context
    pub fn get_value(&self, name: &str) -> Option<PyObject> {
        let context = self.context.lock().unwrap();
        context.get(name).cloned()
    }
    
    /// Call a Python function from the given module with args
    pub fn call_function(&self, module_name: &str, function_name: &str, args: &[&str]) -> Result<String> {
        Python::with_gil(|py| {
            // Import the module
            let module = py.import(module_name)?;
            
            // Get the function
            let function = module.getattr(function_name)?;
            
            // Convert args to Python list
            let py_args = PyList::new(py, args);
            
            // Call the function
            match function.call1((py_args,)) {
                Ok(result) => {
                    // Extract the result
                    if let Ok(string_result) = result.extract::<String>() {
                        Ok(string_result)
                    } else if let Ok(option) = result.extract::<Option<String>>() {
                        Ok(option.unwrap_or_default())
                    } else {
                        Ok(result.repr()?.extract::<String>()?)
                    }
                }
                Err(e) => {
                    Err(anyhow!("Python function error: {}", e))
                }
            }
        })
    }
}

/// Cached function to generate code from instructions using LLM
#[cached(
    type = "cached::SizedCache<String, String>",
    create = "{ cached::SizedCache::with_size(100) }",
    convert = r#"{ instructions.to_string() }"#,
    result = true
)]
pub fn cached_llm_generate_function_code(instructions: &str) -> Result<String> {
    // Create a Python executor to call the existing function
    let executor = PythonExecutor::new();
    
    // Call the existing Python function
    executor.call_function("language.parser", "llm_generate_function_code", &[instructions])
} 