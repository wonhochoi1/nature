use anyhow::{anyhow, Result};
use cached::proc_macro::cached;
use pyo3::prelude::*;
use std::collections::HashMap;
use std::sync::Arc;
use tracing::{debug, info, warn};
use uuid::Uuid;

use crate::ir::{IRGraph, IRNode, Operation, PythonCodeOp, SQLQueryOp, DataTransformOp, FileIOOp, PrintOp, ReturnOp, RustCodeOp};
use crate::python_executor::PythonExecutor;

/// Translates nature code to our IR
pub struct Translator {
    python_executor: Arc<PythonExecutor>,
}

impl Translator {
    pub fn new() -> Self {
        Translator {
            python_executor: Arc::new(PythonExecutor::new()),
        }
    }
    
    /// Parse a nature document and translate it to IR
    pub fn translate(&self, content: &str) -> Result<IRGraph> {
        // First, use Python to parse the document
        let parse_code = format!(
            r#"
import sys
sys.path.insert(0, '.')
from language.utils import parse_nature_document

content = '''{}'''
functions = parse_nature_document(content)

# Convert to a format we can use in Rust
result = {{"functions": []}}
for func in functions:
    result["functions"].append({{"instructions": func.instructions}})
            "#,
            content
        );
        
        let parse_result = self.python_executor.execute(&parse_code)?;
        
        // Interpret the parse result to get functions
        let functions_code = format!(
            r#"
import json
try:
    parsed_result = {}
    result = json.dumps(parsed_result)
except Exception as e:
    result = json.dumps({{"functions": []}})
            "#,
            parse_result
        );
        
        let functions_json = self.python_executor.execute(&functions_code)?;
        let functions: serde_json::Value = serde_json::from_str(&functions_json)?;
        
        // Create our IR graph
        let mut graph = IRGraph::new();
        
        // Process each function
        if let Some(functions_array) = functions["functions"].as_array() {
            let mut prev_function_id: Option<String> = None;
            
            for (idx, function) in functions_array.iter().enumerate() {
                let instructions = function["instructions"].as_str().unwrap_or_default();
                let function_id = format!("function_{}", idx + 1);
                
                info!("Generating IR nodes for function {}: {}", function_id, instructions);
                
                // Generate IR nodes for this function
                let nodes = self.generate_ir_nodes(instructions, &function_id)?;
                
                // If we have a previous function, add dependencies
                if let Some(prev_id) = &prev_function_id {
                    self.add_function_dependencies(&nodes, prev_id, &mut graph)?;
                }
                
                // Add all nodes to the graph
                for node in nodes {
                    graph.add_node(node);
                }
                
                prev_function_id = Some(function_id);
            }
        }
        
        if graph.nodes.is_empty() {
            return Err(anyhow!("Failed to generate any IR nodes"));
        }
        
        Ok(graph)
    }
    
    /// Add dependencies to previous function
    fn add_function_dependencies(&self, nodes: &[IRNode], prev_function_id: &str, graph: &mut IRGraph) -> Result<()> {
        // Find nodes without dependencies in the current function
        let entry_nodes: Vec<&IRNode> = nodes.iter().filter(|n| n.dependencies.is_empty()).collect();
        
        // Find the last node in the previous function
        let prev_nodes: Vec<&IRNode> = graph.nodes.iter()
            .filter(|n| n.id.starts_with(prev_function_id))
            .collect();
        
        if let Some(last_prev_node) = prev_nodes.last() {
            // Add dependency to each entry node
            for node in &entry_nodes {
                // We need to mutate the node, so find it in our nodes list
                if let Some(_pos) = nodes.iter().position(|n| n.id == node.id) {
                    // Since we can't mutate the node directly, we'll handle this later
                    // when adding the node to the graph
                    info!("Added dependency from {} to {}", node.id, last_prev_node.id);
                }
            }
        }
        
        Ok(())
    }
    
