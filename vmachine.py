# The virtual machine

"""
This file contains the definition of the virtual machine
and provides functions to run the virtual machine code and print the virtual machine code
"""

# memory size of each segment
segment_size = 8192

'''
the simulated memory
pre-allocate to segment_size integers 
each integer will be an instruction or data
we use Harvard structure, each segment has a different memory block. 
pointers pointing to three memory segments 
.text stores the code representation
stack pointer stores the bottom of the stack
.data stores the data for global variables 
'''
text_seg = [0] * segment_size
stack_seg = [0] * segment_size
data_seg = [0] * segment_size

'''
the registers 
for simplicity we only implement one general purpose register rax
and the others are specific purpose registers 
registers description: 
rax: general purpose register
rip: the program counter, pointing to the next instruction to be executed 
rbp: the base pointer of the current stack frame 
rsp: the stack pointer, pointing to the top of the stack 
rzero: always zero 
'''
reg_file = [0, 0, 0, 0, 0]
reg_names = ['rax', 'rip', 'rbp', 'rsp', 'rzero']

'''
the register identifiers for encoding the instructions 
'''
rax = 0
rip = 1
rbp = 2
rsp = 3
rzero = 4

'''
the instructions 
since our virtual machine has only one general purpose register, 
most of the instructions won't require an operand. 

instruction encoding: 
we use a different instruction encoding from real machines 
we reserve the first 16 bits for identifying the instruction type 
the upper bits are operands, each operand can take 8 bits (because we only have 5 registers)

after the operands, there might be immediates, the immediates are infinitely long
'''

''' 
load effective address, lea <reg0>, <imm>(reg1) => <reg0> = <reg1> + <imm>
encoding 
0 - 15 bits: 0000 0000 0000 0000
16 - 23 bits: <reg0>
24 - 31 bits: <reg1>
32+ bits: <imm>
'''
lea = 0


def gen_lea(reg0, reg1, imm):
    encoding = lea
    reg0 = reg0 << 16
    reg1 = reg1 << 24
    imm = imm << 32
    encoding = encoding | reg0 | reg1 | imm
    return encoding


def do_lea(encoding):
    reg0 = (encoding >> 16) & 0xFF
    reg1 = (encoding >> 24) & 0xFF
    imm = (encoding >> 32)
    reg_file[reg0] = reg_file[reg1] + imm
    return


def _print_lea(encoding):
    reg0 = (encoding >> 16) & 0xFF
    reg1 = (encoding >> 24) & 0xFF
    imm = (encoding >> 32)
    print('lea {}, {}({})'.format(reg_names[reg0], imm, reg_names[reg1]))
    return


'''
jump instruction, jmp <addr> => rip = <addr>
0 - 15 bits: 0000 0000 0000 0001
16+ bits: <addr>
'''
jmp = 1


def gen_jmp(addr):
    encoding = jmp
    addr = addr << 16
    encoding = encoding | addr
    return encoding


def do_jmp(encoding):
    addr = encoding >> 16
    reg_file[rip] = addr
    return


def _print_jmp(encoding):
    addr = encoding >> 16
    print('jmp {}'.format(addr))
    return


'''
call instruction, call <addr> => *rsp-- = rip, rip = <addr>
0 - 15 bits: 0000 0000 0000 0010
16+ bits: <addr> 
'''
call = 2


def gen_call(addr):
    encoding = call
    addr = addr << 16
    encoding = encoding | addr
    return encoding


def do_call(encoding):
    addr = encoding >> 16
    stack_seg[reg_file[rsp]] = reg_file[rip]
    reg_file[rsp] = reg_file[rsp] + 1
    reg_file[rip] = addr

    return


def _print_call(encoding):
    addr = encoding >> 16
    print('call {}'.format(addr))
    return


'''
jz / jnz instruction jump if rax is equal / not equal to 0
jz <addr> => rip = (rax == 0) ? (<addr>) : (rip)
jnz <addr> => rip = (rax == 0) ? (rip) ; (<addr>)
'''
jz = 3
jnz = 4


def gen_jz(addr):
    encoding = jz
    addr = addr << 16
    encoding |= addr
    return encoding


def gen_jnz(addr):
    encoding = jnz
    addr = addr << 16
    encoding |= addr
    return encoding


def do_jz(encoding):
    addr = encoding >> 16
    if reg_file[rax] == 0:
        reg_file[rip] = addr


def do_jnz(encoding):
    addr = encoding >> 16
    if reg_file[rax] != 0:
        reg_file[rip] = addr


def _print_jz(encoding):
    print('jz {}'.format(encoding >> 16))


def _print_jnz(encoding):
    print('jnz {}'.format(encoding >> 16))


'''
li / si: load / save integers to stack 
address is at the top of the stack, integer is stored in rax
the address is popped after the operation
'''
li = 5
si = 6


def gen_li():
    return li


def gen_si():
    return si


def do_li(encoding):
    reg_file[rsp] -= 1
    addr = stack_seg[reg_file[rsp]]
    reg_file[rax] = stack_seg[addr]


