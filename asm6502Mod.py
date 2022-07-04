# 
# asm6502Mod.py V1.R1.M0
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

import re


valid_mnemonic_table = { 'LDA', 'BVS', 'PLA', 'INY', 'PHA', 'RTS', 'BCS', 'DEC', 'AND',
                         'NOP', 'STY', 'ASL', 'BRK', 'TAX', 'SED', 'TXS', 'INC', 'EOR', 
                         'BMI', 'CPX', 'TYA', 'INX', 'LDY', 'PLP', 'LDX', 'STX', 'JSR', 
                         'BNE', 'BVC', 'CPY', 'LSR', 'CLI', 'CLV', 'ROL', 'TXA', 'DEX', 
                         'TSX', 'CLD', 'SEC', 'TAY', 'BPL', 'JMP', 'ADC', 'CLC', 'SEI', 
                         'PHP', 'SBC', 'BCC', 'BIT', 'RTI', 'ROR', 'STA', 'DEY', 'BEQ', 
                         'CMP', 'ORA',
}


valid_directive_table = { '.ORG', '.DB', '.DS', '.EQU', '.END' }


address_mode = {
#   ROR A
    'Accumulator': (1, [ ('ASL', '0A'), ('LSR', '4A'), ('ROL', '2A'), ('ROR', '6A') ] ),

#   SBC #$44
    'Immediate':   (2, [ ('ADC', '69'), ('AND', '29'), ('LDY', 'A0'), ('LDX', 'A2'), 
                         ('LDA', 'A9'), ('EOR', '49'), ('CPY', 'C0'), ('CPX', 'E0'), 
                         ('CMP', 'C9'), ('ORA', '09'), ('SBC', 'E9') ] ),

#   SBC $44
    'Zero Page':   (2, [ ('ADC', '65'), ('AND', '25'), ('ASL', '06'), ('BIT', '24'), 
                         ('LSR', '46'), ('LDY', 'A4'), ('LDX', 'A6'), ('LDA', 'A5'), 
                         ('INC', 'E6'), ('EOR', '45'), ('DEC', 'C6'), ('CPY', 'C4'), 
                         ('CPX', 'E4'), ('CMP', 'C5'), ('ORA', '05'), ('ROL', '26'),
                         ('ROR', '66'), ('SBC', 'E5'), ('STA', '85'), ('STX', '86'),
                         ('STY', '84') ] ),

#   SBC $44,X
    'Zero Page,X': (2, [ ('ADC', '75'), ('AND', '35'), ('ASL', '16'), ('CMP', 'D5'),
                         ('DEC', 'D6'), ('EOR', '55'), ('INC', 'F6'), ('LDA', 'B5'),
                         ('LDY', 'B4'), ('LSR', '56'), ('ORA', '15'), ('ROL', '36'),
                         ('ROR', '76'), ('SBC', 'F5'), ('STA', '95'), ('STY', '94') ] ),

#   STX $44,Y
    'Zero Page,Y': (2, [ ('LDX', 'B6'), ('STX', '96') ] ),

#   STX $4400
    'Absolute':    (3, [ ('ADC', '6D'), ('AND', '2D'), ('ASL', '0E'), ('BIT', '2C'), 
                         ('CMP', 'CD'), ('CPX', 'EC'), ('CPY', 'CC'), ('DEC', 'CE'),
                         ('EOR', '4D'), ('INC', 'EE'), ('JMP', '4C'), ('JSR', '20'),
                         ('LDA', 'AD'), ('LDX', 'AE'), ('LDY', 'AC'), ('LSR', '4E'),
                         ('ORA', '0D'), ('ROL', '2E'), ('ROR', '6E'), ('SBC', 'ED'),
                         ('STA', '8D'), ('STX', '8E'), ('STY', '8C') ] ),

#   STA $4400,X
    'Absolute,X':  (3, [ ('ADC', '7D'), ('AND', '3D'), ('ASL', '1E'), ('CMP', 'DD'),
                         ('DEC', 'DE'), ('EOR', '5D'), ('INC', 'FE'), ('LDA', 'BD'),
                         ('LDY', 'BC'), ('LSR', '5E'), ('ORA', '1D'), ('ROL', '3E'),
                         ('SBC', 'FD'), ('STA', '9D') ] ),

#   STA $4400,Y
    'Absolute,Y':  (3, [ ('ADC', '79'), ('AND', '39'), ('CMP', 'D9'), ('EOR', '59'),
                         ('LDA', 'B9'), ('LDX', 'BE'), ('ORA', '19'), ('SBC', 'F9'),
                         ('STA', '99') ] ),

#   JMP ($5597)
    'Indirect':    (3, [ ('JMP', '6C') ] ),

#   LDA ($44,X)
    'Indirect,X':  (2, [ ('ADC', '61'), ('AND', '21'), ('CMP', 'C1'), ('EOR', '41'),
                         ('LDA', 'A1'), ('ORA', '01'), ('SBC', 'E1'), ('STA', '81') ] ),

#   LDA ($44),Y
    'Indirect,Y':  (2, [ ('ADC', '71'), ('AND', '31'), ('CMP', 'D1'), ('EOR', '51'),
                         ('LDA', 'B1'), ('ORA', '11'), ('SBC', 'F1'), ('STA', '91') ] ),

#   BRK
    'Implied':     (1, [ ('BRK', '00'), ('CLC', '18'), ('SEC', '38'), ('CLI', '58'),
                         ('SEI', '78'), ('CLV', 'B8'), ('CLD', 'D8'), ('SED', 'F8'),
                         ('TAX', 'AA'), ('TXA', '8A'), ('DEX', 'CA'), ('INX', 'E8'),
                         ('TAY', 'A8'), ('TYA', '98'), ('DEY', '88'), ('INY', 'C8'),
                         ('TXS', '9A'), ('TSX', 'BA'), ('PHA', '48'), ('PLA', '68'),
                         ('PHP', '08'), ('PLP', '28'), ('NOP', 'EA'), ('RTI', '40'),
                         ('RTS', '60') ] )
}


