#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <SDL2/SDL.h>
#include <stdbool.h>

#define pixel_size 4

#define x_res 128
#define y_res 128

#define x_size pixel_size*x_res
#define y_size pixel_size*y_res

Uint32 * pixels;


void setpixel_internal(uint32_t x, uint32_t y, uint32_t* video_mem, uint32_t colour){
	uint32_t ptr = (x_size*y)+x;
	video_mem[ptr] = colour;
}


void setpixel(uint16_t x, uint16_t y, uint32_t colour){
	x *= pixel_size;
	y *= pixel_size;
	for(uint8_t i = 0; i < pixel_size; i++){
		for(uint8_t j = 0; j < pixel_size; j++){
			setpixel_internal(x+i, y+j, pixels, colour);
		}
	}
}

uint8_t pixelarr[sizeof(uint32_t) * x_size * y_size];

SDL_Event event;
SDL_Texture * texture;
SDL_Renderer * renderer;
bool quit = false;
void init(){
	SDL_Init(SDL_INIT_VIDEO);
	SDL_Window * screen = SDL_CreateWindow("Emulator",
	SDL_WINDOWPOS_UNDEFINED, SDL_WINDOWPOS_UNDEFINED, x_size, y_size, 0);
	renderer = SDL_CreateRenderer(screen, -1, 0);
	texture = SDL_CreateTexture(renderer,
	SDL_PIXELFORMAT_ARGB8888, SDL_TEXTUREACCESS_STATIC, x_size, y_size);
	pixels = (uint32_t*)&pixelarr;
	memset(pixels, 255, x_size * y_size * sizeof(Uint32));
}


void lopb(){
	SDL_UpdateTexture(texture, NULL, pixels, x_size * sizeof(Uint32));
}


void lope(){
	SDL_RenderClear(renderer);
	SDL_RenderCopy(renderer, texture, NULL, NULL);
	SDL_RenderPresent(renderer);
}


void cleanup(){
	SDL_DestroyTexture(texture);
	SDL_DestroyRenderer(renderer);
	SDL_Quit();
}

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


__attribute__((always_inline)) inline uint8_t getrombyte(uint16_t addr){
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
			case 0x0B:
				acc++;
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
			break;
		case 0x1F:
			regs[arg0]++;
			break;





	}
}

#define uberpixel 4*4
#define uberpixelsize 16
#define superpixel 4*4
#define pixel 8*8

uint8_t grmodes[] = {
	4,8,16,32,64,128
};


uint32_t getcol(uint16_t enccol){
uint8_t rc,gc,bc;
bc = (enccol)&(31); //magic numbers
enccol >>= 5;
gc = (enccol)&(63);
enccol >>= 6;
rc = (enccol)&(31);
bc <<= 3;
gc <<= 2;
rc <<= 3;
uint32_t col = 0xff;
col <<= 8;
col |= rc;
col <<= 8;
col |= gc;
col <<= 8;
col |= bc;
return(col);
}


uint32_t getpixcolour(uint8_t xl, uint8_t yl, uint8_t res){
	uint16_t base = memread(0xff07);
	base += 2*(xl);
	base += 2*(yl)*res;
	return(getcol(memread(base)));
}

void screen_update(void){
	uint16_t mode = memread(0xff06);
	if(mode > 5){printf("ERROR"); return;}
	uint8_t res = grmodes[mode];
	uint8_t pixs = 128/res;
	printf("res: %d, pixs %d\n", res, pixs);
	for(uint8_t xi = 0; xi <x_res; xi++){
		for(uint8_t yi = 0; yi <y_res; yi++){
			uint8_t mpx, mpy;
			mpx = xi/pixs;
			mpy = yi/pixs;
			setpixel(xi, yi, getpixcolour(mpx, mpy, res));
		}
	}
}

void vblank(){
//update screen
screen_update();
//update controller

//interrupt
if(memread(0xff02) != 0){
printf("int\n");
push(isp);
isp = memread(0xff02);
}
}

#define inspe 1000

int main(int arg, char *argc[]){
	if(arg < 2){
		printf("No arguments given\n");
		return(1);
	}
program = fopen(argc[1],"r");
isp = 0;

init();

//program loaded 
//mruns ins for every enter press

uint16_t aks = 0;

while(1){
exec();
lopb();
/*
for(uint8_t i = 0; i <0xff; i++){
	printf("%u ", mem[i]);
}
printf("\n");
*/

if(aks%inspe == 0){
for(uint8_t i = 0; i <= ACC; i++){
	printf("%u ", regs[i]);
}printf("\n");

int inpu = getchar();
if(inpu == ' '){
	printf("VBLANK\n");
	vblank();
}
if(inpu == '0'){return(0);}
}aks++;
lope();
}


cleanup();
return(0);
}