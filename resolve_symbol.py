"""
This file contains the definitions of the symbols and symbol tables
and also contains the functions of resolving the symbols
If the symbol is referenced before definition, an exception will be thrown
Note that our language supports calling a function before the function definition,
we need an extra pass to resolve function symbols independently before the full symbol resolution
"""


from parser import *
from ast import *
from lexer import *


class Symbol:
    """
    Metaclass for symbols
    """

    def __init__(self, name: "str"):
        self.name = name  # symbol name
        self.referenced = 0  # the number of time this symbol is referenced
        self.position = 0  # the memory position of this symbol in the corresponding segment


class FunctionSymbol(Symbol):
    """
    The symbol for functions
    """

    def __init__(self, name: "str", args: '[tuple(arg_name, arg_type)]', return_type: "str"):
        super(FunctionSymbol, self).__init__(name)
        self.args = args  # function arguments
        self.return_type = return_type

    def __str__(self):
        string = self.name
        for arg in self.args:
            string += arg[0] + ' '
        string += str(self.position)
        return '({})'.format(string)


class VariableSymbol(Symbol):
    """
    The symbol for variables
    """

    def __init__(self, name: "str", var_type: "str", is_global: "bool"):
        super(VariableSymbol, self).__init__(name)
        self.type = var_type  # the type of the variable
        self.is_global = is_global  # True if the variable is a global variable

    def __str__(self):
        return '({} {})'.format(self.name, self.position)


class SymbolTable:
    """
    The metaclass for symbol tables
    """

    def __init__(self, parent):
        self.symbols = {}  # a dictionary mapping names to a FunctionSymbol / VariableSymbol
        self.children = {}  # a dictionary mapping names to children symbol tables
        self.parent = parent  # the parent symbol table


class GlobalSymbolTable(SymbolTable):
    """
    The symbol table for global variables and functions
    """

    def __init__(self):
        super(GlobalSymbolTable, self).__init__(None)
        self.symbols = {
            'input': FunctionSymbol('input', [], 'Int'),
            'print': FunctionSymbol('print', [('val', 'Int')], 'Int'),
            'exit': FunctionSymbol('exit', [], 'Int')
        }  # the internal functions: input(), print(val: Int), exit()

    def __str__(self):
        for sym in self.symbols:
            print(sym)
        for child in self.children:
            print('local')
            print(child)
            print('end local')
        return ''


class LocalSymbolTable(SymbolTable):
    """
    The symbol table for local code blocks, functions in this case
    """

    def __init__(self, parent):
        super(LocalSymbolTable, self).__init__(parent)

    def __str__(self):
        for sym in self.symbols:
            print(sym)
        return ''


symbol_table = GlobalSymbolTable()  # this is the symbol table for the program


def check_function_definition(current_ast):
    """
    travel through the AST and read all of the function definitions first
    because this language supports making function call before function declaration
    :param current_ast: the current AST node
    :return: None
    """
    if isinstance(current_ast, GlobalDeclarationAst):
        for func_ast in current_ast.func_declaration:
            check_function_definition(func_ast)  # the functions are all global
    elif isinstance(current_ast, FunctionDeclarationAst):
        if current_ast.name in symbol_table.symbols:
            raise ValueError('semantic error: redefinition of function: {}'.format(current_ast.name))
        current_ast.args.sort()  # sort the arguments, supporting unordered argument passing
        symbol_table.symbols[current_ast.name] = FunctionSymbol(current_ast.name,
                                                                current_ast.args, current_ast.return_type)
        symbol_table.children[current_ast.name] = LocalSymbolTable(symbol_table)
        pass
    else:
        pass


