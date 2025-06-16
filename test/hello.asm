.section data

.org 0x22
str:        .byte 'hello' 0x20 'world!!!'
iters:      .word 14
cur_addr:   .word str

.section text

start:
    loop:
        ld_ind  cur_addr
        and     0xFF000000
        shiftr  24
        st      0x21

        ld_a    cur_addr
        inc
        st      cur_addr

        sub     str
        sub_a   iters
        jnz     loop
    halt


.section int
    halt