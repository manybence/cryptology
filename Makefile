PROJECT_NAME = main

SRC = $(wildcard *.c)
OBJ = $(SRC:.c=.o)

$(PROJECT_NAME): $(OBJ)
	$(CC) -o $@ $^
	rm -f $(OBJ)

.PHONY: clean
clean:
	rm -f main
