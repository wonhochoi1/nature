# Nature Language

Nature is a natural language programming interface that allows you to write programs in plain English.

## Key Features

- Write programs in plain English
- Automatic translation to executable code
- Simple syntax with function-based structure
- Support for SQL operations, data manipulation, arithmetic operations
- String manipulation and array operations
- Natural language math expressions

## Getting Started

### Prerequisites

- Python 3.7+

### Running an Example

```bash
# Run the demo example
./nature examples/demo.nature

# Try arithmetic operations
./nature examples/calculator.nature

# Try array and string operations
./nature examples/custom.nature
./nature examples/strings.nature
./nature examples/math.nature
```

## Example Programs

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
```

## How It Works

Nature translates natural language into executable operations using pattern matching and rule-based NLP. 

The process involves:
1. Parsing the input file into functions
2. Recognizing the type of operation in each function
3. Executing the appropriate action based on the detected operation

## Documentation

For more detailed information, see the [USAGE.md](USAGE.md) file.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
