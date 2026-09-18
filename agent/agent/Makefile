# Reproducible build rules for the Linux monitoring agent.
# Author: Leslie Raya
# GitHub: https://github.com/leslieraya555

CC ?= gcc
CFLAGS ?= -std=c11 -Wall -Wextra -Wpedantic -Werror -O2

.PHONY: all clean

all: monitor

monitor: monitor.c
	$(CC) $(CFLAGS) monitor.c -o monitor

clean:
	$(RM) monitor