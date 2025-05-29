use anyhow::{anyhow, Result};
use dashmap::DashMap;
use std::sync::Arc;
use tracing::{debug, info, warn};

use crate::ir::{IRGraph, IRNode, Operation};
use crate::python_executor::PythonExecutor;

/// Stores the result of executing a node
#[derive(Debug, Clone)]
pub enum ExecutionResult {
    String(String),
    Number(f64),
    Boolean(bool),
    Object(serde_json::Value),
    Null,
}

impl ExecutionResult {
    pub fn to_string(&self) -> String {
        match self {
            ExecutionResult::String(s) => s.clone(),
            ExecutionResult::Number(n) => n.to_string(),
            ExecutionResult::Boolean(b) => b.to_string(),
            ExecutionResult::Object(o) => o.to_string(),
            ExecutionResult::Null => "null".to_string(),
        }
    }
}

/// The main executor for our IR Graph
pub struct GraphExecutor {
    python_executor: Arc<PythonExecutor>,
    results: Arc<DashMap<String, ExecutionResult>>,
}

impl GraphExecutor {
    pub fn new() -> Self {
        GraphExecutor {
            python_executor: Arc::new(PythonExecutor::new()),
            results: Arc::new(DashMap::new()),
        }
    }

    /// Execute an entire IR graph
    pub fn execute_graph(&self, graph: &IRGraph) -> Result<ExecutionResult> {
        // Find the entry point
        let entry_node = graph.nodes.iter()
            .find(|node| node.id == graph.entry_point)
            .ok_or_else(|| anyhow!("Entry point not found"))?;
        
        // Execute the entry node and its dependencies
        self.execute_node(entry_node, graph)
    }

    /// Execute a single node in the graph
    pub fn execute_node(&self, node: &IRNode, graph: &IRGraph) -> Result<ExecutionResult> {
        // Check if we already have a result for this node
        if let Some(result) = self.results.get(&node.id) {
            return Ok(result.clone());
        }
        
        // Execute dependencies first
        for dep_id in &node.dependencies {
            let dep_node = graph.nodes.iter()
                .find(|n| &n.id == dep_id)
                .ok_or_else(|| anyhow!("Dependency node not found: {}", dep_id))?;
            
            self.execute_node(dep_node, graph)?;
        }
        
        // Now execute this node
        info!("Executing node: {}", node.id);
        let result = match &node.operation {
            Operation::SQLQuery(op) => {
                // For now, we'll execute SQL via Python
                let code = format!(
                    r#"
import sqlite3
conn = sqlite3.connect('sandbox/database_name.db')
cursor = conn.cursor()
query = """{}"""
cursor.execute(query)
result = str(cursor.fetchall())
conn.close()
                    "#, 
                    op.query
                );
                
                let output = self.python_executor.execute(&code)?;
                ExecutionResult::String(output)
            },
            
            Operation::DataTransform(op) => {
                // For now, use Python for data transforms
                let code = format!(
                    r#"
# This is a placeholder for data transformation
transform_type = "{}"
args = {}
result = f"Transformed data with {{transform_type}}: {{args}}"
                    "#,
                    op.transform_type,
                    op.args
                );
                
                let output = self.python_executor.execute(&code)?;
                ExecutionResult::String(output)
            },
            
            Operation::FileIO(op) => {
                let code = match op.operation_type.as_str() {
                    "read" => format!(
                        r#"
with open('{}', 'r') as f:
    result = f.read()
                        "#,
                        op.path
                    ),
                    "write" => format!(
                        r#"
with open('{}', 'w') as f:
    f.write("Output data")
result = "File written successfully"
                        "#,
                        op.path
                    ),
                    _ => return Err(anyhow!("Unknown file operation: {}", op.operation_type)),
                };
                
                let output = self.python_executor.execute(&code)?;
                ExecutionResult::String(output)
            },
            
            Operation::PythonCode(op) => {
                // Execute the Python code directly
                let output = self.python_executor.execute_with_stdout(&op.code)?;
                ExecutionResult::String(output)
            },
            
            Operation::RustCode(_op) => {
                // In the future, we'll compile and execute Rust code
                // For now, return a placeholder
                ExecutionResult::String("Rust code execution placeholder".to_string())
            },
            
            Operation::Print(op) => {
                // Get the value to print
                let value = self.results.get(&op.value_ref)
                    .ok_or_else(|| anyhow!("Value not found for printing: {}", op.value_ref))?;
                
                // Print the value
                println!("{}", value.to_string());
                
                // Return the same value
                value.clone()
            },
            
            Operation::Return(op) => {
                // Get the value to return
                let value = self.results.get(&op.value_ref)
                    .ok_or_else(|| anyhow!("Value not found for return: {}", op.value_ref))?;
                
                // Return the value
                value.clone()
            },
        };
        
        // Store the result
        self.results.insert(node.id.clone(), result.clone());
        
        Ok(result)
    }
    
    /// Get a stored result by node ID
    pub fn get_result(&self, node_id: &str) -> Option<ExecutionResult> {
        self.results.get(node_id).map(|r| r.clone())
    }
    
    /// Clear all stored results
    pub fn clear_results(&self) {
        self.results.clear();
    }
} 