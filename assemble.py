#everyone loves lookup tables!
all_regs = [0,1,2,3,4,5,6,7]
all_mem = [-1,-2,-3,-4,-5,-6,-7]

valid_instructions = [
[["mov", [all_regs,all_regs]], [0x00, [True, True]]], #mov reg-reg
[["mov", [[3], [0xff]]], [0x01, [False, True]]], #movx
[["mov", [[4], [0xff]]], [0x02, [False, True]]], #movy
[["mov", [[5], [0xff]]], [0x03, [False, True]]], #mova
[["mov", [[6], [0xff]]], [0x04, [False, True]]], #movb
[["mov", [[7], [0xff]]], [0x05, [False, True]]], #movacc
[["mov", [[3], [-0xff]]], [0x06, [False, True]]], #mov ram->x
[["mov", [[4], [-0xff]]], [0x07, [False, True]]], #mov ram->y
[["mov", [[5], [-0xff]]], [0x08, [False, True]]], #mov ram->a
[["mov", [[6], [-0xff]]], [0x09, [False, True]]], #mov ram->b
[["mov", [[7], [-0xff]]], [0x0A, [False, True]]], #mov ram->acc
[["mov", [all_regs, all_mem]], [0x0D, [True, True]]], #mov reg->[reg]
[["mov", [all_mem, all_regs]], [0x0C, [True, True]]], #mov [reg]->reg
[["mov", [[-0xff], [3]]], [0x0D, [True, False]]], #mov x->ram
[["mov", [[-0xff], [4]]], [0x0E, [True, False]]], #mov y->ram
[["mov", [[-0xff], [5]]], [0x0F, [True, False]]], #mov a->ram
[["mov", [[-0xff], [6]]], [0x10, [True, False]]], #mov b->ram
[["mov", [[-0xff], [7]]], [0x11, [True, False]]], #mov acc->ram


[["maths", [all_regs, [0xff]]], [0x12, [True, True]]], #do maths

[["cmp", [all_regs, all_regs]], [0x13, [True, True]]],
[["cmp", [all_regs, [0xff]]], [0x14, [True, True]]],
[["test", [[0xff]]], [0x15, [True]]],
[["jmpr", [[0xff]]], [0x16, [True]]],
#relative register jump is useless
[["jmp", [[0xff]]], [0x18, [True]]],
[["jmp", [all_regs]], [0x19, [True]]],

[["push", [all_regs]], [0x1A, [True]]],
[["push", [[0xff]]], [0x1B, [True]]],
[["pop", [all_regs]], [0x1C, [True]]],
[["call", [[0xff]]], [0x1D, [True]]],
[["ret", []], [0x1E, []]],

[["inc", [all_regs]], [0x1F, [True]]],

[["num", [[0xff]]], [0xFF, [True]]]
]

#0 is 8bitbal
#1 is 16bitval
#2 is 8bit 0 padding
#4 is nothing
instruction_param = {
0x00 : [0,0],
0x01 : [1,4],
0x02 : [1,4],
0x03 : [1,4],
0x04 : [1,4],
0x05 : [1,4],
0x06 : [1,4],
0x07 : [1,4],
0x08 : [1,4],
0x09 : [1,4],
0x0A : [1,4],
0x0B : [0,0],
0x0C : [0,0],
0x0D : [1,4],
0x0E : [1,4],
0x0F : [1,4],
0x10 : [1,4],
0x11 : [1,4],
0x12 : [0,0],
0x13 : [0,0],
0x14 : [0,0],
0x15 : [0,2],
0x16 : [1,4],
0x17 : [0,0],
0x18 : [1,4],
0x19 : [0,2],
0x1A : [0,2],
0x1B : [1,4],
0x1C : [0,2],
0x1D : [1,4],
0x1E : [2,2],
0x1F : [0,2],
0xff : [1,4]
}

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
["and",0x07],["or", 0x08],["xor",0x09],["not",0x0A],["incr",0x0B],
#conditionals
["lt", 0x00],["gt",0x01],["leq",0x02],["geq",0x03],["eq",0x04],["neq",0x05]
]

def isnum(num):
	try:
		a = int(str(num), 10)
		return(True)
	except:
		pass
	try:
		a = int(str(num), 0x10)
		return(num[:2] == "0x")
	except:
		pass
	return(False)

def getnum(num):
	num = str(num).strip("[]")
	try:
		return(int(num,  10))
	except:
		pass
	try:
		return(int(num,0x10))
	except:
		pass
		return(0)


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
		is_imm = isnum(i)
		#todo - Make this 1000 times more complicated
		argtype = 0
		if(is_imm):
			argtype = 0xff
		else:
			argtype = regs[i]
		if(isaddr):
			argtype *= -1
		operands.append(argtype)
	
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
		if(inst != i[0][0]):
			failiure = True
		for j in range(num_args):
			if(operands[j] in arg_types[j]):
				pass
			else:
				failiure = True
		if(failiure == False):
			return(i[1])
	print(f"Error, Invalid instruction {instruction_data}")
	exit()


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

#structure:
#array of arrays containing:
#address and then an array of instruction id and paramaters

processed_instruction = []

for i in ins:
	tmp = [i[1][0][0]]
	for j in range(len(i[1][0][1])):
		if(i[1][0][1][j]):
			tmp.append(i[1][1+j])
	processed_instruction.append(tmp)


# print(processed_instruction)
#todo GETINT

instbytes = []

for i in processed_instruction:
	threebyteinst = [i[0]]
	for j in range(1,3):
		print(i)
		if(instruction_param[i[0]][j-1] == 0):
			if(isnum(i[j]) or isnum(str(i[j]).strip("[]"))):
				threebyteinst.append(getnum(i[j])%0x100)
			else:
				threebyteinst.append(regs[i[j].strip("[]")])
		elif(instruction_param[i[0]][j-1] == 1):
			if(isnum(i[j]) or isnum(str(i[j]).strip("[]"))):
				threebyteinst.append(getnum(i[j])%0x100)
				threebyteinst.append((getnum(i[j])>>8)%0x100)
			else:
				print("ERROR, Number expected")
				exit()
		elif(instruction_param[i[0]][j-1] == 2):
			threebyteinst.append(0x00)
	instbytes.append(threebyteinst)

#---------------------------------------
#PADDING ON 0x15 NOT OPERATING CORRECTLY
#---------------------------------------

bytesasnum = []
for i in instbytes:
	isval = False
	if(i[0] == 0xff):
		isval = True
	for j in range(len(i)):
		if(j !=0 or isval == False):
			bytesasnum.append(i[j])

print(bytesasnum)
bytesasbytes = bytes(bytesasnum)
print(bytesasbytes)
output = open("pytest.bin", "wb")
output.write(bytesasbytes)
output.close()