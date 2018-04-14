"""
This file contains the definitions of the nodes of the abstract syntax tree
"""


def print_array(arr):
    """
    Prints the content of a list
    :param arr: a list that needed to be printed
    :return: the string needed to print
    """
    string = ''
    for a in arr:
        string += str(a) + ' '
    return string.strip(' ')


class Ast:
    def __init__(self, parent):
        self.parent = parent


class BinaryExprAst(Ast):
    def __init__(self, parent: 'None', operator: 'str', lhs: 'Ast', rhs: 'Ast'):
        super(BinaryExprAst, self).__init__(parent)
        self.operator = operator
        self.lhs = lhs
        self.rhs = rhs

    def __str__(self):
        return '({}, {}, {})'.format(self.operator, self.lhs, self.rhs)


class UnaryExprAst(Ast):
    def __init__(self, parent: 'None', operator: 'str', operand: 'Ast'):
        super(UnaryExprAst, self).__init__(parent)
        self.operator = operator
        self.operand = operand

    def __str__(self):
        return '({} {})'.format(self.operator, self.operand)


class CallExprAst(Ast):
    def __init__(self, parent: 'None', callee: 'str', args: 'list[ tuple(arg_name: str, arg_val: Ast) ]'):
        super(CallExprAst, self).__init__(parent)
        self.callee = callee
        self.args = args

    def __str__(self):
        return '({} {})'.format(self.callee, print_array(self.args))


class VariableExprAst(Ast):
    def __init__(self, parent: 'None', name: 'str'):
        super(VariableExprAst, self).__init__(parent)
        self.name = name

    def __str__(self):
        return self.name


class NumberExprAst(Ast):
    def __init__(self, parent: 'None', value: 'int'):
        super(NumberExprAst, self).__init__(parent)
        self.value = value

    def __str__(self):
        return '{}'.format(self.value)


class VariableDeclarationAst(Ast):
    def __init__(self, parent: 'None', name: 'str', var_type: 'str'):
        super(VariableDeclarationAst, self).__init__(parent)
        self.name = name
        self.type = var_type

    def __str__(self):
        return '(var {}:{})'.format(self.name, self.type)


class FunctionDeclarationAst(Ast):
    def __init__(self, parent: 'None', name: 'str',
                 args: 'list[ tuple(arg_name:str, arg_type:str) ]',
                 return_type: 'str',
                 body: 'FunctionBodyAst'):
        super(FunctionDeclarationAst, self).__init__(parent)
        self.name = name
        self.args = args
        self.return_type = return_type
        self.body = body

    def __str__(self):
        return '({}({})->{} {})'.format(self.name, print_array(self.args), self.return_type, self.body)


class ReturnStatementAst(Ast):
    def __init__(self, parent: 'None', value: 'Ast'):
        super(ReturnStatementAst, self).__init__(parent)
        self.value = value

    def __str__(self):
        return '(return {})'.format(self.value)


class IfStatementAst(Ast):
    def __init__(self, parent: 'None', condition: 'Ast', then_block: 'StatementAst', else_block: 'StatementAst'):
        super(IfStatementAst, self).__init__(parent)
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

    def __str__(self):
        return '(if {} {} {})'.format(self.condition, self.then_block, self.else_block)


class WhileStatementAst(Ast):
    def __init__(self, parent: 'None', condition: 'Ast', loop_block: 'StatementAst'):
        super(WhileStatementAst, self).__init__(parent)
        self.condition = condition
        self.condition.parent = condition
        self.loop_block = loop_block

    def __str__(self):
        return '(while {} {})'.format(self.condition, self.loop_block)


class StatementAst(Ast):
    def __init__(self, parent: 'None',
                 statements: '[Ast]'):
        super(StatementAst, self).__init__(parent)
        self.statements = statements

    def __str__(self):
        return '{}'.format(print_array(self.statements))


class FunctionBodyAst(Ast):
    def __init__(self, parent: 'None',
                 var_declaration: '[VariableDeclarationAst]', statements: '[StatementAst]'):
        super(FunctionBodyAst, self).__init__(parent)
        self.var_declaration = var_declaration
        self.statements = statements

    def __str__(self):
        return '({} {})'.format(print_array(self.var_declaration), print_array(self.statements))


class GlobalDeclarationAst(Ast):
    def __init__(self, parent: 'None',
                 var_declaration: '[VariableDeclarationAst]', func_declaration: '[FunctionDeclarationAst]'):
        super(GlobalDeclarationAst, self).__init__(parent)
        self.var_declaration = var_declaration
        self.func_declaration = func_declaration

    def __str__(self):
        return '({} {})'.format(print_array(self.var_declaration), print_array(self.func_declaration))
