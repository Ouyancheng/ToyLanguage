# ToyLanguage

### A toy language implemented in Python

Special thanks to @Chaowing for writing driver.py

### Usage
#### Requirement
    Python3 
That's it! No other dependency is required! 
#### Run:
    python3 driver.py <code_file> [-h] [--dump-ast] [--dump-assembly]

#### Required argument:
    <code_file>: the file containing the code you want to run

#### Options:

    --dump-ast: dumps the abstract syntax tree in a very abstract way, only use in debugging, not for users
    
    --dump-assembly: dumps the generated assembly code for the internal virtual machine
    
    --help or -h: prints the help message
    
If no option specified, it will run the code directly.

### Grammar
```
program ::= global_declaration+
global_declaration ::= {variable_declaration}* {function_declaration}*
function_declaration ::= 'func' id '(' id ':' type { ',' id ':' type}* ')' ':' type '{' body_declaration '}'
body_declaration ::= {variable_declaration}* {statement}*

statement ::= if_statement | while_statement | '{' statement* '}' | 'return' expression | expression | 'pass'
if_statement ::= 'if' '(' expression ')' statement {'else' statement}
while_statement ::= 'while' '(' expression ')' statement


expression ::= term expression_tail
expression_tail ::= operator term expression_tail | empty
term ::= unary_expression | num | '(' expression ')' | identifier_expression
identifier_expression ::= id | id '(' id ':' expression {',' id ':' expression}* ')'
unary_expression ::= unary_operator expression

var_declaration ::= 'var' id ':' type

id: [A-Za-z_][A-Za-z0-9_]*
num:
    hexadecimal: 0x[0-9A-Fa-f]+ | 0X[0-9A-Fa-f]+
    octal: 0o[0-7]+ | 0O[0-7]+
    binary: 0b[01]+ | 0B[01]+
    decimal: [0-9]+ 
type: Int

operator_precedence: '*': 100, '/': 100, '%': 100,
                     '+': 90, '-': 90,
                     '<<': 80, '>>': 80,
                     '>': 70, '>=': 70, '<': 70, '<=': 70, '==': 60, '!=': 60,
                     '&': 50, '^': 40, '|': 30, '&&': 20, '||': 10, '=': 1
```

### Note
- Assignment operator = is right-associative. 

### Limitations
- Only supports single file program. 

- Variable declarations must come before any function declarations (for global variables) and statements (for local variables).

- for ... and do ... while ... statements are not supported. Only if and while statements are supported. 

- break and continue keywords are not supported. 

- Only supports integer, but with infinite precision. 

- Two operators putting together will be treated as one operator (mostly undefined). In 1+-2, +- is treated as one operator, but undefined. Please use 1+ -2 instead. 

- Variable initialization on declaration is not supported. 

### Language 
#### function definition 
```
func <function_name>(<argument1_name>: <argument1_type>, <argument2_name>: <argument2_type>...): <return_type> {
    <local_variable_declarations>
    <function_body_statements>
}
```
#### example 
```
func sample(arg1: Int, arg2: Int): Int {
    return !(arg1 + arg2 * -arg2 / arg1 - ~((arg1 & arg2) >> arg2 | arg1)) && (1+2-3)
}
```

#### variable declaration
```
var <variable_name>: <variable_type>
```
#### example
```
var a: Int
```

#### if ... statement
```
if (<condition>) {
    <then_statements>
} else {
    <else_statements>
}

if (<condition>) {
    <then_statements>
} else if (<condition2>) {
    <else_if_statements>
} else {
    <else_statements>
}
```
#### example
```
if (1 > 2) {
    return 0
} else if (1 == 2) {
    return -1
} else {
    return 1
}
```

#### while ... statement
```
while (<condition>) {
    <loop_block>
}
```
#### example
```
while (i > 0) {
    i = i + 1
}
```

#### function call 
```
<callee_name>(<argument1_name>: <argument1_value>, <argument2_name>: <argument2_value>...)
```
#### example
```
sample(arg1: 1, arg2: 2)
or equivalently:
sample(arg2: 2, arg1: 1)
```

#### comments
```
# here is a single-line comment
'multiple line comment'
"this is also a multiple line comment"
```

#### builtin functions 
```
input() # reads an integer from stdin
print(val: Int) # prints an integer to stdout
exit()  # halt the program 
```

### Sample program
```
# the entry point is the main function
func main(): Int {
    'local variable must be at the very first beginning of the function block'
    var n: Int
    n = input()
    print(val: fact(x: n))
}

# calculate the factorial 
func fact(x: Int): Int {
    if (x < 0) {
        return -1
    } else if (x == 0 || x == 1) {
        return 1
    } else {
        return x * fact(x: x-1)
    }
}
```

### Another sample 
```
var globalVariable: Int  # global variable must be in front of all function declarations

func main(): Int {
    globalVariable = 0
    return infLoop()
}

func infLoop(): Int {
    while (1) {
        globalVariable = globalVariable + 1
        if (globalVariable > 10) {
            globalVariable = 0
        }
    }
    return 0
}
```
