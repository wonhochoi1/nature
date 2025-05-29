## Staged Hybrid

### Graph 1: GPT -> Python -> Rust

- Natural-Language Understanding: One LLM call turns the full user prompt into runnable Python. The model must resolve intent, references, and APIs in one shot.

- Intermediate IR: Implicit – the generated Python is the IR; any optimisation is left to the Python runtime.

- Runtime & Libraries: Python standard + PyPI, executed from Rust via an embedded CPython (e.g. PyO3) or by spawning an external Python process.	

- Context Management: Mostly delegated to Python variables inside the generated script; references like “previous table” must be encoded in the prompt so GPT emits correct variable names.	

### Graph 2: Intent -> Semantic Graph -> Executor

- Natural Language Understanding: A lighter “intent analysis” stage (can still be an LLM) outputs a structured IR (semantic graph). Knowledge-base look-ups refine that IR.

- Intermediate Representation: Explicit semantic graph: nodes = operations, edges = dataflow. Lets you reason about safety, optimise, or re-order steps before code runs.

- Runtime & Libraries: Native Rust code (or Rust wrappers around C/SQL/etc.). External libraries must be exposed through Rust crates or FFI.

- Context Management: Central Rust data-store tracks every step’s outputs; later IR nodes can formally reference them. Easier to guarantee correctness.

### ROADMAP

Embed CPython from Rust with PyO3; you get safe ownership semantics and can share Rust memory if needed 
pyo3.rs
GitHub

Cache every generated script so subsequent runs avoid extra LLM cost/latency.

Introduce a low-level IR (Graph 2’s semantic graph) behind the scenes:

Prompt GPT not for raw Python but for a JSON array of operations.

Convert that IR either to Python (MVP path) or to native Rust routines when you implement them – you can switch per node.

This lets you migrate hot paths (e.g., data transforms) from Python to Rust crate implementations for speed, one op at a time.

Gradually replace Python for core domains (DB queries, file I/O, data-frame math) with Rust or SQL back-ends.

You keep Python as a “last-mile” escape-hatch for niche libraries until Rust coverage is good enough.