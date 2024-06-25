#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

FILE* program;

//ram
uint8_t mem[0xffff];
//regs
#define SS 0
#define ISP 1
#define FLAGS 2
#define X 3
#define Y 4
#define A 5
#define B 6
#define ACC 7
uint16_t regs[ACC+1];

#define ss regs[SS]
#define isp regs[ISP]
#define flags regs[FLAGS]
#define x regs[X]
#define y regs[Y]
#define a regs[A]
#define b regs[B]
#define acc regs[ACC]

uint8_t getrombyte(uint16_t addr){
	fseek(program,addr,SEEK_SET);
	return(fgetc(program));
}

uint16_t word(uint8_t byte0, uint8_t byte1){
	return(byte0 + (byte1<<8));
}

void memwrite(uint16_t address, uint16_t value){
	mem[address] = value&0xff;
	mem[address+1] = value>>0x08;
}

uint16_t memread(uint16_t address){
	uint16_t tmp = mem[address];
	tmp += (mem[address+1]<<0x08);
	return(tmp);
}

void arith(uint8_t arg0, uint8_t arg1){
	switch(arg1){
			case 0x00:
				acc += regs[arg0];
				break;
			case 0x01:
				acc -= regs[arg0];
				break;
			case 0x02:
				acc *= regs[arg0];
				break;
			case 0x03:
				acc /= regs[arg0];
				break;
			case 0x04:
				acc %= regs[arg0];
				break;
			case 0x05:
				acc >>= regs[arg0];
				break;
			case 0x06:
				acc<<= regs[arg0];
				break;
			case 0x07:
				acc &= regs[arg0];
				break;
			case 0x08:
				acc |= regs[arg0];
				break;
			case 0x09:
				acc ^= regs[arg0];
				break;
			case 0x0A:
				acc ^= 0xffff;
				break;
	}
}

void push(uint16_t value){
	ss -=2;
	memwrite(ss, value);
}

void pop(uint8_t reg){
	regs[reg] = memread(ss);
	ss +=2;
}

void cmp(uint16_t val1, uint16_t val2){
	flags = 0;
	if(val1 < val2){flags |= 0x01;}
	if(val1 > val2){flags |= 0x02;}
	if(val1 == val2){flags|= 0x04;}
}

void test(uint8_t mode){
	switch(mode){
		case 0x00:
			if(!(flags&0x01)){isp +=3;}
			break;
		case 0x01:
			if(!(flags&0x02)){isp +=3;}
			break;
		case 0x02:
			if(!(flags&0x05)){isp +=3;}
			break;
		case 0x03:
			if(!(flags&0x06)){isp +=3;}
			break;
		case 0x04:
			if(!(flags&0x04)){isp +=3;}
			break;
		case 0x05:
			if(flags&0x05){isp +=3;}
			break;
	}
}


void exec(void){
	uint8_t instbyte = getrombyte(isp++);
	uint8_t arg0 = getrombyte(isp++); //dest
	uint8_t arg1 = getrombyte(isp++); //source
	switch(instbyte){
		case 0: // reg<-reg
			regs[arg0] = regs[arg1];
			break;
		case 1: //imm -> reg
		case 2:
		case 3:
		case 4:
		case 5:
			regs[instbyte-1+X] = word(arg0,arg1);
			break;
		case 6: //ram->reg
		case 7:
		case 8:
		case 9:
		case 0x0A:
			regs[instbyte-6+X] = memread(word(arg0, arg1));
			break;
		case 0x0B: //reg<-[reg]
			regs[arg0] = memread(regs[arg1]);
			break;
		case 0x0C: //[regs]<-reg
		memwrite(regs[arg0], regs[arg1]);
			break;
		case 0x0D: //reg->ram
		case 0x0E:
		case 0x0F:
		case 0x10:
		case 0x11:
			memwrite(word(arg0,arg1), regs[instbyte-0x0D+X]);
			break;
		case 0x12:
			arith(arg0, arg1);
			break;
		case 0x13:
			cmp(regs[arg0], regs[arg1]);
			break;
		case 0x14:
			cmp(regs[arg0], arg1);
			break;
		case 0x15:
			test(arg0);
			break;
		case 0x16:
			isp -=3;
			uint16_t imm = word(arg0,arg1);
			if(imm>>15 == 1){
				isp -= imm&0x7fff;
			}else{
				isp += imm;
			}
			break;
		case 0x17:
			isp -= 3;
			if(arg1 == 0){
				isp += regs[arg0];
			}else{
				isp -= regs[arg1];
			}
			break;
		case 0x18:
			isp = word(arg0, arg1);
			break;
		case 0x19:
			isp = regs[arg0];
			break;
		case 0x1A:
			push(regs[arg0]);
			break;
		case 0x1B:
			push(word(arg0,arg1));
			break;
		case 0x1C:
			pop(arg0);
			break;
		case 0x1D:
			push(isp);
			isp = word(arg0, arg1);
			break;
		case 0x1E:
			pop(ISP);





	}
}

int main(int arg, char *argc[]){
	if(arg < 2){
		printf("No arguments given\n");
		return(1);
	}
	program = fopen(argc[1],"r");
isp = 0;
//program loaded

while(1){
exec();
for(uint8_t i = 0; i <0xff; i++){
	printf("%u ", mem[i]);
}
printf("\n");
for(uint8_t i = 0; i <= ACC; i++){
	printf("%u ", regs[i]);
}
getchar();
}

return(0);
}