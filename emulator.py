from collections import OrderedDict as odict

# watch how spaces or new lines are parsed

DATA_MEM_SIZE = 256
NUM_REG = 16
OVERFLOW = 'overflow'
BRANCH = 'branch'

def truncated(i):
    return i & 0xFF

def int_to_byte(i):
    if i not in range(256):
        raise ValueError('invalid integer')
    return chr(i & 0xFF)

def byte_to_int(byte):
    if len(byte) != 1:
        raise ValueError('invalid byte')
    return ord(byte)

class Register(object): # registers only contain unsigned numbers
    def __init__(self, idx):
        self.idx = idx
        self.value = '\xFF'

    def set(self, byte):
        self.value = byte

    def get(self):
        return self.value

    def idx(self):
        return self.idx

    def inc(self): # register++
        temp = byte_to_int(self.value)
        if temp + 1 >= 256:
            raise ValueError('register inc overflow')
        self.value = int_to_byte(temp + 1)

    def __str__(self):
        return str(byte_to_int(self.value))

def get_named_instruction(name):
    def named_instruction(instruction):
        instruction.name = name
        return instruction
    return named_instruction

def get_instruction_object(instruction):
    class Instruction(object):
        def __init__(self, *args):
            self.args = args
            self.instruction = instruction

        def execute(self):
            return self.instruction(*self.args)
        def __str__(self):
            bit_string = ''
            bit_string += INSTRUCTION_OP[self.instruction.name]

            if self.instruction.name in I_TYPE:
                bit_string += bin(self.args[1])[2:].zfill(4)
            elif self.instruction.name in R_TYPE:
                bit_string += bin(self.args[1].idx)[2:].zfill(4)
            elif self.instruction.name in N_TYPE:
                bit_string += '0000'
            elif self.instruction.name in M_TYPE:
                bit_string += bin(self.args[1].idx)[2:].zfill(4)
            elif self.instruction.name in B_TYPE:
                if (self.args[1] in self.args[2]):
                    l = sorted(self.args[2].keys())
                    bit_string += bin(l.index(self.args[1]))[2:].zfill(4)
                else:
                    raise ValueError('Label, ' + self.args[1] + ' does not exist')
            else:
                raise ValueError('Unknown Type')

            return bit_string

    return Instruction

@get_instruction_object
@get_named_instruction('ASS')
def ass(r0, i): # only assigns nonnegative numbers
    if i not in range(16):
        raise ValueError('invalid immediate')
    r0.set(int_to_byte(i))

@get_instruction_object
@get_named_instruction('MOVF')
def movf(r0, r):
    r0.set(r.get())

@get_instruction_object
@get_named_instruction('MOVT')
def movt(r0, r):
    r.set(r0.get())

@get_instruction_object
@get_named_instruction('ADD')
def add(r0, r):
    result = byte_to_int(r0.get()) + byte_to_int(r.get())
    if result >= 256:
        r0.set(int_to_byte(truncated(result)))
        return OVERFLOW
    r0.set(int_to_byte(result))

@get_instruction_object
@get_named_instruction('ADDI')
def addi(r0, i):
    if i not in range(16):
        raise ValueError('invalid immediate')
    result = byte_to_int(r0.get()) + i
    if result >= 256:
        r0.set(int_to_byte(truncated(result)))
        return OVERFLOW
    r0.set(int_to_byte(result))

@get_instruction_object
@get_named_instruction('SUB')
def sub(r0, r):
    result = byte_to_int(r0.get()) - byte_to_int(r.get())
    if result < 0:
        raise ValueError('subtraction overflow with ' + r0.get() + ' and ' + r.get())
    r0.set(int_to_byte(result))

@get_instruction_object
@get_named_instruction('SUBI')
def subi(r0, i):
    if i not in range(16):
        raise ValueError('invalid immediate')
    result = byte_to_int(r0.get()) - i
    if result < 0:
        raise ValueError('subtraction overflow with ' + r0.get() + ' and ' + str(i))
    r0.set(int_to_byte(result))

