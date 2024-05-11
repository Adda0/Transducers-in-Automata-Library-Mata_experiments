CC=gcc
CPP=g++
CFLAGS=-O3
CPPFLAGS=-std=c++20

all: composition projection apply-literal apply-language

projection: projection.o
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o projection projection.o -lmata

projection.o: projection.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c projection.cc

composition: composition.o
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o composition composition.o -lmata

composition.o: composition.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c composition.cc

apply-literal: apply-literal.o
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o apply-literal apply-literal.o -lmata

apply-literal.o: apply-literal.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c apply-literal.cc

apply-language: apply-language.o
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -o apply-language apply-language.o -lmata

apply-language.o: apply-language.cc
	$(CPP)  $(CFLAGS) $(CPPFLAGS) -c apply-language.cc

.PHONY: clean
clean:
	rm projection projection.o composition composition.o apply-literal apply-literal.o apply-language apply-language.o