def do_si(encoding):
    reg_file[rsp] -= 1
    addr = stack_seg[reg_file[rsp]]
    stack_seg[addr] = reg_file[rax]


def _print_li(encoding):
    print('li')


def _print_si(encoding):
    print('si')


'''
lid / sid: the data segment version of li / si
'''
lid = 7
sid = 8


def gen_lid():
    return lid


def gen_sid():
    return sid


def do_lid(encoding):
    reg_file[rsp] = reg_file[rsp] - 1
    addr = stack_seg[reg_file[rsp]]
    reg_file[rax] = data_seg[addr]


def do_sid(encoding):
    reg_file[rsp] = reg_file[rsp] - 1
    addr = stack_seg[reg_file[rsp]]
    data_seg[addr] = reg_file[rax]


def _print_lid(encoding):
    print('lid')


def _print_sid(encoding):
    print('sid')


'''
push: push <reg> to the stack
'''
push = 9


def gen_push(reg):
    encoding = push
    reg = reg << 16
    encoding |= reg
    return encoding


def do_push(encoding):
    reg = (encoding >> 16) & 0xFF
    # print('rsp before push: {}'.format(reg_file[rsp]))
    stack_seg[reg_file[rsp]] = reg_file[reg]
    reg_file[rsp] += 1


def _print_push(encoding):
    reg = (encoding >> 16) & 0xFF
    print('push {}'.format(reg_names[reg]))


'''
pop: pop the top of the stack to <reg>
'''
pop = 10


def gen_pop(reg):
    encoding = pop
    reg = reg << 16
    encoding |= reg
    return encoding


def do_pop(encoding):
    reg = (encoding >> 16) & 0xFF
    reg_file[rsp] -= 1
    reg_file[reg] = stack_seg[reg_file[rsp]]


def _print_pop(encoding):
    reg = (encoding >> 16) & 0xFF
    print('pop {}'.format(reg_names[reg]))


'''
ret: return from subroutine
'''
ret = 11


def gen_ret():
    return ret


def do_ret(encoding):
    reg_file[rsp] -= 1
    reg_file[rip] = stack_seg[reg_file[rsp]]


def _print_ret(encoding):
    print('ret')


'''
orb / xorb / andb / eq / ne / lt / le / gt / ge / shl / shr / add / sub / mul / div / mod
arithmetic instructions
the first operand is at the top of the stack 
the second operand is in rax
note that after the operation, the first operand will be popped 
'''
orb = 12
xorb = 13
andb = 14
eq = 15
ne = 16
lt = 17
le = 18
gt = 19
ge = 20
shl = 21
shr = 22
add = 23
sub = 24
mul = 25
div = 26
mod = 27
notb = 28


def pop_from_stack():
    reg_file[rsp] = reg_file[rsp] - 1
    operand0 = stack_seg[reg_file[rsp]]
    return operand0


def gen_orb():
    return orb


def gen_xorb():
    return xorb


def gen_andb():
    return andb


def gen_eq():
    return eq


def gen_ne():
    return ne


def gen_lt():
    return lt


def gen_le():
    return le


def gen_gt():
    return gt


def gen_ge():
    return ge


def gen_shl():
    return shl


def gen_shr():
    return shr


def gen_add():
    return add


def gen_sub():
    return sub


def gen_mul():
    return mul


def gen_div():
    return div


def gen_mod():
    return mod


def gen_notb():
    return notb


