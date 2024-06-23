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
	lines[i] = lines[i].rstrip()

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

labeltable = []
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

for i in range(len(ins)):
	ins[i][1] = ins[i][1].split()
	for j in range(len(ins[i][1])):
		ins[i][1][j] = ins[i][1][j].strip(", \n()")

print(ins)
del(labeltable)