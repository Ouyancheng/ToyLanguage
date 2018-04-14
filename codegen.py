"""
This file contains functions that can generate the target code for our virtual machine
and there's a linking process, which generates correct call instruction for each function call
The target code will be generated in text_seg defined in vmachine.py
"""


from vmachine import *
from resolve_symbol import *
from ast import *

text_seg_ptr = 0  # the pointer pointing to the next empty position in the text segment
data_seg_ptr = 0  # the pointer pointing to the next empty position in the data segment


def push_instruction(instr):
    """
    Push an instruction to the text segment and move the text segment pointer forward by 1
    :param instr: the encoding of the instruction needed to insert
    :return: None
    """
    global text_seg_ptr
    text_seg[text_seg_ptr] = instr
    text_seg_ptr += 1


def generate_code(current_ast, current_symbol_table=symbol_table, var_num=0):
    """
    Generates the target code for the current AST,
    the generated code will be automatically stored in the virtual machine's corresponding segments
    :param current_ast: the current AST needed to generate code
    :param current_symbol_table: the symbol table for the current context
    :param var_num: for function code generation, records the number of local variables inside the function,
    this is used for stack unwinding before the function return
    :return: None, all generated codes are stored in the text segment of the virtual machine
    """
    global text_seg_ptr
    global data_seg_ptr
    if isinstance(current_ast, BinaryExprAst):
        op = current_ast.operator
        if op == '=':
            """
            the assignment 
            we treat the assignment operator to be the same as all other operators 
            and it doesn't return anything (returns some unexpected value)
            using assignment multiple times in one line may cause mistakes 
            please only use assignment at most once inside one line, this is very important
            """
            if isinstance(current_ast.lhs, VariableExprAst):
                # parse assignment
                if current_ast.lhs.name in current_symbol_table.symbols:
                    # local variable
                    """
                    lea rax, <position>(rbp) 
                    push rax 
                    <generated code for expression>
                    si 
                    """
                    position = current_symbol_table.symbols[current_ast.lhs.name].position
                    push_instruction(gen_lea(rax, rbp, position))
                    push_instruction(gen_push(rax))
                    generate_code(current_ast.rhs, current_symbol_table, var_num)
                    push_instruction(gen_si())
                    pass
                elif current_ast.lhs.name in symbol_table.symbols:
                    # global variable
                    """
                    lea rax, <position>
                    push rax
                    <generated code for expression>
                    sid
                    """
                    position = symbol_table.symbols[current_ast.lhs.name].position
                    push_instruction(gen_lea(rax, rzero, position))
                    push_instruction(gen_push(rax))
                    generate_code(current_ast.rhs, current_symbol_table, var_num)
                    push_instruction(gen_sid())
                    pass
                else:
                    raise ValueError('error in codegen: variable {} not found'.format(current_ast.lhs.name))
                pass
            else:
                raise ValueError('rvalue assignment')
            return

        # below is the common binary operations
        """
        <generated code for LHS>
        # note that the result will be saved on rax after running <generated code for LHS> 
        push rax
        <generated code for RHS>
        <operation>
        """
        generate_code(current_ast.lhs, current_symbol_table, var_num)
        push_instruction(gen_push(rax))
        generate_code(current_ast.rhs, current_symbol_table, var_num)
        if op == '*':
            push_instruction(gen_mul())
            pass
        elif op == '/':
            push_instruction(gen_div())
            pass
        elif op == '%':
            push_instruction(gen_mod())
            pass
        elif op == '+':
            push_instruction(gen_add())
            pass
        elif op == '-':
            push_instruction(gen_sub())
            pass
        elif op == '<<':
            push_instruction(gen_shl())
            pass
        elif op == '>>':
            push_instruction(gen_shr())
            pass
        elif op == '>':
            push_instruction(gen_gt())
            pass
        elif op == '>=':
            push_instruction(gen_ge())
            pass
        elif op == '<':
            push_instruction(gen_lt())
            pass
        elif op == '<=':
            push_instruction(gen_le())
            pass
        elif op == '==':
            push_instruction(gen_eq())
            pass
        elif op == '!=':
            push_instruction(gen_ne())
            pass
        elif op == '&':
            push_instruction(gen_andb())
            pass
        elif op == '^':
            push_instruction(gen_xorb())
            pass
        elif op == '|':
            push_instruction(gen_orb())
            pass
        elif op == '&&':
            """
            for && operation we first multiplies the two operand and check whether the result is zero or not 
            """
            push_instruction(gen_mul())
            push_instruction(gen_push(rzero))
            push_instruction(gen_ne())
            pass
        elif op == '||':
            """
            for || operation we first performs a bitwise or and check whether the result is zero or not 
            """
            push_instruction(gen_orb())
            push_instruction(gen_push(rzero))
            push_instruction(gen_ne())
            pass

        pass
    elif isinstance(current_ast, UnaryExprAst):
        """
        <generated code for operand>
        push rax or rzero 
        <operation>
        """
        op = current_ast.operator
        generate_code(current_ast.operand, current_symbol_table, var_num)
        if op == '!':
            push_instruction(gen_push(rzero))
            push_instruction(gen_eq())
            pass
        elif op == '~':
            push_instruction(gen_push(rax))
            push_instruction(gen_notb())
            pass
        elif op == '-':
            push_instruction(gen_push(rzero))
            push_instruction(gen_sub())
            pass
        pass
    elif isinstance(current_ast, CallExprAst):
        """
        for each argument 
            <generated code for the argument value>
            push rax
        
        call <callee>
        lea rsp, -<number of arguments>(rsp)  # stack unwind for arguments 
        """
        for i in range(len(current_ast.args)):
            generate_code(current_ast.args[i][1], current_symbol_table, var_num)
            push_instruction(gen_push(rax))  # push arguments
        text_seg[text_seg_ptr] = current_ast.callee  # call instructions are generated in the next stage
        text_seg_ptr += 1
        push_instruction(gen_lea(rsp, rsp, -len(current_ast.args)))  # stack unwind for arguments
        pass
    elif isinstance(current_ast, VariableExprAst):
        if current_ast.name in current_symbol_table.symbols:
            # local variable
            """
            lea rax, <position>(rbp)
            push rax 
            li 
            """
            position = current_symbol_table.symbols[current_ast.name].position
            push_instruction(gen_lea(rax, rbp, position))
            push_instruction(gen_push(rax))
            push_instruction(gen_li())
            pass
        elif current_ast.name in symbol_table.symbols:
            # global variable
            """
            lea rax, <position>
            push rax
            lid 
            """
            position = symbol_table.symbols[current_ast.name].position
            push_instruction(gen_lea(rax, rzero, position))
            push_instruction(gen_push(rax))
            push_instruction(gen_lid())
            pass
        else:
            raise ValueError('error in codegen: variable declaration for {} not found'.format(current_ast.name))

        pass
    elif isinstance(current_ast, NumberExprAst):
        """
        lea rax, <value>
        """
        push_instruction(gen_lea(rax, rzero, current_ast.value))
        pass
    elif isinstance(current_ast, VariableDeclarationAst):
        if current_symbol_table == symbol_table:
            current_symbol_table.symbols[current_ast.name].position = data_seg_ptr
            data_seg_ptr += 1
        else:
            # local variable
            # we don't generate code for local variable here, we should generate code while parsing FunctionBodyAst
            raise ValueError('error in codegen: local variables are already resolved in function body')
        pass
    elif isinstance(current_ast, FunctionDeclarationAst):
        """
        push rbp
        lea rsp, 0(rbp)
        <generated code for function body> # this also contains the stack unwinding 
        pop rbp
        ret 
        """
        current_symbol_table.symbols[current_ast.name].position = text_seg_ptr
        local_symbol_table = current_symbol_table.children[current_ast.name]
        """
        calculate the position of each parameter, note that the parameters are pushed from left to right 
        """
        for i in range(len(current_ast.args)):
            local_symbol_table.symbols[current_ast.args[i][0]].position = -2 - len(current_ast.args) + i
        push_instruction(gen_push(rbp))
        push_instruction(gen_lea(rbp, rsp, 0))
        generate_code(current_ast.body, current_symbol_table.children[current_ast.name], var_num)
        push_instruction(gen_pop(rbp))
        push_instruction(gen_ret())

        pass
    elif isinstance(current_ast, ReturnStatementAst):
        """
        <generated code for return value>
        lea rsp, -<var_num>(rsp) 
        pop rbp
        ret 
        """
        generate_code(current_ast.value, current_symbol_table, var_num)
        push_instruction(gen_lea(rsp, rsp, -var_num))
        push_instruction(gen_pop(rbp))
        push_instruction(gen_ret())
        pass
    elif isinstance(current_ast, IfStatementAst):
        """
            <condition>
            jz false
            <then_block>
            jmp exit
        false: 
            <else_block>
        exit: 
        """
        generate_code(current_ast.condition, current_symbol_table, var_num)
        jz_false = text_seg_ptr
        text_seg_ptr += 1
        generate_code(current_ast.then_block, current_symbol_table, var_num)
        jmp_exit = text_seg_ptr
        text_seg_ptr += 1
        text_seg[jz_false] = gen_jz(text_seg_ptr)
        generate_code(current_ast.else_block, current_symbol_table, var_num)
        text_seg[jmp_exit] = gen_jmp(text_seg_ptr)
        pass
    elif isinstance(current_ast, WhileStatementAst):
        """
        loop: 
            <condition>
            jz exit
            <loop_block>
            jmp loop
        exit: 
        """
        loop_begin = text_seg_ptr
        generate_code(current_ast.condition, current_symbol_table, var_num)
        jz_exit = text_seg_ptr
        text_seg_ptr += 1
        generate_code(current_ast.loop_block, current_symbol_table, var_num)
        push_instruction(gen_jmp(loop_begin))
        text_seg[jz_exit] = gen_jz(text_seg_ptr)
        pass
    elif isinstance(current_ast, StatementAst):
        for statement in current_ast.statements:
            generate_code(statement, current_symbol_table, var_num)
        pass
    elif isinstance(current_ast, FunctionBodyAst):
        """
        lea rsp, var_num(rsp) # allocate space for local variables 
        <statements>
        lea rsp, -var_num(rsp) # stack unwind for local variables 
        """
        var_num = len(current_ast.var_declaration)
        push_instruction(gen_lea(rsp, rsp, var_num))
        for i in range(var_num):
            current_symbol_table.symbols[current_ast.var_declaration[i].name].position = i

        for statement in current_ast.statements:
            generate_code(statement, current_symbol_table, var_num)

        push_instruction(gen_lea(rsp, rsp, -var_num))
        pass
    elif isinstance(current_ast, GlobalDeclarationAst):
        for i in range(len(current_ast.var_declaration)):
            generate_code(current_ast.var_declaration[i], current_symbol_table, var_num)

        for i in range(len(current_ast.func_declaration)):
            generate_code(current_ast.func_declaration[i], current_symbol_table, var_num)
        pass
    else:
        pass


def link_function():
    """
    Links every function call to the real function address
    :return: None
    """
    for i in range(len(text_seg)):
        if text_seg[i] == 0:
            return
        if isinstance(text_seg[i], str):
            if text_seg[i] == 'print':
                text_seg[i] = gen_outpt()
                continue
            elif text_seg[i] == 'input':
                text_seg[i] = gen_inpt()
                continue
            elif text_seg[i] == 'exit':
                text_seg[i] = gen_iexit()
                continue
            text_seg[i] = gen_call(symbol_table.symbols[text_seg[i]].position)


# tests for code generation
if __name__ == '__main__':
    file = open('test_parser.txt', 'r')
    lex = Lexer(file)
    parser = Parser(lex)
    ast = parser.parse_program()
    print(ast)  # prints the ast
    # below are generating the target code
    check_function_definition(ast)
    check_symbol_definition(ast, symbol_table)
    push_instruction('main')
    push_instruction(gen_iexit())
    generate_code(ast, symbol_table)
    link_function()
    # up to now the target code is generated
    print_text()  # prints the assembly
    run_vm()  # runs the program
