.section data

.org 0x22
inp_status: .word 0
save:       .word 0
pointer:    .word arr
end_ptr:    .word 0
second:     .word 0
second_ptr: .word 0
arr:        .word 0


.section text

start:

    start_loop:
        ld_a   inp_status
        jz     start_loop

    big_bubble_loop:
        ld     arr
        st     pointer

    bubble_loop:
        ld_a        pointer
        inc4
        st          second_ptr
        ld_ind      second_ptr
        st          second
        ld_ind      pointer
        sub_a       second
        jlt         less

    bigger:
        ld_ind     pointer
        st_ind     second_ptr
        ld_a       second
        st_ind     pointer

    less:
        ld_a    pointer
        inc4
        st      pointer
        sub_a   end_ptr
        jnz     bubble_loop

    ld_a    end_ptr
    dec4
    st      end_ptr

    sub     arr
    jnz     big_bubble_loop
    ld     arr
    st     pointer

    end_loop:
        ld_ind     pointer
        st         0x21
        jz         end
        ld_a       pointer
        inc4
        st         pointer
        jmp        end_loop
    end:
        halt


.section int
    st      save

    ld_a    inp_status
    jnz     int_ret

    ld_a    0x20
    st_ind  pointer
    jz      inp_end

    ld_a    pointer
    inc4
    st      pointer

    jmp     int_ret

    inp_end:
        ld     1
        st     inp_status

        ld_a   pointer
        dec4
        st     end_ptr

    int_ret:
        ld_a     save
        ret