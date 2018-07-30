"""
This file contains the definition of the parser and its helper functions
The parser can convert the token stream to a structured abstract syntax tree (AST) according to the grammar

BNF:
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

"""

from lexer import *
from ast import *
from language_basis import *


def match(token: 'Int', lexer: 'Lexer') -> 'throws ValueError':
    """
    Match a specific type of classification of the next token, if match, it returns the value of the token
    otherwise it will throw a ValueError
    :param token: the classification of the expected token, note that it's not the value
                    for matching the value of the token, please use the match_val function
    :param lexer: the lexer you want to get token from
    :return: the value of the matched token, or raise ValueError if mismatch
    """
    if lexer.current_token.classification == token:
        token = lexer.current_token
        lexer.next_token()
        return token.value
    else:
        raise ValueError('Token mismatch, expected: {}, got: {}'.format(token, lexer.current_token.value))


def match_val(token_val: 'str', lexer: 'Lexer') -> 'throws ValueError':
    """
    Match a specific value of the next token, if match, it returns the value of the token
    otherwise it will throw a ValueError
    :param token_val: the value of the token needed to match, this is a string
    :param lexer: the lexer you want to get token from
    :return: the value of the matched token, if mismatch, it will throw a ValueError
    """
    if lexer.current_token.value == token_val:
        token = lexer.current_token
        lexer.next_token()
        return token.value
    else:
        raise ValueError('Token value mismatch, expected: {}, got: {}'.format(token_val, lexer.current_token.value))


