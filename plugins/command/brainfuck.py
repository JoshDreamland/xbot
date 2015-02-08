from plugins import plugin

def brainfuck(input_bytes, program, max_steps):
    input_bytes_pos = 0

    tape = {}
    ptr = 0

    def parse():
        loops = {}
        i = 0
        stack = []
        while i < len(program):
            if program[i] == '[':
                stack.append(i)
            if program[i] == ']':
                if len(stack) == 0:
                    raise Exception("Mismatched square brackets.")
                loops[stack[-1]] = i
                del stack[-1]
            if program[i] not in '[]<>+-,.':
                raise Exception("Illegal character " + program[i])
            i += 1
        if len(stack) > 0:
            raise Exception("Mismatched square brackets.")
        return loops

    ends = parse()

    steps = 0
    pc = 0
    stack = []
    output = ""
    while pc < len(program):
        c = program[pc]
        if c == '>':
            ptr += 1
        elif c == '<':
            ptr -= 1
        elif c == '+':
            if ptr not in tape:
                tape[ptr] = 0
            tape[ptr] += 1
        elif c == '-':
            if ptr not in tape:
                tape[ptr] = 0
            tape[ptr] -= 1
        elif c == '.':
            if ptr not in tape:
                tape[ptr] = 0
            
            if tape[ptr] < ord(' ') or tape[ptr] > ord('~'):
                a = '\\' + hex(tape[ptr])
            else:
                a = chr(tape[ptr])
                
            output += a
        elif c == ',':
            if ptr not in tape:
                tape[ptr] = 0
            if input_bytes_pos >= len(input_bytes):
                tape[ptr] = 0
            else:
                tape[ptr] = ord(input_bytes[input_bytes_pos])
                input_bytes_pos += 1
        elif c == '[':
            if ptr not in tape:
                tape[ptr] = 0
            if tape[ptr]:
                stack.append(pc)
            else:
                pc = ends[pc]
        elif c == ']':
            pc = stack[-1]-1
            del stack[-1]
        pc += 1
        steps += 1
        if steps >= max_steps:
            raise Exception("Program timeout (PC: %d)" % pc)
    return output

class pluginClass(plugin):
    def gettype(self):
        return "command"
        
    def action(self,complete):
        msg = complete.message()

        tokens = msg.split()
        if len(tokens) == 1:
            program = tokens[0]
            input_bytes = ''
        elif len(tokens) > 1:
            program = tokens[-1]
            input_bytes = ' '.join(tokens[:-1])
        else:
            return self.describe(0)

        try:
            output = brainfuck(input_bytes, program, 2000000)
            return ["PRIVMSG $C$ :" + (output if len(output) > 0 else "[No output]")]
        except Exception as e:
            return ["PRIVMSG $C$ :Fatal error - " + str(e)]

    def describe(self, complete):
        return ["PRIVMSG $C$ :I am the brainfuck plugin!",
                "PRIVMSG $C$ :Usage: !brainfuck <input stream> <program>",
                "PRIVMSG $C$ :The tape consists of 1024 integers. Good luck!"]

