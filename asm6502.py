# 
# asm6502.py V1.R1.M0
#
# This file is part of the asm6502 distribution.
# Copyright (c) 2022 James Salvino.
# 
# This program is free software: you can redistribute it and/or modify  
# it under the terms of the GNU General Public License as published by  
# the Free Software Foundation, version 3.
#
# This program is distributed in the hope that it will be useful, but 
# WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU 
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License 
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

import asm6502Mod as fn
import re
import sys
from collections import OrderedDict


label_dict = {}
pc = 0
pass1_error_count = 0
pass2_error_count = 0
code_dict = OrderedDict()


address_mode_patterns_sym = {
    '\#[0-9A-Z]{1,8}': 'Immediate', '[0-9A-Z+-]{1,8}': ('Zero Page', 'Absolute'), 
    '[0-9A-Z]{1,8},X': ('Zero Page,X', 'Absolute,X'), '[0-9A-Z]{1,8},Y': ('Zero Page,Y', 'Absolute,Y'),  
    '\([0-9A-Z]{1,8}\)': 'Indirect', '\([0-9A-Z]{1,8},X\)': 'Indirect,X', '\([0-9A-Z]{1,8}\),Y': 'Indirect,Y'
}


relative_address_mode_instructions = {
    'BPL': '10', 'BMI': '30', 'BVC': '50', 'BVS':'70', 
    'BCC': '90', 'BCS': 'B0', 'BNE': 'D0', 'BEQ': 'F0'
}


def pass1_error_check(t, a, o):
    global pass1_error_count
    if o == 'XX':
        pass1_error_count += 1
        if a == 'Invalid':
            print('Error:', t[1], ' - Invalid Operand')
        else:
            print('Error:', t[0], ' - Invalid Mnemonic for the specified Addressing Mode')
    return


if len(sys.argv) < 2:
    print('usage: asm6502.py <inputsourcefile>')
    exit(3)

finame = sys.argv[1]

print(45*'*')
print('*  JLS 6502 Assembler', 21*' ', '*')
print('*  Copyright (c) 2022 James Salvino.', 6*' ', '*')
print(45*'*')

# pass 1
with open(finame) as sfi:
    source_code = [l.rstrip('\n') for l in sfi]

for line in source_code:
    # ignore blank lines
    if len(line) == 0 or line.isspace():
        continue
    else:
        token_line = fn.tokenize_sl(line)
        # detect lines with just comments in them
        if len(token_line) == 0:
            continue

    if (token_line[0] not in fn.valid_mnemonic_table) and (token_line[0] not in fn.valid_directive_table):
    # not in the valid mnemonic and directive tables, then it must be a LABEL
        label = token_line.pop(0)
        label_dict[label] = fn.i2h(pc, 4)

    if len(token_line) == 2 and token_line[1].startswith('#'):
    # handle different types of immediate operands: #$0A, #128, #'C', #%00001111
        if token_line[1][1].isdigit():
            token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][1:]), 2)
        elif token_line[1][1] == "'":
            token_line[1] = '#' + '$' + fn.i2h(ord(token_line[1][2:3]), 2)
        elif token_line[1][1] == "%":
            token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][2:],2), 2)
            
    if token_line[0] == '.ORG':
        pc = int(token_line[1][1:],16)
    elif token_line[0] == '.DB':
        num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
        pc = pc + num_data_bytes
    elif token_line[0] == '.DS':
        pc = pc + int(token_line[1])
    elif token_line[0] == '.EQU':
        num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
        label_dict[label] = data_bytes
    elif token_line[0] == '.END':
        if pass1_error_count == 0:
            print('Pass 1 Complete - No Errors Encountered')
        else:
            print('Pass 1 Complete - ', pass1_error_count, 'Error(s) Encountered')
        print(' ')
        break
    # handle Relative Address Mode Instructions    
    elif token_line[0] in relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token_line[1]) != None:
        pc = pc + 2
    else:
        if len(token_line) == 2:
            oper = token_line[1]
            if not '$' in oper:
                for p in address_mode_patterns_sym.keys():
                    z = re.fullmatch(p, oper)
                    if z != None:
                        mode = address_mode_patterns_sym[p]
                        if isinstance(mode, tuple):
                            if 'Zero Page' in mode:
                                label = oper
                            elif 'Zero Page,X' in mode:
                                label = oper.rstrip(',X')
                            elif 'Zero Page,Y' in mode:
                                label = oper.rstrip(',Y')
                        else:
                            if mode == 'Indirect':
                                label = oper.lstrip('(').rstrip(')')
                            elif mode == 'Indirect,X':
                                label = oper.lstrip('(').rstrip(',X)')
                            elif mode == 'Indirect,Y':
                                label = oper.lstrip('(').rstrip('),Y')
                            elif mode == 'Immediate':   
                                label = oper.lstrip('#')
                        # handle arithmetic in symbolic label
                        z = re.search('[0-9+-]{2,4}', label)
                        if z != None:
                            f, t = z.span()
                            label = label[0:f]
                        if label in label_dict:
                            oper = '$' + label_dict[label]
                        else:
                            oper = '$FFFF'
                            label_dict[label] = oper
                        if isinstance(mode, tuple):
                            if 'Zero Page,X' in mode:
                                oper = oper + ',X'
                            elif 'Zero Page,Y' in mode:
                                oper = oper + ',Y'
                        else:
                            if mode == 'Indirect':
                                oper = '(' + oper + ')'
                            elif mode == 'Indirect,X':
                                oper = '(' + oper + ',X)'
                            elif mode == 'Indirect,Y':
                                oper = '(' + oper + '),Y'
                            elif mode == 'Immediate':   
                                oper = '#' + oper                            
                        break
                        
            am, nb, oc = fn.determine_mode(token_line[0], oper)
            pass1_error_check(token_line, am, oc)
        elif len(token_line) == 1:
            am, nb, oc = fn.determine_mode(token_line[0], '')
            pass1_error_check(token_line, am, oc)
        else:
            pass1_error_count += 1
            print('Error on:', token_line, ' - Too Many Tokens')
                
        pc = pc + nb    