@get_instruction_object
@get_named_instruction('NOT')
def bitwise_not(r0):
    r0.set(int_to_byte(byte_to_int(r0.get()) ^ 0xFF))

@get_instruction_object
@get_named_instruction('AND')
def bitwise_and(r0, r):
    r0.set(int_to_byte(byte_to_int(r0.get()) & byte_to_int(r.get())))

@get_instruction_object
@get_named_instruction('OR')
def bitwise_or(r0, r):
    r0.set(int_to_byte(byte_to_int(r0.get()) | byte_to_int(r.get())))

@get_instruction_object
@get_named_instruction('GT')
def gt(r0, r):
    if byte_to_int(r0.get()) > byte_to_int(r.get()):
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('LT')
def lt(r0, r):
    if byte_to_int(r0.get()) < byte_to_int(r.get()):
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('GE')
def ge(r0, r):
    if byte_to_int(r0.get()) >= byte_to_int(r.get()):
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('LE')
def le(r0, r):
    if byte_to_int(r0.get()) <= byte_to_int(r.get()):
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('EQ')
def eq(r0, r):
    if byte_to_int(r0.get()) == byte_to_int(r.get()):
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('LOAD')
def load(r0, r, data_mem):
    r0.set(data_mem[byte_to_int(r.get())].get())

@get_instruction_object
@get_named_instruction('STR')
def store(r0, r, data_mem):
    data_mem[byte_to_int(r.get())].set(r0.get())

@get_instruction_object
@get_named_instruction('CFB')
def cfb(r0):
    fb = byte_to_int(r0.get()) >> 7
    if fb == 1:
        r0.set('\x01')
    else:
        r0.set('\x00')

@get_instruction_object
@get_named_instruction('BEZ')
def bez(r0, i, lookup_table, pc):
    if i not in lookup_table:
        raise ValueError('invalid index for the lookup table')
    addr = lookup_table[i] # addr in binary
    if r0.get() == '\x00':
        pc.set(int_to_byte(addr))
        return BRANCH

@get_instruction_object
@get_named_instruction('BNZ')
def bnz(r0, i, lookup_table, pc):
    if i not in lookup_table:
        raise ValueError('invalid index for the lookup table')
    addr = lookup_table[i] # addr in binary
    if r0.get() != '\x00':
        pc.set(int_to_byte(addr))
        return BRANCH

@get_instruction_object
@get_named_instruction('B')
def b(r0, i, lookup_table, pc):
    if i not in lookup_table:
        raise ValueError('invalid index for the lookup table')
    addr = lookup_table[i] # addr in binary
    pc.set(int_to_byte(addr))
    return BRANCH

@get_instruction_object
@get_named_instruction('LSL')
def lsl(r0, i): # Note - integer is truncated
    if i not in range(8):
        raise ValueError('invalid immediate')
    r0.set(int_to_byte(truncated(byte_to_int(r0.get()) << i)))

@get_instruction_object
@get_named_instruction('LSR')
def lsr(r0, i):
    if i not in range(8):
        raise ValueError('invalid immediate')
    r0.set(int_to_byte(byte_to_int(r0.get()) >> i))

@get_instruction_object
@get_named_instruction('LSLR')
def lslr(r0, r):
    i = byte_to_int(r.get())
    if i not in range(8):
        raise ValueError('invalid register value')
    r0.set(int_to_byte(truncated(byte_to_int(r0.get()) << i)))

@get_instruction_object
@get_named_instruction('LSRR')
def lsrr(r0, r):
    i = byte_to_int(r.get())
    if i not in range(8):
        raise ValueError('invalid register value')
    r0.set(int_to_byte(byte_to_int(r0.get()) >> i))

@get_instruction_object
@get_named_instruction('HALT')
def halt(r0): # r0 unused
    raise Exception('end of program')

@get_instruction_object
@get_named_instruction('GOV')
def get_ov(r0, r):
    r0.set(r.get())

@get_instruction_object
@get_named_instruction('COV')
def clear_ov(r): # r is the overflow register
    r.set(int_to_byte(0))

