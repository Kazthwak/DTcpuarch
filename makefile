.PHONY: run

default: run

run: emu
	@./emu test

a.out: emu.c
	@gcc emu.c -o emu