#print(label_dict)

if pass1_error_count > 0:
    print('Error(s) Encountered')
    print('Unable to Continue')
    exit(1)


# pass 2
lstfiname = finame.split('.')[0] + '.lst' 
lstout = open(lstfiname, 'w')

for line in source_code:
    # ignore blank lines
    if len(line) == 0 or line.isspace():
        print(line)
        lstout.write(line + '\n') 
        continue
    else:
        token_line = fn.tokenize_sl(line)
        # detect lines with just comments in them
        if len(token_line) == 0:
            print(line)
            lstout.write(line + '\n') 
            continue        

    if (token_line[0] not in fn.valid_mnemonic_table) and (token_line[0] not in fn.valid_directive_table):
    # not in the valid mnemonic and directive tables, then it must be a LABEL
        label = token_line.pop(0)

    if len(token_line) == 2 and token_line[1].startswith('#'):
    # handle different types of immediate operands: #$0A, #128, #'C', #%00001111
        if token_line[1][1].isdigit():
            token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][1:]), 2)
        elif token_line[1][1] == "'":
            token_line[1] = '#' + '$' + fn.i2h(ord(token_line[1][2:3]), 2)
        elif token_line[1][1] == "%":
            token_line[1] = '#' + '$' + fn.i2h(int(token_line[1][2:],2), 2)

    if token_line[0] == '.ORG':
        pc = int(token_line[1][1:],16)
        lineout = fn.myprint(line, 'pc =', pc)
        lstout.write(lineout)   
    elif token_line[0] == '.DB':
        num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
        lineout = fn.myprint(line, fn.i2h(pc, 4), ':', data_bytes)
        lstout.write(lineout)   
        code_dict[fn.i2h(pc, 4)] = data_bytes
        pc = pc + num_data_bytes
    elif token_line[0] == '.DS':
        lineout = fn.myprint(line, fn.i2h(pc, 4), ':', 'Reserved', token_line[1], 'Bytes')
        lstout.write(lineout)   
        pc = pc + int(token_line[1])
    elif token_line[0] == '.EQU':
        num_data_bytes, data_bytes = fn.build_data_bytes(token_line[1])
        lineout = fn.myprint(line, label, '=', data_bytes)
        lstout.write(lineout)   
    elif token_line[0] == '.END':
        lineout = fn.myprint(line, fn.i2h(pc, 4))
        lstout.write(lineout)   
        print(' ')
        if pass2_error_count == 0:
            print('Pass 2 Complete - No Errors Encountered')
        else:
            print('Pass 2 Complete - ', pass2_error_count, 'Error(s) Encountered')
        print(' ')
        print('Assembly Complete')
        break
    # handle Relative Address Mode Instructions    
    elif token_line[0] in relative_address_mode_instructions and re.fullmatch('[0-9A-Z]{1,8}', token_line[1]) != None:
        oc = relative_address_mode_instructions[token_line[0]]
        x = int(label_dict[token_line[1]], 16) - pc
        if x > 127 or x < -128:
            pass2_error_count += 1
            print('Error on:', token_line, ' - Relative Displacment Out of Range')
        else:
            if x < 0:
                disp = fn.cvtint2scomp(x-2)
            else:    
                disp = hex(x-2)[2:].zfill(2)
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc, disp)
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc + disp             
            pc = pc + 2
    else:
        if len(token_line) == 2:
            oper = token_line[1]
            if not '$' in oper:
                for p in address_mode_patterns_sym.keys():
                    z = re.fullmatch(p, oper)
                    if z != None:
                        mode = address_mode_patterns_sym[p]
                        if isinstance(mode, tuple):
                            if 'Zero Page' in mode:
                                label = oper
                            elif 'Zero Page,X' in mode:
                                label = oper.rstrip(',X')
                            elif 'Zero Page,Y' in mode:
                                label = oper.rstrip(',Y')
                        else:
                            if mode == 'Indirect':
                                label = oper.lstrip('(').rstrip(')')
                            elif mode == 'Indirect,X':
                                label = oper.lstrip('(').rstrip(',X)')
                            elif mode == 'Indirect,Y':
                                label = oper.lstrip('(').rstrip('),Y')
                            elif mode == 'Immediate':   
                                label = oper.lstrip('#')
                        # handle arithmetic in symbolic label
                        z = re.search('[0-9+-]{2,4}', label)
                        if z != None:
                            f, t = z.span()
                            exp = label[f:t]
                            label = label[0:f]
                            lab_len = len(label_dict[label])
                            x = eval(str(int(label_dict[label], 16)) + exp)
                            if lab_len == 2 and x < 256:
                                oper = '$' + fn.i2h(x, 2)
                            elif lab_len == 4 and x < 65536:
                                oper = '$' + fn.i2h(x, 4)
                            else:
                                pass2_error_count += 1
                                print('Error on:', token_line, ' - Symbol Arithmetic Overflow')
                                oper = '$FF'
                                if lab_len == 4:
                                    oper += 'FF'
                        else:
                            oper = '$' + label_dict[label]

                        if isinstance(mode, tuple):
                            if 'Zero Page,X' in mode:
                                oper = oper + ',X'
                            elif 'Zero Page,Y' in mode:
                                oper = oper + ',Y'
                        else:
                            if mode == 'Indirect':
                                oper = '(' + oper + ')'
                            elif mode == 'Indirect,X':
                                oper = '(' + oper + ',X)'
                            elif mode == 'Indirect,Y':
                                oper = '(' + oper + '),Y'
                            elif mode == 'Immediate':   
                                oper = '#' + oper                            
                        break
                        
            am, nb, oc = fn.determine_mode(token_line[0], oper)
        elif len(token_line) == 1:
            am, nb, oc = fn.determine_mode(token_line[0], '')
                
        if am == 'Implied' or am == 'Accumulator':
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc)
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc
        elif am == 'Immediate' or am == 'Indirect,X' or am == 'Indirect,Y':
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc, oper[2:4])
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc + oper[2:4]
        elif am == 'Zero Page' or am == 'Zero Page,X' or am == 'Zero Page,Y': 
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc, oper[1:3])
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc + oper[1:3]
        elif am == 'Absolute' or am == 'Absolute,X' or am == 'Absolute,Y':
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc, oper[3:5], oper[1:3])
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc + oper[3:5] + oper[1:3]
        elif am == 'Indirect':
            lineout = fn.myprint(line, fn.i2h(pc, 4), ':', oc, oper[4:6], oper[2:4])    
            lstout.write(lineout)   
            code_dict[fn.i2h(pc, 4)] = oc + oper[4:6] + oper[2:4]
        pc = pc + nb
        
lstout.close()

if pass2_error_count > 0:
    print('Error(s) Encountered')
    print('Unable to Continue')
    exit(2)   

# create and write out the Intel hex file
print(' ')
print('Creating Intel hex file')
fiout = finame.split('.')[0] + '.hex'
tot_bytes = 0
tot_code = ''
with open(fiout, 'w') as sfo:
    for address in code_dict:
        if tot_code  == '':
            iaddress = address
        code = code_dict[address]
        num_bytes = len(code) // 2
        next_address = hex(int(address, 16) + num_bytes).upper()[2:].zfill(4)
        tot_bytes += num_bytes
        tot_code += code
        if tot_bytes < 16 and next_address in code_dict:
            continue
        iline = ':' + hex(tot_bytes).upper()[2:].zfill(2) + iaddress + '00' + tot_code 
        x = iline[1:]
        y = [int(x[i:i+2],16) for i in range(0,len(x),2)]
        chksum = hex(256-sum(y) % 256)[2:].zfill(2).upper()
        if len(chksum) > 2:
            chksum = chksum[1:]
        iline += chksum + '\n'
        sfo.write(iline)
        tot_bytes = 0
        tot_code = ''

print('Intel hex file created')
print(' ') 
print('All Done')
exit(0)       