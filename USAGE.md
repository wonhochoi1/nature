# Using the Nature Language

## Prerequisites

This project requires Python 3.7+ with SQLite support (included in standard Python installations).

## Running Nature Programs

You can run Nature programs directly with the `nature` script:

```bash
./nature examples/demo.nature
```

The script will parse and execute your Nature code, handling all the necessary setup automatically.

## Creating Your Own Programs

Nature programs consist of functions that describe operations. Here are some examples:

### SQL Operations

```
function:
    create a SQL table called "Books" with an id, title, and price
    add a book called "1987" for $4.44
    add a book called "Learning Geology" for $24
    return this table
function:
    print the table in function before this one
```

### Arithmetic Operations

```
function:
    return 100 * 5 + 20 / 2
function:
    return (300 + 5) * 2
```

### Natural Language Math

```
function:
    calculate the square root of 16
function:
    calculate 5 times 8 plus 2 divided by 2
```

### Array Operations

```
function:
    print an array of 10-19
function:
    count from 1 to 5
```

### String Operations

```
function:
    reverse the string hello
function:
    uppercase the string nature language
function:
    lowercase the string PROGRAMMING
```

Save your program with a `.nature` extension and run it with the `./nature` command.

## How It Works

The `nature` script is a Python script that:
1. Parses the Nature file into functions
2. Uses pattern matching and rule-based NLP to understand instructions
3. Executes each function based on the detected operation type
4. Handles common operations like SQL, arithmetic, arrays, and strings

This implementation works reliably without requiring any external API keys or special setup.

## Supported Operations

Currently, the Nature language supports:
- Creating SQL tables
- Adding data to tables
- Querying tables
- Printing results
- Basic arithmetic operations (+, -, *, /, parentheses)
- Natural language math (e.g., "calculate 5 times 8")
- Array generation and counting
- String manipulation (reverse, uppercase, lowercase)

More operations will be added in future versions.

## Troubleshooting

If you encounter any errors:

1. Make sure you're using Python 3.7 or newer
2. Check your Nature syntax to make sure it follows the examples
3. For complex tasks, break them down into simpler functions 