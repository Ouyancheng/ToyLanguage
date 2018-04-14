"""
This file contains some basic definitions of the language, such keywords, operators and internal types
"""

"""
token classifications
"""

Num, Id, Func, Else, If, Int, Return, While, Assign, Var, Break, Continue, Extern, Pass, \
Orb, Andb, Xorb, Notb, \
Or, And, Not, Eq, Ne, Lt, Gt, Le, Ge, \
Shl, Shr, Add, Sub, Mul, Div, Mod, \
Character = range(35)

"""
the reserved words
"""
reserved_words = {
    'func': Func,
    'else': Else,
    'if': If,
    'Int': Int,
    'return': Return,
    'while': While,
    # 'break': Break,
    # 'continue': Continue,
    'var': Var,
    'pass': Pass
}

"""
the operators
"""
operators = {
    '!': Not,
    '!=': Ne,
    '==': Eq,
    '|': Orb,
    '&': Andb,
    '^': Xorb,
    '||': Or,
    '&&': And,
    '<': Lt,
    '<=': Le,
    '>': Gt,
    '>=': Ge,
    '<<': Shr,
    '>>': Shl,
    '+': Add,
    '-': Sub,
    '*': Mul,
    '/': Div,
    '%': Mod,
    '=': Assign,
    '~': Notb
}

"""
the types
"""
types = {
    'Int': Int
}

"""
set of characters for hexadecimal
"""
hex_set = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
           'A', 'B', 'C', 'D', 'E', 'F',
           'a', 'b', 'c', 'd', 'e', 'f'}
"""
set of characters for octal 
"""
oct_set = {'0', '1', '2', '3', '4', '5', '6', '7'}
"""
set of characters for binary
"""
bin_set = {'0', '1'}

"""
set of characters for operators 
"""
operator_character_set = {'=', '<', '>', '!', '&', '^', '+', '-', '*', '/', '%', '|', '~'}

"""
the precedence of the operators 
"""
operator_precedence = {'*': 100, '/': 100, '%': 100,
                       '+': 90, '-': 90,
                       '<<': 80, '>>': 80,
                       '>': 70, '>=': 70, '<': 70, '<=': 70, '==': 60, '!=': 60,
                       '&': 50, '^': 40, '|': 30, '&&': 20, '||': 10, '=': 1}
"""
unary operator set 
"""
unary_operator = {'!', '~', '-'}