INSTRUCTION_SET = {
        'ASS': ass,
        'MOVF': movf,
        'MOVT': movt,
        'ADD': add,
        'ADDI': addi,
        'SUB': sub,
        'SUBI': subi,
        'NOT': bitwise_not,
        'AND': bitwise_and,
        'OR': bitwise_or,
        'GT': gt,
        'LT': lt,
        'GE': ge,
        'LE': le,
        'EQ': eq,
        'LOAD': load,
        'STR': store,
        'CFB': cfb,
        'BEZ': bez,
        'BNZ': bnz,
        'B': b,
        'LSL': lsl,
        'LSR': lsr,
        'LSLR': lslr,
        'LSRR': lsrr,
        'HALT': halt,
        'GOV': get_ov,
        'COV': clear_ov,
}


INSTRUCTION_OP = {
        'ASS'           : bin(1)[2:].zfill(5),
        'MOVF'          : bin(2)[2:].zfill(5),
        'MOVT'          : bin(3)[2:].zfill(5),
        'ADD'           : bin(4)[2:].zfill(5),
        'ADDI'          : bin(5)[2:].zfill(5),
        'SUB'           : bin(6)[2:].zfill(5),
        'SUBI'          : bin(7)[2:].zfill(5),
        'NOT'           : bin(8)[2:].zfill(5),
        'AND'           : bin(9)[2:].zfill(5),
        'OR'            : bin(10)[2:].zfill(5),
        'GT'            : bin(11)[2:].zfill(5),
        'LT'            : bin(12)[2:].zfill(5),
        'GE'            : bin(13)[2:].zfill(5),
        'LE'            : bin(14)[2:].zfill(5),
        'EQ'            : bin(15)[2:].zfill(5),
        'LOAD'          : bin(16)[2:].zfill(5),
        'STR'           : bin(17)[2:].zfill(5),
        'CFB'           : bin(18)[2:].zfill(5),
        'BEZ'           : bin(19)[2:].zfill(5),
        'BNZ'           : bin(20)[2:].zfill(5),
        'B'             : bin(21)[2:].zfill(5),
        'LSL'           : bin(22)[2:].zfill(5),
        'LSR'           : bin(23)[2:].zfill(5),
        'LSLR'          : bin(24)[2:].zfill(5),
        'LSRR'          : bin(25)[2:].zfill(5),
        'HALT'          : bin(26)[2:].zfill(5),
        'COV'           : bin(27)[2:].zfill(5),
        'GOV'           : bin(28)[2:].zfill(5),
}

N_TYPE = {
        'NOT',
        'CFB',
        'HALT',
        'COV',
        'GOV',
}

R_TYPE = {
        'MOVF',
        'MOVT',
        'ADD',
        'SUB',
        'AND',
        'OR',
        'GT',
        'GE',
        'LE',
        'LT',
        'EQ',
        'LSLR',
        'LSRR',
}

I_TYPE = {
        'ASS',
        'ADDI',
        'SUBI',
        'LSL',
        'LSR',
}

# M-type is a sub-type of R-type
M_TYPE = {
        'LOAD',
        'STR',
}

# B-type is a sub-type of R-type
B_TYPE = {
        'BEZ',
        'BNZ',
        'B',
}