address_mode_patterns = {
    '\#\$[0-9A-F]{2}': 'Immediate', '\$[0-9A-F]{2}': 'Zero Page', '\$[0-9A-F]{2},X': 'Zero Page,X', 
    '\$[0-9A-F]{2},Y': 'Zero Page,Y', '\$[0-9A-F]{4}': 'Absolute', '\$[0-9A-F]{4},X': 'Absolute,X',
    '\$[0-9A-F]{4},Y': 'Absolute,Y', '\(\$[0-9A-F]{4}\)': 'Indirect', '\(\$[0-9A-F]{2},X\)': 'Indirect,X',
    '\(\$[0-9A-F]{2}\),Y': 'Indirect,Y'
}


# Convert int x to hex string and left zero fill to y positions
def i2h(x, y):
    return hex(x)[2:].zfill(y).upper()


# Construct, print, and return a source listing line
def myprint(sline, *arguments):
    z = ''
    for arg in arguments:
        if isinstance(arg, str):
            z = z + arg + ' '
        else:
            z = z + str(arg) + ' '
    l = len(z)
    if l > 25:
        z = z[0:26]
    else:
        z = z + (25-l)*' '
    print(z, sline)
    return z + ' ' + sline + '\n'
    
    
# Convert a negative signed integer to a 1 byte hex string in two's complement format
def cvtint2scomp(x):
    t = bin(x)[3:]
    b = '0'*(8-len(t)) + t   #expand by propagating a '0' out to 8 bits
    #flip the bits in b creating num1 
    num1 = ''
    for bit in b:
        if bit == '0':
            num1 = num1 + '1'
        else:
            num1 = num1 + '0'
    return hex(int(num1,2) + int('0001',2))[2:].upper()
    
    
# Tokenize source line into a list
# Discarding any comment on the right
def tokenize_sl(line):
    z = line.find(';')
    if z == -1:
        z = len(line)
    return [y for y in line[0:z].upper().split(' ') if y != '']


# Given the mnemonic and operand in a source line
# determine the addressing mode and...
# return the addressing mode, number of bytes for that instruction and 
# the instruction's opcode
#
# 'XX' is returned in cases where the assembler mnemonic is invalid
# 'Invalid' is returned for mode and 9 is returned for numbytes 
# in cases where the addressing mode cannot be determined
#
def determine_mode(mnemonic, operand):
    mode = 'Invalid'
    if operand == '':
        mode = 'Implied'
    elif operand == 'A':
        mode = 'Accumulator'
    else:
        for p in address_mode_patterns.keys():
            z = re.fullmatch(p, operand)
            if z != None:
                mode = address_mode_patterns[p]        
                break

    if mode == 'Invalid':
        return (mode, 9, 'XX')
    
    numbytes = address_mode[mode][0]
    good_mnemonic = False
    for m, opc in address_mode[mode][1]:
        if m == mnemonic:
            good_mnemonic = True
            break
    if good_mnemonic:
        return (mode, numbytes, opc)
    else:
        return (mode, numbytes, 'XX')


# Construct data bytes field from a .db directive
# return the number of bytes and data bytes string
def build_data_bytes(operand):
    db_str = ''
    for db in operand.split(','):
        if db.startswith('$'):
            db_str = db_str + db[1:]
        elif db[0].isdigit():
            h = hex(int(db))[2:].upper()
            if (len(h) % 2) != 0:
                db_str = db_str + '0' + h
            else:
                db_str = db_str + h
        elif db[0] == "'":
            for c in db:
                if c == "'":
                    continue
                else:
                    db_str = db_str + hex(ord(c))[2:].zfill(2).upper()
        elif db[0] == '%':                   
            db_str = db_str + hex(int(db[1:],2))[2:].zfill(2).upper()
    nb = len(db_str) // 2        
    return (nb, db_str)
    