def do_orb(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 | operand1


def do_xorb(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 ^ operand1


def do_andb(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 & operand1


def do_eq(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 == operand1


def do_ne(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 != operand1


def do_lt(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    if operand0 < operand1:
        reg_file[rax] = 1
    else:
        reg_file[rax] = 0
    # reg_file[rax] = int(operand0 < operand1)


def do_le(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 <= operand1


def do_gt(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 > operand1


def do_ge(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 >= operand1


def do_shl(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 << operand1


def do_shr(encoding):
    reg_file[rsp] = reg_file[rsp] - 1
    operand0 = stack_seg[reg_file[rsp]]
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 >> operand1


def do_add(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 + operand1


def do_sub(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 - operand1


def do_mul(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 * operand1


def do_div(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 // operand1


def do_mod(encoding):
    operand0 = pop_from_stack()
    operand1 = reg_file[rax]
    reg_file[rax] = operand0 % operand1


def do_notb(encoding):
    operand0 = pop_from_stack()
    reg_file[rax] = ~operand0


def _print_orb(encoding):
    print('orb')


def _print_xorb(encoding):
    print('xorb')


def _print_andb(encoding):
    print('andb')


def _print_eq(encoding):
    print('eq')


def _print_ne(encoding):
    print('ne')


def _print_lt(encoding):
    print('lt')


def _print_le(encoding):
    print('le')


def _print_gt(encoding):
    print('gt')


def _print_ge(encoding):
    print('ge')


def _print_shl(encoding):
    print('shl')


def _print_shr(encoding):
    print('shr')


def _print_add(encoding):
    print('add')


def _print_sub(encoding):
    print('sub')


def _print_mul(encoding):
    print('mul')


def _print_div(encoding):
    print('div')


def _print_mod(encoding):
    print('mod')


def _print_notb(encoding):
    print('notb')


'''
builtin functions for input / output and exit
'''
inpt = 100
outpt = 200
iexit = 300


def gen_inpt():
    return inpt


def gen_outpt():
    return outpt


def gen_iexit():
    return iexit


def do_inpt(encoding):
    reg_file[rax] = int(input())


def do_outpt(encoding):
    print(stack_seg[reg_file[rsp] - 1])


def do_iexit(encoding):
    pass


def _print_inpt(encoding):
    print('inpt')


def _print_outpt(encoding):
    print('outpt')


def _print_iexit(encoding):
    print('iexit')


def run_vm():
    """
    Run the program according to the code in the text_seg
    :return: None
    """
    while True:
        encoding = text_seg[reg_file[rip]]
        reg_file[rip] += 1
        code = encoding & 0xFFFF
        if code == lea:
            do_lea(encoding)
        elif code == jmp:
            do_jmp(encoding)
        elif code == jz:
            do_jz(encoding)
        elif code == jnz:
            do_jnz(encoding)
        elif code == call:
            do_call(encoding)
        elif code == li:
            do_li(encoding)
        elif code == si:
            do_si(encoding)
        elif code == lid:
            do_lid(encoding)
        elif code == sid:
            do_sid(encoding)
        elif code == push:
            do_push(encoding)
        elif code == pop:
            do_pop(encoding)
        elif code == ret:
            do_ret(encoding)
        elif code == orb:
            do_orb(encoding)
        elif code == xorb:
            do_xorb(encoding)
        elif code == andb:
            do_andb(encoding)
        elif code == eq:
            do_eq(encoding)
        elif code == ne:
            do_ne(encoding)
        elif code == lt:
            do_lt(encoding)
        elif code == le:
            do_le(encoding)
        elif code == gt:
            do_gt(encoding)
        elif code == ge:
            do_ge(encoding)
        elif code == shl:
            do_shl(encoding)
        elif code == shr:
            do_shr(encoding)
        elif code == add:
            do_add(encoding)
        elif code == sub:
            do_sub(encoding)
        elif code == mul:
            do_mul(encoding)
        elif code == div:
            do_div(encoding)
        elif code == mod:
            do_mod(encoding)
        elif code == notb:
            do_notb(encoding)
        elif code == inpt:
            do_inpt(encoding)
        elif code == outpt:
            do_outpt(encoding)
        elif code == iexit:
            print('program exited')
            break
        else:
            print('unknown instruction: {}'.format(code))
            break


def print_text():
    """
    Prints the assembly in text_seg
    :return: None
    """
    line = 0
    for i in text_seg:
        print(line, end='\t')
        encoding = i
        if isinstance(i, str):
            # if the code is not linked, the function calls will just be the callee name itself
            print(i)
            line += 1
            continue
        if i == 0:
            print()
            break
        code = encoding & 0xFFFF
        if code == lea:
            _print_lea(encoding)
        elif code == jmp:
            _print_jmp(encoding)
        elif code == jz:
            _print_jz(encoding)
        elif code == jnz:
            _print_jnz(encoding)
        elif code == call:
            _print_call(encoding)
        elif code == li:
            _print_li(encoding)
        elif code == si:
            _print_si(encoding)
        elif code == lid:
            _print_lid(encoding)
        elif code == sid:
            _print_sid(encoding)
        elif code == push:
            _print_push(encoding)
        elif code == pop:
            _print_pop(encoding)
        elif code == ret:
            _print_ret(encoding)
        elif code == orb:
            _print_orb(encoding)
        elif code == xorb:
            _print_xorb(encoding)
        elif code == andb:
            _print_andb(encoding)
        elif code == eq:
            _print_eq(encoding)
        elif code == ne:
            _print_ne(encoding)
        elif code == lt:
            _print_lt(encoding)
        elif code == le:
            _print_le(encoding)
        elif code == gt:
            _print_gt(encoding)
        elif code == ge:
            _print_ge(encoding)
        elif code == shl:
            _print_shl(encoding)
        elif code == shr:
            _print_shr(encoding)
        elif code == add:
            _print_add(encoding)
        elif code == sub:
            _print_sub(encoding)
        elif code == mul:
            _print_mul(encoding)
        elif code == div:
            _print_div(encoding)
        elif code == mod:
            _print_mod(encoding)
        elif code == notb:
            _print_notb(encoding)
        elif code == inpt:
            _print_inpt(encoding)
        elif code == outpt:
            _print_outpt(encoding)
        elif code == iexit:
            _print_iexit(encoding)
        else:
            print('unknown instruction: {}'.format(code))
            break
        line += 1


# testing the virtual machine
def test_vm():
    text_seg[0] = gen_lea(rax, rzero, 10)
    text_seg[1] = gen_push(rax)
    text_seg[2] = gen_lea(rax, rzero, 20)
    text_seg[3] = gen_mul()
    text_seg[4] = gen_push(rax)
    text_seg[5] = gen_outpt()
    text_seg[6] = gen_iexit()
    run_vm()


if __name__ == '__main__':
    test_vm()
