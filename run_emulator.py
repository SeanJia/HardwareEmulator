import sys
import emulator

if len(sys.argv) != 2:
  print 'Usage: python run_emulator.py <filename>'
  print '<filename> be in "test" directory'
  exit(1)

filename = sys.argv[1]

mem_min = 0
mem_max = 255

#################### YOU SHOULD ONLY HAVE TO MODIFY THESE ################

# First register is the accumulator
# regs is the list of registers
# data_mem is the dictionary of memory address to data
# mem_min is the minimum memory range to print (inclusive) [optional]
# mem_max is the maximum memory range to print (inclusive) [optional]


if filename == 'test/float2int.txt':
  regs = ['R0', 'I1', 'I2', 'I3', 'I4', 'T1', 'T2', 'M1', 'M2', 'C1', 'C2', 'MSB', 'LSB', 'MOUT', 'LOUT', 'TMP']
  data_mem = {64: 0b11100000, 65: 0b11000001}
  mem_min = 66
  mem_max = 67

elif filename == 'test/int2float.txt':
  regs = ['R0', 'R1', 'R2', 'R3', 'R4', 'T', 'T1', 'T2', 'T3']
  integer = 4097
  integer = bin(integer)[2:].zfill(16)
  int1, int2 = int(integer[:-8], 2), int(integer[-8:], 2)
  print int1, int2
  data_mem = {0: int1, 1: int2}
  mem_min = 5
  mem_max = 6

elif filename == 'test/floatplusfloat.py':
  regs = ['R0', 'R1', 'R2', 'R3', 'R4', 'R5', 'R6', 'R7', 'R8', 'R9', 'R10',
  'R11', 'R12', 'R13', 'R14', 'R15']
  data_mem = {128: 0b00111110, 129: 0b10010110, 130: 0b00111000, 131: 0b00010011}
  mem_min = 132
  mem_max = 133

elif filename == 'test/test.txt':
  regs = ['R0', 'R1']
  data_mem = {0: 0}
  mem_min = 0
  mem_max = 0

else:
  print 'Exiting: Undefined File'
  exit(1)




###########################################################################

e = emulator.Emulator()

# Specify the registers
m = {}
for i in range(0, len(regs)):
  m[regs[i]] = i

for i in data_mem:
  e.insert_data_mem(i, data_mem[i])

e.set_mem_range(mem_min, mem_max)

e.create_register_idx_map(m)
e.load_program(filename)
print '------------------ Machine Code -----------------'
e.print_machine_code('float_add_machine_code_final.txt')
print '------------------ Lookup Table -----------------'
e.print_lookup_table('float_add_lookup_table_final.txt')
print '------------------ Emulator ---------------------'
e.run_program()
