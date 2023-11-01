  ; ** test source code for the JLS 6502 Assembler **
  ; Note 1: this is a nonsense program - it is meant to 
  ; convey proper assembler syntax only.

  ; Note 2: this assembler does NOT require fields to start 
  ; in certain (fixed) columns. Also case is irrelevant. 

  ; Note 3: all equate (.equ) statements MUST precede
  ; the program code as shown in the example below.
  
  ; Note 4: this assembler does NOT support the CMOS
  ; version of the 6502 only the MOS (original) version.
  
  ; Note 5: this assembler has NO macro facility.  
  
  ; Note 6: a .org directive MUST be the first
  ; statemant in the assembler source code.

  ; Note 7: a .end directive MUST be the last
  ; statemant in the assembler source code.

  ; Note 8: '.org', '.db', '.ds', '.equ', '.end' are the
  ; only assembler directives. '.ds' is define (reserve) storage -
  ; the rest are self-explanatory.  
          .org $0200
  xxxx    .equ $10
  yyyy    .equ $4000
  zzzz    .equ 255
  begin   LDA #$FF    ; load accum 
          LDA #255
          LDA #'A'
          LDA #%00000011
          LDA byte2,X
          BNE begin
          BEQ debug
          STA $1500   ; save it
          LDA yyyy
          JMP begin
          SBC $44,X
          ROR $AAAA
          STA $4400,Y
clrlp     sta (xxxx),y
          iny
          dex
          bne clrlp
  debug   inx
          lda xxxx+1
          lda yyyy+10
          JMP ($5597)
  byte1   .db $0f,$44,15,$ee,80
  byte2   .db 'ABCD',%00001111
  area1   .ds 5
  byte2   .db $55
          .end
