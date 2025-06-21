.section data

.org 0x22
res1:   .word 0
i:      .word 1
limit:  .word 101
res2:   .word 0

.section text
start:
main_loop:
        ld_a    i
        add_a   res1
        st      res1

        ld_a    i
        mul_a   i
        add_a   res2
        st      res2

        ld_a    i
        inc
        st      i
        sub_a   limit
        jnz     main_loop

    ld_a    res1
    mul_a   res1
    sub_a   res2
    st      0x21
    halt

.section int
    ret