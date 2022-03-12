all: make_animation

clean:
	rm -f bitgrid.o make_animation.o make_animation

build: clean all

.PHONY: all clean build

CXXFLAGS=-Wall -Wextra -Werror

%.o: %.cpp
	g++ $(CXXFLAGS) -c -o $@ $<

make_animation.o: make_animation.cpp bitgrid.h constants.h
bitgrid.o: bitgrid.cpp bitgrid.h

make_animation: make_animation.o bitgrid.o
	g++ $(CXXFLAGS) $(LDFLAGS) -o $@ $^ -lz