class Emulator(object):
    def __init__(self):
        self.regs = [Register(i) for i in range(NUM_REG)]
        self.data_mem = [Register(i) for i in range(DATA_MEM_SIZE)]
        self.instr_mem = []
        self.reg_idx_map = None
        self.lookup_table = dict()
        self.pc = Register(-1)
        self.pc.set(int_to_byte(0))
        self.ov = Register(-2)
        self.ov.set(int_to_byte(0))
        self.debug_lines = odict()
        self.mem_min = 0
        self.mem_max = DATA_MEM_SIZE - 1

    def set_mem_range(self, mem_min, mem_max):
        self.mem_min = mem_min
        self.mem_max = mem_max

    def insert_data_mem(self, idx, val):
        self.data_mem[idx].set(int_to_byte(val))

    def create_register_idx_map(self, reg_map):
        self.reg_idx_map = reg_map # requires R0 mapped to index 0

    # Loads Program with the file
    def load_program(self, filename):
        if not self.reg_idx_map:
            raise ValueError('invalid register index map')
        r0 = self.regs[0]
        with open(filename, 'r') as program:
            for line in program:
                line = line.replace('\n', '')
                tokens = line.split(' ')

                # if the entire line is blank, skip it.
                blank_line = True
                for token in tokens:
                    if token != '':
                        blank_line = False
                if blank_line:
                    continue

                # remove any empty tokens
                tokens = [token for token in tokens if token != '']

                # for debug mode
                if tokens[0] == 'DEBUG':
                    self.debug_lines[len(self.instr_mem) - 1] = tokens[1]
                    continue

                # for comments in the assembly codes
                if tokens[0].startswith('#'):
                    continue

                # for labels used by branching
                if tokens[0].startswith('[') and tokens[0].endswith(']:'):
                    self.lookup_table[tokens[0][:-1]] = len(self.instr_mem)
                    continue

                # if encounter invalid instruction
                if tokens[0] not in INSTRUCTION_SET:
                    raise ValueError('unknown instruction: ' + tokens[0])

                instruction = INSTRUCTION_SET[tokens[0]]
                if tokens[0] in I_TYPE:
                    i = int(tokens[1])
                    instruction = instruction(r0, i)
                if tokens[0] in R_TYPE:
                    if tokens[1] not in self.reg_idx_map:
                        raise ValueError('unknown register: ' + tokens[1])
                    r = self.regs[self.reg_idx_map[tokens[1]]]
                    instruction = instruction(r0, r)
                if tokens[0] in N_TYPE:
                    if tokens[0] == 'GOV':
                        instruction = instruction(r0, self.ov)
                    elif tokens[0] == 'COV':
                        instruction = instruction(self.ov)
                    else:
                        instruction = instruction(r0)
                if tokens[0] in M_TYPE:
                    if tokens[1] not in self.reg_idx_map:
                        raise ValueError('unknown register: ' + tokens[1])
                    r = self.regs[self.reg_idx_map[tokens[1]]]
                    instruction = instruction(r0, r, self.data_mem)
                if tokens[0] in B_TYPE:
                    label = tokens[1]
                    instruction = instruction(
                            r0, label, self.lookup_table, self.pc)

                self.instr_mem.append(instruction)


    def print_machine_code(self, filename):
        out = open(filename, "w")
        for r in self.instr_mem:
            out.write(str(r) + '\n')
            print r
        out.close()

    def print_lookup_table(self, filename):
        i = 0
        out = open(filename, 'w')
        for k in sorted(self.lookup_table):
            print k + ': ' + str(i) + ' -> ' + str(self.lookup_table[k])

            out.write("'d" + str(i) + " : data_o = " + str(self.lookup_table[k]) + ';\n')
            i += 1

        for k in range(i, 16):
            out.write("'d" + str(i) + " : data_o = " + str(0) + ';\n')
        out.close()

    def print_memory_state(self):
        for i in range(self.mem_min, self.mem_max + 1):
            print str(i) + ": " + str(self.data_mem[i])
        return self.data_mem[self.mem_min:self.mem_max+1]

    def run_program(self):
        while True:
            try:
                curr_addr = byte_to_int(self.pc.get())
                curr_instr = self.instr_mem[curr_addr]
                ret_val = curr_instr.execute()

                # debug
                if byte_to_int(self.pc.get()) in self.debug_lines:
                    pc_val, r0_val = str(self.pc), str(self.regs[0])
                    info = '(' + self.debug_lines[byte_to_int(self.pc.get())] + ')'
                    print '[' + pc_val + ']: ' + r0_val + ' ' + info

                # handle branching and overflow
                if ret_val != BRANCH:
                    self.pc.inc()
                if ret_val == OVERFLOW:
                    self.ov.set(int_to_byte(1))

            except Exception as e:
                print e
                print '----------------- Memory State ------------------'
                return self.print_memory_state()
