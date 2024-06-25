#everyone loves lookup tables!
all_regs = [0,1,2,3,4,5,6,7]
all_mem = [-1,-2,-3,-4,-5,-6,-7]

valid_instructions = [
[["mov", [all_regs,all_regs]], 0x00], #mov reg-reg
[["mov", [[3], [0xff]]], 0x01], #movx
[["mov", [[4], [0xff]]], 0x02], #movy
[["mov", [[5], [0xff]]], 0x03], #mova
[["mov", [[6], [0xff]]], 0x04], #movb
[["mov", [[7], [0xff]]], 0x05], #movacc
[["mov", [[3], [-0xff]]], 0x06], #mov ram->x
[["mov", [[4], [-0xff]]], 0x07], #mov ram->y
[["mov", [[5], [-0xff]]], 0x08], #mov ram->a
[["mov", [[6], [-0xff]]], 0x09], #mov ram->b
[["mov", [[7], [-0xff]]], 0x0A], #mov ram->acc
[["mov", [all_regs, all_mem]], 0x0D], #mov reg->[reg]
[["mov", [all_mem, all_regs]], 0x0C], #mov [reg]->reg
[["mov", [[-0xff], [3]]], 0x0D], #mov x->ram
[["mov", [[-0xff], [4]]], 0x0E], #mov y->ram
[["mov", [[-0xff], [5]]], 0x0F], #mov a->ram
[["mov", [[-0xff], [6]]], 0x10], #mov b->ram
[["mov", [[-0xff], [7]]], 0x11], #mov acc->ram


[["maths", [all_regs, [0xff]]], 0x12], #do maths

[["cmp", [all_regs, all_regs]], 0x13],
[["cmp", [all_regs, [0xff]]], 0x14],
[["test", [[0xff]]], 0x15],
[["jmpr", [[0xff]]], 0x16],
[["jmp", [[0xff]]], 0x17],
#relative register jump is useless
[["jmp", [all_regs]], 0x19],

[["push", [all_regs]], 0x1A],
[["push", [[0xff]]], 0x1B],
[["pop", [all_regs]], 0x1C],
[["call", [[0xff]]], 0x1D],
[["ret", []], 0x1E]
]

regs = {
"isp": 0x00, # stack pointer
"ip" : 0x01, # instruction pointer
"fl" : 0x02,
"x"  : 0x03,
"y"  : 0x04,
"a"  : 0x05,
"b"  : 0x06,
"acc": 0x07
}

maths = [["add",0x00],["sub",0x01],["mul",0x02],["div",0x03],["rem", 0x04],["bsr",0x05],["bsl",0x06],
["and",0x07],["or", 0x08],["xor",0x09],["not",0x0A]]

def get_inst(instruction_data):
	#most complicated function I have ever made
	#work out the instruction based on the pneumonic and the operands given
	#create list of operand types
	tmp = instruction_data[1:]
	operands = []
	#operand types
	#negative is used as an address
	#255 is an immediate
	#register is its id number
	for i in tmp:
		isaddr = False
		if(i[:1] == "[" and i[-1:] == "]"):
			isaddr = True
		elif("[" in i or "]" in i):
			print(f"Unexpected square bracket in instruction {instruction_data}")
			exit()
		i = i.strip("[]")
		is_imm = False
		try:
			a = int(i, 10)
			is_imm = True
		except:
			pass
		try:
			a = int(i, 0x10)
			is_imm = True
		except:
			pass
		#todo - Make this 1000 times more complicated
		argtype = 0
		if(is_imm):
			argtype = 0xff
		else:
			argtype = regs[i]

		if(isaddr):
			argtype *= -1
		operands.append(argtype)
	print(instruction_data)
	print(operands)
	
	#operands now contains an array of the different operand types provided
	inst = instruction_data[0]
	#inst contains the instruction pneumonic
	
	#pad out operands with invalid operands to avoid jankiness later
	operands.append(0xfff)
	operands.append(0xfff)
	operands.append(0xfff)

	#combine into a horrible mess

	isntmess = [inst, operands]
	for i in valid_instructions:
		#structure (of i)is:
			#array containing[instruction data, instruction number]
			#data is ["name", arguments]
			#arguments is [args, args]
			#any number of args each of which is:
				#an array of acceptable numbers for that arg
		#step 1
		#decode basic facts like number of instruction paramaters
		#and the paramaters it takes de-packed
		#check if they match perfectly
		#if they do, return the instruction number
		#else try a different instruction
		#print error if none match
		num_args = len(i[0][1])
		arg_types = i[0][1]
		failiure = False
		for j in range(num_args):
			if(operands[j] in arg_types[j])
		pass


#done with the hardest part now (he says, hopefully)

filen = input("Filename >")
file = open(filen, "r")

lines = file.readlines()
for i in range(len(lines)):
	thing = True
	acc =""
	for j in range(len(lines[i])):
		if(thing and lines[i][j] == ";"):
			thing = False
		if(thing):
			acc += lines[i][j]
	lines[i] = acc
	lines[i] = lines[i].strip()

#n passes
#remove redundant lines
#work out adresses of each instruction, and label
#resolve labels
#split instructions into ins + args
#encode as numbers
#write

#remove redundant + get adresses
ins = []
loc = 0
for i in lines:
	if(i != ""):
		ins.append([loc,i])
		if(i[:3] == "num"):
			loc += 2
		elif(i[-1:] == ":"):
			loc += 0
		else:
			loc += 3

labeltable = maths
for i in ins:
	if(i[1][-1:] == ":"):
		labeltable.append([i[1][:-1], i[0]])

#replace labels with labeladresses
for i in range(len(ins)):
	for j in labeltable:
		if(j[0] in ins[i][1] and ins[i][1][-1:] != ":"):
			ins[i][1] = ins[i][1].replace(j[0], str(j[1]))

#remove lables
i = 0
while(i < len(ins)):
	if(ins[i][1][-1:] == ":"):
		ins.pop(i)
	else:
		i += 1

#split instructions into parts 
for i in range(len(ins)):
	ins[i][1] = ins[i][1].split()
	for j in range(len(ins[i][1])):
		ins[i][1][j] = ins[i][1][j].strip(", \n()")
	
#work out the unique instruction byte
for i in range(len(ins)):
	ins[i][1][0] = get_inst(ins[i][1])

print(ins)
del(labeltable)