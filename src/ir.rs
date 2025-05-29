use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// Represents a node in our semantic graph
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IRNode {
    pub id: String,
    pub operation: Operation,
    pub dependencies: Vec<String>, // IDs of nodes this depends on
    pub metadata: HashMap<String, String>,
}

/// Represents a semantic operation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum Operation {
    SQLQuery(SQLQueryOp),
    DataTransform(DataTransformOp),
    FileIO(FileIOOp),
    PythonCode(PythonCodeOp),
    RustCode(RustCodeOp),
    Print(PrintOp),
    Return(ReturnOp),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SQLQueryOp {
    pub query: String,
    pub params: Option<Vec<String>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DataTransformOp {
    pub transform_type: String, // e.g., "filter", "map", "groupby"
    pub args: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct FileIOOp {
    pub operation_type: String, // "read" or "write"
    pub path: String,
    pub format: Option<String>, // "csv", "json", etc.
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PythonCodeOp {
    pub code: String,
    pub use_sandbox: bool,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct RustCodeOp {
    pub code: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PrintOp {
    pub value_ref: String, // ID of the node whose value to print
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ReturnOp {
    pub value_ref: String, // ID of the node whose value to return
}

/// The full IR Graph for a nature program
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct IRGraph {
    pub nodes: Vec<IRNode>,
    pub entry_point: String, // ID of the starting node
}

impl IRGraph {
    pub fn new() -> Self {
        IRGraph {
            nodes: Vec::new(),
            entry_point: String::new(),
        }
    }

    pub fn add_node(&mut self, node: IRNode) {
        if self.nodes.is_empty() {
            self.entry_point = node.id.clone();
        }
        self.nodes.push(node);
    }

    /// Convert the IR graph to a JSON representation
    pub fn to_json(&self) -> Result<String, serde_json::Error> {
        serde_json::to_string_pretty(self)
    }

    /// Create an IR graph from JSON
    pub fn from_json(json: &str) -> Result<Self, serde_json::Error> {
        serde_json::from_str(json)
    }
} 