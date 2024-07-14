.PHONY: run

default: run

run: emu
	@./emu pytest.bin

emu: emu.c
	@gcc emu.c -lSDL2main -lSDL2 -o emu
