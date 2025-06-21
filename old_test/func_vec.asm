.section data

.org 0x22
arr1: .word 12 45 89 123
arr2: .word -12 68468 9 -124
arr3: .word -123 0 -1 4856
res:      .word 0 0 0 0
pointer:  .word res
read_cnt: .word 0
save:     .word 0
rr:       .word 0

.section text

#define cmp_step
    ld_ind  pointer
    sub     1
    jnzr    11

    ld_a    rr
    inc
    st      rr

    ld_a    pointer
    inc4
    st      pointer
#enddefine

start:    ; func: (a+b)*c == 0
    vld1    arr1
    vld2    arr2
    vadd12
    vmv31
    vld2    arr3
    vmul12
    vcmp3
    vst3    res

    cmp_step
    cmp_step
    cmp_step
    cmp_step

    ld_a    rr
    st      0x21
    halt

.section int
    ret