def check_symbol_definition(current_ast, current_symbol_table):
    """
    checks all of the symbol definitions and references
    if a symbol is referenced before definition, it will prompt an error
    function is an exception, it supports function call before definition
    :param current_ast: the current AST node
    :param current_symbol_table: the symbol table of the current context
    :return: None
    """
    if current_ast is None:
        return
    if isinstance(current_ast, BinaryExprAst):
        """
        for BinaryExprAst, just recursively checks its LHS and RHS
        """
        check_symbol_definition(current_ast.lhs, current_symbol_table)
        check_symbol_definition(current_ast.rhs, current_symbol_table)
        pass
    elif isinstance(current_ast, UnaryExprAst):
        """
        for UnaryExprAst, just recursively checks its operand
        """
        check_symbol_definition(current_ast.operand, current_symbol_table)
        pass
    elif isinstance(current_ast, CallExprAst):
        callee = current_ast.callee
        symbol_table_ptr = current_symbol_table
        # find the symbol definition, if it's not defined in the current context, find in the upper context
        while callee not in symbol_table_ptr.symbols:
            if isinstance(symbol_table_ptr, GlobalSymbolTable):
                raise ValueError('semantic error: function ({}) is not defined'.format(callee))
            else:
                symbol_table_ptr = symbol_table_ptr.parent

        symbol = symbol_table_ptr.symbols[callee]
        current_ast.args.sort()  # also sort the arguments to match the order of the function argument definition
        args = current_ast.args
        if len(args) != len(symbol.args):
            raise ValueError('semantic error: '
                             'function {} requires {} arguments, '
                             'but {} arguments are provided'.format(callee, len(symbol.args), len(args)))

        i = 0
        # checks the argument names
        while i < len(args):
            if args[i][0] != symbol.args[i][0]:
                raise ValueError('semantic error: unknown argument: {}'.format(args[i][0]))
            i += 1
        symbol.referenced += 1
        pass
    elif isinstance(current_ast, VariableExprAst):
        symbol_table_ptr = current_symbol_table
        # find the symbol definition, if not in current context, find in the upper context
        while current_ast.name not in symbol_table_ptr.symbols:
            if isinstance(symbol_table_ptr, GlobalSymbolTable):
                raise ValueError('semantic error: variable ({}) is not defined'.format(current_ast.name))
            else:
                symbol_table_ptr = symbol_table_ptr.parent

        symbol_table_ptr.symbols[current_ast.name].referenced += 1
        pass
    elif isinstance(current_ast, NumberExprAst):
        # nothing to do
        pass
    elif isinstance(current_ast, VariableDeclarationAst):
        if current_ast.name in current_symbol_table.symbols:
            raise ValueError('semantic error: redefinition of variable: {}'.format(current_ast.name))

        # we should add variable symbols to the current symbol table when we see a variable declaration
        current_symbol_table.symbols[current_ast.name] = \
            VariableSymbol(name=current_ast.name,
                           var_type=current_ast.type,
                           is_global=isinstance(current_symbol_table, GlobalSymbolTable))
        pass
    elif isinstance(current_ast, FunctionDeclarationAst):
        if not isinstance(current_symbol_table, GlobalSymbolTable):
            raise ValueError('unknown error: function declaration must be in global scope, this is an expected error, '
                             'feel free to report this error to ou2@ualerta.ca')

        # the function symbol has been added to the symbol table
        local_symbol_table = current_symbol_table.children[current_ast.name]
        # add the arguments to the function's local symbol table
        for arg in current_ast.args:
            local_symbol_table.symbols[arg[0]] = VariableSymbol(name=arg[0], var_type=arg[1], is_global=False)

        check_symbol_definition(current_ast.body, current_symbol_table.children[current_ast.name])
        pass
    elif isinstance(current_ast, ReturnStatementAst):
        check_symbol_definition(current_ast.value, current_symbol_table)
        pass
    elif isinstance(current_ast, IfStatementAst):
        check_symbol_definition(current_ast.condition, current_symbol_table)
        check_symbol_definition(current_ast.then_block, current_symbol_table)
        check_symbol_definition(current_ast.else_block, current_symbol_table)
        pass
    elif isinstance(current_ast, WhileStatementAst):
        check_symbol_definition(current_ast.condition, current_symbol_table)
        check_symbol_definition(current_ast.loop_block, current_symbol_table)
        pass
    elif isinstance(current_ast, StatementAst):
        for statement in current_ast.statements:
            check_symbol_definition(statement, current_symbol_table)
        pass
    elif isinstance(current_ast, FunctionBodyAst):
        for var_ast in current_ast.var_declaration:
            check_symbol_definition(var_ast, current_symbol_table)

        for statement in current_ast.statements:
            check_symbol_definition(statement, current_symbol_table)
        pass
    elif isinstance(current_ast, GlobalDeclarationAst):
        for var_ast in current_ast.var_declaration:
            check_symbol_definition(var_ast, current_symbol_table)

        for func_ast in current_ast.func_declaration:
            check_symbol_definition(func_ast, current_symbol_table)
        pass
    else:
        pass


# tests for the functions above
if __name__ == '__main__':
    file = open('test_parser.txt', 'r')
    lex = Lexer(file)
    parser = Parser(lex)
    ast = parser.parse_program()
    check_function_definition(ast)
    check_symbol_definition(ast, symbol_table)
    print(len(symbol_table.children))
    print(symbol_table.children['f'].symbols)
