# 6502Asm
## An Assembler for the 6502 Microprocessor

This program requires the Python3 interpreter to be installed.

Installation instructions:
- Download asm6502.py AND asm6502Mod.py and save both to a directory of your choosing
- Save your assembler source file (.asm extension) to the same directory
- Navigate to that directory
- Then invoke python3 against asm6502.py as is shown below

Usage is as follows:   python3 asm6502.py inputsourcefile

   Example:  python3 asm6502.py test1.asm
   
(replace python3 with whatever command you use on your system to invoke the Python 3 interpreter)
   
A successful assembly will create the following 2 files in the current working directory (from the above example):
   - test1.lst  -  the assembler listing
   - test1.hex  -  the machine language file in Intel hex format
   
Other noteable items:
  - Note 1: this assembler does NOT require fields to start 
    in certain (fixed) columns. Also case is irrelevant. 

  - Note 2: all equate (.equ) statements MUST precede
    the program code as shown in the test1.asm example.
  
  - Note 3: this assembler does NOT support the CMOS
    version of the 6502 only the MOS (original) version.
  
  - Note 4: this assembler has NO macro facility.  
  
  - Note 5: a .end statement MUST be the last
    statemant in the assembler source code.
  
  - Note 6: '.org', '.db', '.ds', '.equ', '.end' are the
    only assembler directives. '.ds' is define (reserve) storage -
    the rest are self-explanatory.  
