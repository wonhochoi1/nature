use std::collections::HashMap;
use std::path::Path;
use std::error::Error;
use std::fs;

#[derive(Debug)]
pub struct ModuleManager {
    global_env: HashMap<String, Module>,
    loaded_modules: Vec<String>,
    module_paths: Vec<String>,
}

#[derive(Debug)]
pub struct Module {
    name: String,
    functions: HashMap<String, Function>,
    variables: HashMap<String, Value>,
}

#[derive(Debug)]
pub struct Function {
    name: String,
    parameters: Vec<String>,
    body: String,
}

#[derive(Debug)]
pub enum Value {
    String(String),
    Number(f64),
    Boolean(bool),
    List(Vec<Value>),
    Function(Function),
    Module(Module),
    Null,
}

impl ModuleManager {
    pub fn new() -> Self {
        ModuleManager {
            global_env: HashMap::new(),
            loaded_modules: Vec::new(),
            module_paths: vec![
                "Lib".to_string(),
                "Modules".to_string(),
            ],
        }
    }

    pub fn load_module(&mut self, name: &str) -> Result<(), Box<dyn Error>> {
        if self.loaded_modules.contains(&name.to_string()) {
            return Ok(());
        }

        // First try to load from module paths
        for path in &self.module_paths {
            let module_path = Path::new(path).join(format!("{}.nature", name));
            if module_path.exists() {
                let content = fs::read_to_string(module_path)?;
                let module = self.parse_module(&content)?;
                self.global_env.insert(name.to_string(), module);
                self.loaded_modules.push(name.to_string());
                return Ok(());
            }
        }

        // If not found in module paths, try to load as a built-in module
        self.load_builtin_module(name)?;
        self.loaded_modules.push(name.to_string());
        Ok(())
    }

    fn parse_module(&self, _content: &str) -> Result<Module, Box<dyn Error>> {
        // TODO: Implement module parsing
        Ok(Module {
            name: "temp".to_string(),
            functions: HashMap::new(),
            variables: HashMap::new(),
        })
    }

    fn load_builtin_module(&mut self, _name: &str) -> Result<(), Box<dyn Error>> {
        // TODO: Implement built-in module loading
        // This would handle modules like 'sqlite3', 'tabulate', etc.
        Ok(())
    }

    pub fn get_module(&self, name: &str) -> Option<&Module> {
        self.global_env.get(name)
    }

    pub fn get_global_env(&self) -> &HashMap<String, Module> {
        &self.global_env
    }
} 