class Parser:
    """
    The parser class, it needs a lexer as the member and
    invoke the parse_program method to convert the whole program to an AST
    """

    def __init__(self, lexer):
        self.lexer = lexer  # the lexer you want to get tokens from
        self.text_ptr = 0  # the pointer pointing to the text segment, not used currently

    def parse_number_expression(self, parent: "None") -> 'throws ValueError':
        """
        Parse the number expression, which is just the number literal
        :param parent: should be the parent of the generated AST node, but not used this time
        :return: NumberExprAst if no error, otherwise it will throw ValueError
        """
        if self.lexer.current_token.classification != Num:
            raise ValueError('error in parsing: expected a number but got {}'.format(self.lexer.current_token.value))
        else:
            number_ast = NumberExprAst(None, self.lexer.current_token.value)
            self.lexer.next_token()  # eat number
            return number_ast

    def parse_variable_expression(self, parent: 'None') -> 'throws ValueError':
        """
        Parse the variable expression, which is just the variable reference
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: VariableExprAst if no error, otherwise it will throw ValueError
        """
        if self.lexer.current_token.classification != Id:
            raise ValueError(
                'error in parsing: expected an identifier but got {}'.format(self.lexer.current_token.value))
        else:
            variable_ast = VariableExprAst(None, self.lexer.current_token.value)
            self.lexer.next_token()
            return variable_ast

    def parse_unary_expression(self, parent: 'None') -> 'throws ValueError':
        """
        unary_expression ::= unary_op term
        Parse the unary expression, such as -a, ~1, !(f(x: 1) + a * 2)
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: UnaryExprAst if no error, otherwise it will throw ValueError
        """
        if self.lexer.current_token.value in unary_operator:
            op = self.lexer.current_token.value
            self.lexer.next_token()  # eat operator
            operand = self.parse_expression(None, min_priority=101)
            unary_ast = UnaryExprAst(None, op, operand)
            return unary_ast
        else:
            raise ValueError(
                'error in parsing: expected an unary operator but got {}'.format(self.lexer.current_token.value))

    def parse_identifier_expression(self, parent: 'None') -> 'throws ValueError':
        """
        identifier_expression ::= id | id '(' id ':' expression {',' id ':' expression}* ')'
        Parse the identifier expression, including function calls and variable references
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: CallExprAst if a function call is detected, VariableExprAst if the identifier reference is detected
        or throws ValueError if token mismatch
        """
        identifier = match(Id, self.lexer)
        if self.lexer.current_token.value == '(':
            # function call
            self.lexer.next_token()  # eat (
            args = []
            while self.lexer.current_token.value != ')':
                arg_name = match(Id, self.lexer)
                match_val(':', self.lexer)
                arg_val = self.parse_expression(None)
                args.append((arg_name, arg_val))
                if self.lexer.current_token.value == ',':
                    self.lexer.next_token()

            self.lexer.next_token()  # eat )

            return CallExprAst(None, identifier, args)
        else:
            # variable reference
            return VariableExprAst(None, identifier)

    def parse_term(self, parent: 'None') -> 'throws ValueError':
        """
        term ::= number_expression | identifier_expression | '(' expression ')' | unary_expression
        Parse the term, which could be a number, a variable reference, a function call, a parenthesis expression,
        or a unary operation
        :param parent: should be the parent of the generated AST node, but not used currently
        :return: NumberExprAst | ExprAst | CallExprAst | VariableExprAst | UnaryExprAst depending on the routine
        or throws ValueError if there's an error
        """
        if self.lexer.current_token.classification == Num:
            return self.parse_number_expression(parent)
        elif self.lexer.current_token.classification == Id:
            return self.parse_identifier_expression(parent)
        elif self.lexer.current_token.value == '(':
            self.lexer.next_token()  # eat (
            expr_ast = self.parse_expression(None)
            match_val(')', self.lexer)
            return expr_ast
        elif self.lexer.current_token.value in unary_operator:
            return self.parse_unary_expression(None)
        else:
            raise ValueError('error in parsing: expected term, got: {}'.format(self.lexer.current_token.value))

    def parse_expression(self, parent, min_priority: 'Int' = 0) -> 'throws ValueError':
        """
        expression ::= term expression_tail
        Parse the expression
        :param parent: should be the parent of the generated AST node, but currently not used
        :param min_priority: the minimum precedence that this function can parse,
        this is essential to operator precedence analysis
        :return: BinaryExprAst if no error, or will throw ValueError if there's an error
        """
        lhs = self.parse_term(None)
        expr_ast = self.parse_expression_tail(parent, lhs, min_priority)
        return expr_ast

    def parse_expression_tail(self, parent: 'None', lhs: 'Ast', min_precedence: 'Int') -> 'throws ValueError':
        """
        expression_tail ::= op expression_tail | empty
        Parsing the expression tail according to the precedence.
        :param parent: should be the parent of the generated AST node, but currently not used
        :param lhs: the left hand side of the current expression
        :param min_precedence: the minimum precedence that this function can parse,
        if the precedence of the next operator is lower than the min_precedence, then this function would return
        if the precedence of the next operator is higher than the min_precedence,
        then the function will be recursively called in order to generate the AST according to the precedence
        :return: BinaryExprAst if no error, or will throw ValueError if there's an error
        """
        while self.lexer.current_token.value in operators: 
            operator_priority = operator_precedence.get(self.lexer.current_token.value)
            if operator_priority is None:
                raise ValueError('error in parsing: unknown operator')
            if operator_priority < min_precedence:
                # if the next operator precedence is less than min_precedence, then this function should return,
                # leaving the next operator to the upper level function to parse. 
                # this is necessary because parse_unary_expression requires this
                break

            op = self.lexer.current_token.value
            self.lexer.next_token()  # eat operator
            rhs = self.parse_term(None)  # parse the right hand side, it may be the left hand side of the next operator
            next_operator_priority = operator_precedence.get(self.lexer.current_token.value)
            if next_operator_priority is None:
                expr_ast = BinaryExprAst(None, op, lhs, rhs)  # complete parsing
                return expr_ast
            if op != '=': 
                # the priority check is not actually necessary since we already have it above. 
                # but this reduces the recursion layer by 1. 
                if next_operator_priority > operator_priority:
                    # left-associative operator
                    # if the next precedence is larger than the current precedence,
                    # the current right hand side should be bound to the next operator as the left hand side
                    rhs = self.parse_expression_tail(None, rhs, operator_priority + 1)
            else: 
                # the priority check is not necessary, we already have it. 
                if next_operator_priority >= operator_priority:
                    # right-associative operator
                    # if the next precedence is larger than OR EQUAL TO the current precedence,
                    # the current right hand side should be bound to the next operator as the left hand side
                    # it is important that the minimum priority is actually the operator_priority, 
                    # otherwise it will be terminated by the operator precedence check above. 
                    rhs = self.parse_expression_tail(None, rhs, operator_priority)
            lhs = BinaryExprAst(None, op, lhs, rhs)

        return lhs

        # below is the tail recursion version. 

        # if self.lexer.current_token.value not in operators:
        #     # parsing complete
        #     return lhs

        # operator_priority = operator_precedence.get(self.lexer.current_token.value)
        # if operator_priority is None:
        #     raise ValueError('error in parsing: unknown operator')
        # if operator_priority < min_precedence:
        #     # if the next operator precedence is less than min_precedence, then this function should return,
        #     # leaving the next operator to the upper level function to parse. 
        #     # this is necessary because parse_unary_expression requires this
        #     return lhs

        # op = self.lexer.current_token.value
        # self.lexer.next_token()  # eat operator
        # rhs = self.parse_term(None)  # parse the right hand side, it may be the left hand side of the next operator
        # next_operator_priority = operator_precedence.get(self.lexer.current_token.value)
        # if next_operator_priority is None:
        #     expr_ast = BinaryExprAst(None, op, lhs, rhs)  # complete parsing
        #     return expr_ast
        # if op != '=': 
        #     # the priority check is not actually necessary since we already have it above. 
        #     # but this reduces the recursion layer by 1. 
        #     if next_operator_priority > operator_priority:
        #         # left-associative operator
        #         # if the next precedence is larger than the current precedence,
        #         # the current right hand side should be bound to the next operator as the left hand side
        #         rhs = self.parse_expression_tail(None, rhs, operator_priority + 1)
        # else: 
        #     # the priority check is not necessary, we already have it. 
        #     if next_operator_priority >= operator_priority:
        #         # right-associative operator
        #         # if the next precedence is larger than OR EQUAL TO the current precedence,
        #         # the current right hand side should be bound to the next operator as the left hand side
        #         # it is important that the minimum priority is actually the operator_priority, 
        #         # otherwise it will be terminated by the operator precedence check above. 
        #         rhs = self.parse_expression_tail(None, rhs, operator_priority)

        # expr_ast = BinaryExprAst(None, op, lhs, rhs)
        # return self.parse_expression_tail(None, expr_ast, min_precedence)

    # def parse_assignment(self, parent):
    #     name = match(Id, self.lexer)
    #     match_val('=', self.lexer)
    #     value = self.parse_expression(None)
    #     return VariableAssignmentAst(None, name, value)

    def parse_variable_declaration(self, parent: 'None') -> 'throws ValueError':
        """
        variable_declaration ::= 'var' id ':' type
        Parse the variable declaration
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: VariableDeclarationAst if no error, or throws ValueError if there's an error
        """
        match(Var, self.lexer)
        name = match(Id, self.lexer)
        match_val(':', self.lexer)
        if self.lexer.current_token.value not in types:
            raise ValueError('error in parsing: expecting type, got {}'.format(self.lexer.current_token.value))
        var_type = self.lexer.current_token.value
        self.lexer.next_token()  # eat type
        # if self.lexer.current_token.value == '[':
        #     array_size = int(match(Num, self.lexer))
        #     match_val(']', self.lexer)
        #     return VariableDeclarationAst(None, name, var_type, is_array=True, array_size=array_size)
        return VariableDeclarationAst(None, name, var_type)

    def parse_if_statement(self, parent: 'None') -> 'throws ValueError':
        """
        if_statement ::= 'if' '(' expression ')' statement {'else' statement}
        Parse the if statement
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: IfStatementAst if there's no error, or throws ValueError if there's an error
        """
        match(If, self.lexer)
        match_val('(', self.lexer)
        condition = self.parse_expression(None)
        match_val(')', self.lexer)
        then_block = self.parse_statement(None)
        if self.lexer.current_token.classification != Else:
            return IfStatementAst(None, condition, then_block, None)
        self.lexer.next_token()  # eat else
        else_block = self.parse_statement(None)
        return IfStatementAst(None, condition, then_block, else_block)

    def parse_while_statement(self, parent: 'None') -> 'throws ValueError':
        """
        while_statement ::= 'while' '(' expression ')' statement
        Parse the while statement
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: WhileStatementAst if there's no error, or throws ValueError if there's an error
        """
        match(While, self.lexer)
        match_val('(', self.lexer)
        condition = self.parse_expression(None)
        match_val(')', self.lexer)
        loop_block = self.parse_statement(None)
        return WhileStatementAst(None, condition, loop_block)

    def parse_statement(self, parent: 'None') -> 'throws ValueError':
        """
        statement ::= if_statement | while_statement | '{' {statement}* '}' | return_statement | 'pass' | expression
        Parse statement, including if, while, statement block, return, pass, and expression
        Note that an assignment is also an expression
        :param parent: should be the parent of the generated AST node, but not used currently
        :return: StatementAst, which contains a list of statements, or throws ValueError if there's an error
        """
        statements = []
        if self.lexer.current_token.classification == If:
            statement = self.parse_if_statement(None)
            statements.append(statement)
            return StatementAst(None, statements)
        elif self.lexer.current_token.classification == While:
            statement = self.parse_while_statement(None)
            statements.append(statement)
            return StatementAst(None, statements)
        elif self.lexer.current_token.value == '{':
            self.lexer.next_token()  # eat {
            while self.lexer.current_token.value != '}':
                # print(self.lexer.current_token.value)
                statement = self.parse_statement(None)
                statements.append(statement)
            self.lexer.next_token()  # eat }
            return StatementAst(None, statements)
        elif self.lexer.current_token.classification == Return:
            self.lexer.next_token()  # eat return
            value = self.parse_expression(None)
            statements.append(ReturnStatementAst(None, value))
            return StatementAst(None, statements)
        elif self.lexer.current_token.classification == Pass:
            self.lexer.next_token()  # eat pass
            return None
        else:
            return self.parse_expression(None)

    def parse_function_declaration(self, parent: 'None') -> 'throws ValueError':
        """
        function_declaration ::= 'func' id '(' id ':' type {',' id ':' type}* ')' '{' body_declaration '}'
        Parse function declaration
        :param parent: should be the parent of the generated node, but currently not used
        :return: FunctionDeclarationAst if no error, or throws ValueError if there's an error
        """
        match(Func, self.lexer)
        name = match(Id, self.lexer)
        match_val('(', self.lexer)
        args = []  # [ (arg_name, arg_type) ]
        while self.lexer.current_token.value != ')':
            arg_name = match(Id, self.lexer)
            match_val(':', self.lexer)
            if self.lexer.current_token.value in types:
                arg_type = self.lexer.current_token.value
                self.lexer.next_token()
                args.append((arg_name, arg_type))
            else:
                raise ValueError('unrecognized type')
            if self.lexer.current_token.value == ',':
                self.lexer.next_token()  # eat ,
        self.lexer.next_token()  # eat )
        match_val(':', self.lexer)
        if self.lexer.current_token.value not in types:
            raise ValueError('unrecognized type')
        return_type = self.lexer.current_token.value
        self.lexer.next_token()
        match_val('{', self.lexer)
        function_body = self.parse_body_declaration(None)
        match_val('}', self.lexer)
        return FunctionDeclarationAst(None, name, args, return_type, function_body)

    def parse_body_declaration(self, parent: 'None') -> 'throws ValueError':
        """
        body_declaration ::= {variable_declaration}* {statement}*
        Parse the function body
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: FunctionBodyAst if there's no error, or throws ValueError if there's an error
        """
        var_decl = []
        statements = []
        while self.lexer.current_token.classification == Var:
            var_ast = self.parse_variable_declaration(None)
            var_decl.append(var_ast)

        while self.lexer.current_token.value != '}':
            statement = self.parse_statement(None)
            statements.append(statement)

        return FunctionBodyAst(None, var_decl, statements)

    def parse_global_declaration(self, parent: 'None') -> 'throws ValueError':
        """
        global_declaration ::= {variable_declaration}* {function_declaration}*
        Parse the global declaration, consisting of variable declarations and function declarations
        Note that the variable declarations always come before the function declarations
        :param parent: should be the parent of the generated AST node, but currently not used
        :return: GlobalDeclarationAst if no error, or throws ValueError if there's an error
        """
        var_decl = []
        func_decl = []
        while self.lexer.current_token is not None and self.lexer.current_token.classification == Var:
            # print('var')
            var_ast = self.parse_variable_declaration(None)
            var_decl.append(var_ast)

        while self.lexer.current_token is not None:
            func_ast = self.parse_function_declaration(None)
            func_decl.append(func_ast)

        return GlobalDeclarationAst(None, var_decl, func_decl)

    def parse_program(self) -> 'throws ValueError':
        """
        Parse the program
        This is the entry of the parser
        :return: GlobalDeclarationAst if no error, or throws ValueError if there's an error
        """
        return self.parse_global_declaration(None)


if __name__ == '__main__':
    file = open('test_parser.txt', 'r')
    lex = Lexer(file)
    parser = Parser(lex)
    ast = parser.parse_program()
    print(ast)
