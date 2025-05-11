from components import DataBus, TrapControlLatch, StateLatch, MemoryUnit

if __name__ == '__main__':
    inb = DataBus(4)
    outb = DataBus(4)
    addrb = DataBus(2)
    control = TrapControlLatch()
    rw = StateLatch()
    mem = MemoryUnit(control, rw, addrb, inb, outb)

    addr = 0x2
    addr2 = 0x3
    value = 123456
    addrb.post_data(addr.to_bytes(2))
    inb.post_data(value.to_bytes(4))
    rw.change_state(True)
    control.change_state(True)

    addrb.post_data(addr2.to_bytes(2))
    rw.change_state(False)
    control.change_state(True)
    print(int.from_bytes(outb.get_data()))
