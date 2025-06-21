.section data

.org 0x22
arr1: .word 12 45 89 123
arr2: .word -12 68468 9 -124
arr3: .word -123 0 -1 4856
pointer_1: .word arr1
pointer_2: .word arr2
pointer_3: .word arr3
tmp:       .word 0
read_cnt:  .word 0
save:      .word 0
rr:        .word 0

.section text

#define cmp_step
    ld_ind  pointer_2
    st      tmp
    ld_ind  pointer_1
    add_a   tmp
    st      tmp
    ld_ind  pointer_3
    mul_a   tmp
    jnz     no_add_$1
    ld_a    rr
    inc
    st      rr

no_add_$1:
    ld_a    pointer_1
    inc4
    st      pointer_1
    ld_a    pointer_2
    inc4
    st      pointer_2
    ld_a    pointer_3
    inc4
    st      pointer_3

#enddefine

start:    ; func: (a+b)*c == 0
    cmp_step 1
    cmp_step 2
    cmp_step 3
    cmp_step 4

    ld_a    rr
    st      0x21
    halt

.section int
    ret