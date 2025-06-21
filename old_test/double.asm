.section data

.org 0x22
num1_lower: .word 0x25d7239c
num1_upper: .word 0x19f28daa
num2_lower: .word 0xff826798
num2_upper: .word 0xffffffff
res_lower:  .word 0
res_upper:  .word 0

.section text
start:
   ld_a     num1_lower
   add_a    num2_lower
   st       res_lower
   jnc      no_c_flag
   ld       1
   jmp      upper

no_c_flag:
   ld       0
   jmp      upper

upper:
   add_a    num1_upper
   add_a    num2_upper
   st       res_upper

   ld_a     res_upper
   st       0x21
   ld_a     res_lower
   st       0x21
   halt

.section int
    ret