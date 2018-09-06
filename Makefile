
CFLAGS := -Wall -g
DEFS := $(DEFS) -D_GNU_SOURCE
LDFLAGS := -lm
CC   := gcc $(CFLAGS) $(INC) $(DEFS)
HEADERS :=
OBJS=calc_distances.o

%.o : %.c
	$(CC) -c $(CFLAGS) $*.c

calc_distances.o: calc_distances.c $(HEADERS)
get_distance.o: get_distance.c $(HEADERS)

calc_distances: $(OBJS)
	$(CC) $(LDFLAGS) $(OBJS) -o calc_distances

get_distance: get_distance.o
	$(CC) $(LDFLAGS) get_distance.o -o get_distance

clean:
	-rm -f *.o
	-rm -f calc_distances
	-rm -f get_distance

all:calc_distances get_distance

