import sys
import emulator

if len(sys.argv) != 2:
  print 'Usage: python run_emulator.py <filename>'
  print '<filename> be in "./test" directory'
  exit(1)

filename = sys.argv[1]

# First register is reserved for the accumulator;
# 'regs' is the list of registers;
# 'data_mem' is the dictionary of memory address to data;
# 'mem_min' is the minimum memory range to print (inclusive) [optional] after running the input files;
# 'mem_max' is the maximum memory range to print (inclusive) [optional] after running the input files.

regs = ['R0']  # Modify usage of registers here; 'R0' is always included as the accumulator.
data_mem = {}  # A map from memory indices to specific values for that byte (in binary).
mem_min = 0
mem_max = 255  # The default memory size is 256 bytes.

###########################################################################

e = emulator.Emulator()

# Specify the registers
m = {}
for i in range(0, len(regs)):
  m[regs[i]] = i

# Specify the original main memory.
for i in data_mem:
  e.insert_data_mem(i, data_mem[i])

e.set_mem_range(mem_min, mem_max)

e.create_register_idx_map(m)
e.load_program(filename)
print '------------------ Machine Code -----------------'
e.print_machine_code('float_add_machine_code_final.txt')
print '----------Lookup Table (for branching)-----------'
e.print_lookup_table('float_add_lookup_table_final.txt')
print '--------------- Emulator Running-----------------'
e.run_program()
