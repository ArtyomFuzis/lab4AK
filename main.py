from compiler.parser import Parser

txt = """
.section data
a: .byte 56
b: .word 896
.section text
.org 0x0100
start: ld_a a
inc 
dec4
jmp end
add 59
end: 
halt
.section int
"""
if __name__ == '__main__':
    Parser.parse_asm(txt)
