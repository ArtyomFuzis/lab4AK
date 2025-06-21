.section data

.org 0x22
arr: .word 500 360 -1 69
res: .word 0 0 0 0
pointer: .word res

.section text

#define to_st_inc
    ld_ind $2
    st  $1
    ld_a $2
    inc4
    st $2
#enddefine

start:
    vld3 arr
    vmv31
    vmv32
    vadd12
    vst3 res
    to_st_inc 0x21 pointer    ; some cool comment
    to_st_inc 0x21 pointer
    to_st_inc 0x21 pointer
    to_st_inc 0x21 pointer
    halt


.section int
    ret