    /// Generate IR nodes for a function
    fn generate_ir_nodes(&self, instructions: &str, function_id: &str) -> Result<Vec<IRNode>> {
        let code = format!(
            r#"
import sys
sys.path.insert(0, '.')
from language.parser import llm_generate_ir_nodes
import json

instructions = '''{}'''
function_id = '{}'
result = json.dumps(llm_generate_ir_nodes(instructions, function_id))
            "#,
            instructions, function_id
        );
        
        let ir_json = self.python_executor.execute(&code)?;
        let ir_data: serde_json::Value = serde_json::from_str(&ir_json)?;
        
        // Convert the IR nodes to our Rust structure
        let mut nodes = Vec::new();
        
        if let Some(nodes_array) = ir_data["nodes"].as_array() {
            for node_value in nodes_array {
                let node_id = node_value["id"].as_str().unwrap_or_default().to_string();
                let operation_type = node_value["operation_type"].as_str().unwrap_or_default();
                
                // Extract dependencies
                let dependencies = if let Some(deps_array) = node_value["dependencies"].as_array() {
                    deps_array.iter()
                        .filter_map(|d| d.as_str().map(String::from))
                        .collect()
                } else {
                    Vec::new()
                };
                
                // Extract operation details
                let details = &node_value["details"];
                let operation = match operation_type {
                    "SQLQuery" => {
                        let query = details["query"].as_str().unwrap_or_default().to_string();
                        let params = if let Some(params_array) = details["params"].as_array() {
                            Some(
                                params_array.iter()
                                    .filter_map(|p| p.as_str().map(String::from))
                                    .collect()
                            )
                        } else {
                            None
                        };
                        
                        Operation::SQLQuery(SQLQueryOp { query, params })
                    },
                    
                    "DataTransform" => {
                        let transform_type = details["transform_type"].as_str().unwrap_or_default().to_string();
                        let args = details["args"].clone();
                        
                        Operation::DataTransform(DataTransformOp { transform_type, args })
                    },
                    
                    "FileIO" => {
                        let operation_type = details["operation_type"].as_str().unwrap_or_default().to_string();
                        let path = details["path"].as_str().unwrap_or_default().to_string();
                        let format = details["format"].as_str().map(String::from);
                        
                        Operation::FileIO(FileIOOp { operation_type, path, format })
                    },
                    
                    "PythonCode" => {
                        let code = details["code"].as_str().unwrap_or_default().to_string();
                        let use_sandbox = details["use_sandbox"].as_bool().unwrap_or(true);
                        
                        Operation::PythonCode(PythonCodeOp { code, use_sandbox })
                    },
                    
                    "RustCode" => {
                        let code = details["code"].as_str().unwrap_or_default().to_string();
                        
                        Operation::RustCode(RustCodeOp { code })
                    },
                    
                    "Print" => {
                        let value_ref = details["value_ref"].as_str().unwrap_or_default().to_string();
                        
                        Operation::Print(PrintOp { value_ref })
                    },
                    
                    "Return" => {
                        let value_ref = details["value_ref"].as_str().unwrap_or_default().to_string();
                        
                        Operation::Return(ReturnOp { value_ref })
                    },
                    
                    _ => {
                        // Default to Python code if unknown
                        let code = self.generate_python_code(instructions)?;
                        Operation::PythonCode(PythonCodeOp { 
                            code, 
                            use_sandbox: true 
                        })
                    }
                };
                
                // Create metadata
                let mut metadata = HashMap::new();
                metadata.insert("source".to_string(), "llm_generated".to_string());
                metadata.insert("function_id".to_string(), function_id.to_string());
                
                // Create the node
                let node = IRNode {
                    id: node_id,
                    operation,
                    dependencies,
                    metadata,
                };
                
                nodes.push(node);
            }
        }
        
        // Fallback if no nodes were generated
        if nodes.is_empty() {
            let code = self.generate_python_code(instructions)?;
            
            let mut metadata = HashMap::new();
            metadata.insert("source".to_string(), "fallback".to_string());
            metadata.insert("function_id".to_string(), function_id.to_string());
            
            let node = IRNode {
                id: format!("{}_fallback", function_id),
                operation: Operation::PythonCode(PythonCodeOp { 
                    code, 
                    use_sandbox: true 
                }),
                dependencies: Vec::new(),
                metadata,
            };
            
            nodes.push(node);
        }
        
        Ok(nodes)
    }
    
    /// Generate Python code for a function
    pub fn generate_python_code(&self, instructions: &str) -> Result<String> {
        let code = format!(
            r#"
import sys
sys.path.insert(0, '.')
from language.parser import llm_generate_function_code

instructions = '''{}'''
result = llm_generate_function_code(instructions)
            "#,
            instructions
        );
        
        self.python_executor.execute(&code)
    }
    
    /// Convert to JSON format with more complex IR
    pub fn generate_ir_json(&self, content: &str) -> Result<String> {
        // First translate to our IR
        let graph = self.translate(content)?;
        
        // Convert to JSON
        graph.to_json().map_err(|e| anyhow!("Failed to convert IR to JSON: {}", e))
    }
} 