"""
This file is the driver file, it provides a command-line frontend 
Usage: python3 driver.py <file> [Option]
Option: 
    --dump-ast: dumps the AST
    --dump-assembly: dumps the assembly code for the internal virtual machine
    --help: print the help message

If no option specified, it will run the program by default 
"""

import argparse
from codegen import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Toy language interpreter',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('code_file',
                        type=argparse.FileType('r'))

    parser.add_argument('--dump-ast',
                        help='dump the AST',
                        action='store_true',
                        dest='ast_dump')

    parser.add_argument('--dump-assembly',
                        help='dump assembly for the internal virtual machine',
                        action='store_true',
                        dest='assembly_dump')

    args = parser.parse_args()

    lex = Lexer(args.code_file)
    parser = Parser(lex)
    try:
        ast = parser.parse_program()
        check_function_definition(ast)
        check_symbol_definition(ast, symbol_table)
        if args.ast_dump and not args.assembly_dump:
            print(ast)
            exit(0)
        push_instruction('main')  # the entry point is the main function
        push_instruction(gen_iexit())  # when the main function returns, then the program will exit
        generate_code(ast, symbol_table)
        link_function()
        if args.ast_dump:
            print(ast)
        if args.assembly_dump:
            print_text()
        if not args.ast_dump and not args.assembly_dump:
            run_vm()
    except ValueError as err:
        print(err)
        exit(0)
    exit(0)
