CC=gcc
CFLAGS=-c -Wall -lpthread

all: trigger

trigger: main.o c_gpio.o common.o cpuinfo.o py_gpio.o py_pwm.o soft_pwm.o
	$(CC) main.o c_gpio.o common.o cpuinfo.o py_gpio.o py_pwm.o soft_pwm.o -o trigger -lpthread

main.o: main.c
	$(CC) $(CFLAGS) main.c

c_gpio.o: c_gpio.c c_gpio.h
	$(CC) $(CFLAGS) c_gpio.c

common.o: common.c common.h
	$(CC) $(CFLAGS) common.c

cpuinfo.o: cpuinfo.c cpuinfo.h
	$(CC) $(CFLAGS) cpuinfo.c

py_gpio.o: py_gpio.c
	$(CC) $(CFLAGS) py_gpio.c

py_pwm.o: py_pwm.c py_pwm.h
	$(CC) $(CFLAGS) py_pwm.c

soft_pwm.o: soft_pwm.c soft_pwm.h
	$(CC) $(CFLAGS) soft_pwm.c

clean:
	rm -f trigger *.o