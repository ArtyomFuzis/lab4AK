.section text
start:
   jmp start


.section int
    ld_a    0x20
    st      0x21
    ret