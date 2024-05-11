CC=gcc
CPP=g++
CFLAGS=-O3
CPPFLAGS=-std=c++20

BDDOBJ=BDD/bdd_cache.o  BDD/bdd_double.o  BDD/bdd_dump.o  BDD/bdd_external.o  BDD/bdd_manager.o  BDD/bdd.o  BDD/bdd_trace.o  BDD/hash.o

DFAOBJ=DFA/analyze.o  DFA/basic.o  DFA/dfa.o  DFA/external.o  DFA/makebasic.o  DFA/minimize.o  DFA/prefix.o  DFA/printdfa.o  DFA/product.o  DFA/project.o  DFA/quotient.o

MemOBJ=Mem/dlmalloc.o  Mem/mem.o

all: composition projection apply-literal apply-language

BDD/%.o: BDD/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

DFA/%.o: DFA/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

Mem/%.o: Mem/%.c
	$(CC) $(CFLAGS) -c -o $@ $<

main: main.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o main main.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)

main.o: main.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c main.cc

projection.o: projection.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c projection.cc

composition.o: composition.cc
	$(CPP) $(CFLAGS) $(CPPFLAGS) -c composition.cc

apply-literal.o: apply-literal.cc
	$(CPP) $(CFLAGS) $(CPPFLAGS) -c apply-literal.cc

apply-language.o: apply-language.cc
	$(CPP) $(CFLAGS) $(CPPFLAGS) -c apply-language.cc

expand_composition_inputs.o: expand_composition_inputs.cc
	$(CPP) $(CFLAGS) $(CPPFLAGS) -c expand_composition_inputs.cc

projection: projection.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o projection projection.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)

composition: composition.o expand_composition_inputs $(BDDOBJ) $(DFAOBJ) $(MemOBJ)
	$(CPP) $(CFLAGS) $(CPPFLAGS) -o composition composition.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)

apply-literal: apply-literal.o expand_composition_inputs $(BDDOBJ) $(DFAOBJ) $(MemOBJ)
	$(CPP) $(CFLAGS) $(CPPFLAGS) -o apply-literal apply-literal.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)

apply-language: apply-language.o expand_composition_inputs $(BDDOBJ) $(DFAOBJ) $(MemOBJ)
	$(CPP) $(CFLAGS) $(CPPFLAGS) -o apply-language apply-language.o $(BDDOBJ) $(DFAOBJ) $(MemOBJ)

expand_composition_inputs: expand_composition_inputs.o
	$(CPP) $(CFLAGS) $(CPPFLAGS) -o expand_composition_inputs expand_composition_inputs.o -lmata

.PHONY: clean
clean:
	rm $(BDDOBJ) $(DFAOBJ) $(MemOBJ) main main.o projection projection.o composition composition.o apply-literal apply-literal.o apply-language apply-language.o
