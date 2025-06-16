.section data

.org 0x22
start_str:  .byte 'What' 0x20 'is' 0x20 'your' 0x20 'name?' 0x0A 0x00
cur_addr:   .word start_str
save:       .word 0
state:      .word 0
state_end:  .word 0
name_addr:  .word name
end_str:    .byte 'Hello,' 0x20
name:       .byte 0
.section text

start:
    loop:
        ld_ind  cur_addr
        and     0xFF000000

        shiftr  24
        st      0x21
        jz      end

        ld_a    cur_addr
        inc
        st      cur_addr

        jmp     loop


    wait_loop:
        ld_a    state
        jz      wait_loop
        ld      end_str
        st      cur_addr
        ld      1
        st      state_end

        ld      '!'
        shiftl  24
        st_ind  name_addr
        ld_a    name_addr
        inc
        st      name_addr
        ld      0
        st_ind  name_addr
        jmp     loop

    end:
        ld_a    state_end
        jz      wait_loop
        halt

.section int
    st      save
    ld_a    state
    jnz     int_ret

    ld_a    0x20
    shiftl  24
    st_ind  name_addr
    jz      end_inp

    ld_a    name_addr
    inc
    st      name_addr

    jmp     int_ret

    end_inp:
        ld      1
        st      state

    int_ret:
        ld_a save
        ret