import time
import threading
import sys
import signal


class CPU:
    def __init__(self):
        print('Booting up')
        self.reg = [0] * 8
        self.ram = [0] * 256
        self.pc=0
    def add(self):
        self.alu('ADD', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3
        self.pc = 0
        self.sp = 7
        self.reg[self.sp] = 0xf4
        self.fl = 0b00000000
        self.MAR = 3
        self.MDR = 4

    def cmp(self):
        self.alu('CMP', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3

    def alu(self, op, reg_a, reg_b=None):
        """ALU operations."""
        if op == "CMP":
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
                # print('equal')
                return self.fl
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010
                # print('greater than')
                return self.fl
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
                return self.fl
                # print('less than')
        elif op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
            return self.reg[reg_a]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "SUB":
            self.reg[reg_a] -= self.reg[reg_b]
        elif op == "DIV":
            self.reg[reg_a] /= self.reg[reg_b]
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        elif op == "XOR":
            self.reg[reg_a] ^= self.reg[reg_b]
        elif op == "OR":
            self.reg[reg_a] |= self.reg[reg_b]
        elif op == "NOT":
            self.reg[reg_a] = ~self.reg[reg_a]
        elif op == "SHL":
            self.reg[reg_a] << self.reg[reg_b]
        elif op == "SHR":
            self.reg[reg_a] >> self.reg[reg_b]
        elif op == "MOD":
            if self.reg[reg_b] == '0':
                print('error message')
                self.hlt()
            else:
                self.reg[reg_a] %= self.reg[reg_b]

        else:
            raise Exception("Unsupported ALU operation")

    def call(self):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.pc + 2
        self.pc += 2
        
    def keyboard_interrupt_handler(self, signal, frame):
        print()
        print('-'*50, '\n Keyboard interrupt, (ID: {}) has been caught, Cleaning up now....'.format(
            signal), '\n', '-'*50, '\n', '\n', '\n')
        exit(0)

    def hlt(self):
        self.pc += 1
        sys.exit(0)

    def ldi(self):
        self.reg[self.ram_read(self.pc + 1)] = self.ram_read(self.pc + 2)

        self.pc += 3

    def prn(self):
        print(self.reg[self.ram_read(self.pc + 1)])
        self.pc += 2

    def mul(self):
        self.alu('MUL', self.ram[self.pc + 1], self.ram[self.pc + 2])
        self.pc += 3


    def pop(self):
        self.ram_pop(self.ram[self.pc + 1])
        self.pc += 2

    def push(self):
        self.ram_push(self.pc + 1)
        self.pc += 2




    def jeq(self):
        if self.fl == 1:
            self.jump()
        else:
            self.pc += 2

    def jne(self):
        if self.fl != 1:
            self.jump()
        else:
            self.pc += 2
    
    def jump(self):
        self.pc = self.reg[self.ram[self.pc + 1]]
    

    def load(self):
        """Load a program into memory."""

        address = 0
        load_address = 0

        program = [0] * 256

        if len(sys.argv) != 2:
            print(f"Usage:\npython3 {sys.argv[0]} filename.ls8")
            exit()
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    possible_num = line[:line.find('#')]    # strip comments
                    if possible_num == '':                  # strip blank lines
                        continue
                    # convert "binary" string into a number
                    program[load_address] = (int(possible_num, 2))
                    load_address += 1
                    if load_address == 256:
                        raise Exception("Out of memory. Program is too large.")

        except FileNotFoundError:
            print(f"{sys.argv[1]} not found.")
            exit()

        for instruction in program:
            self.ram[address] = instruction
            address += 1
    
    def ret(self):
        self.pc = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc += 1

    def run(self):
        """Run the CPU."""
        # self.trace()
        print('-' * 25)

        # ir = self.ram_read(self.pc)

        running = True
        self.timerkeepr()
        signal.signal(signal.SIGINT, self.keyboard_interrupt_handler)
        while running:
            ir = self.ram_read(self.pc)
            # print(f'Current IR: {ir}')

            if ir == 0b00000001:  # HLT -1- Computer Halt (STOP)
                print(f'{"-"*10} HLT {"-"*10} \n COMPUTER STOPPED')
                self.hlt()

            elif ir == 0b10000010:  # LDI -130- Add to registry
                self.ldi()
            elif ir == 0b01000111:    # PRN -71- Display next item from ram
                self.prn()
            elif ir == 0b10100010:   # MUL -162- multipy the next two
                # print(f'{"-"*10} MUL {"-"*10} ')
                self.mul()
            elif ir == 0b10100000:   # MUL -162- multipy the next two
                # print(f'{"-"*10} ADD {"-"*10} ')
                self.add()
            elif ir == 0b01000101:    # PUS -69- add item to stack in end of ram
                # print(f'{"-"*10} PUSH {"-"*10} ')
                self.push()
            elif ir == 0b01000110:    # POP -- remove the last item from the stack
                # print(f'{"-"*10} POP {"-"*10} ')
                self.pop()
            elif ir == 0b01010000:  # Call -80-
                # print(f'{"-"*10} CALL {"-"*10} ')
                # print(self.pc, self.reg, self.ram[:10])
                self.call()
            elif ir == 0b00010001:  # RETURN -17-
                # print(f'{"-"*10} RETURN {"-"*10} ')
                self.ret()
            elif ir == 0b10100111:    # COMPARE -167-
                self.cmp()
            elif ir == 0b01010101:  # JEQ -85- jeq  if equal true jump here
                self.jeq()
            elif ir == 0b01010110:  # JNE -86- if equal is false jump here
                self.jne()
            elif ir == 0b01010100:  # JMP -84-
                self.jump()

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, item):
        # print('in ram_write')
        # print(address, item)
        self.ram[address] = item

    def ram_pop(self, address):
        self.reg[address] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1

    def ram_push(self, address):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[self.ram[address]]

    def reg_write(self, address, item):
        self.reg[address] = item

    def reg_read(self, address):
        # print(self.reg[address])
        return self.reg[address]

    def timerkeepr(self):
        print('\n', time.ctime(), '\n')
        threading.Timer(5, self.timerkeepr).start()


"""Main."""


cpu = CPU()

cpu.load()

cpu.run()
