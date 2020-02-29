/*
Copyright (c) 2012-2016 Ben Croston

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

#include <stdio.h>

#include "c_gpio.h"
#include "py_pwm.h"
#include "common.h"

#define GPIO_WARNINGS 1

int hasSetup = 0;

int mmap_gpio_mem(void) {
   int result;

   if (hasSetup)
      return 0;

   result = setup();
   if (result == SETUP_DEVMEM_FAIL) {
      printf("No access to /dev/mem. Try running as root?\n");
      return 1;
   } else if (result == SETUP_MALLOC_FAIL) {
      printf("No Memory\n");
      return 2;
   } else if (result == SETUP_MMAP_FAIL) {
      printf("Mmap of GPIO registers failed\n");
      return 3;
   } else if (result == SETUP_CPUINFO_FAIL) {
      printf("Unable to open /proc/cpuinfo\n");
      return 4;
   } else if (result == SETUP_NOT_RPI_FAIL) {
      printf("Not running on a RPi!\n");
      return 5;
   } else { // result == SETUP_OK
      hasSetup = 1;
      return 0;
   }
}

int gpio_cleanup() {
   // set everything back to input
   for (int i = 0; i < 54; ++i) {
      if (gpio_direction[i] != -1) {
         setup_gpio(i, INPUT, PUD_OFF);
         gpio_direction[i] = -1;
      }
   }

   return 0;
}

// @NOTE: The only mode this program supports is BCM
int gpio_setup_channel(int channel, int direction, int initial) {
   unsigned int gpio;
   int pud = PUD_OFF;
   int func;

   if (mmap_gpio_mem()) {
      return 1;
   }

   if (direction != INPUT && direction != OUTPUT) {
      printf("Invalid direction\n");
      return 2;
   }

   func = gpio_function(gpio);
   if (GPIO_WARNINGS && (
      (func != 0 && func != 1) || // already one of the alt functions or
      (gpio_direction[gpio] == -1 && func == 1) // already an output not set from this program
   )) {
      printf("This channel is already in use, continuing anyway.\n");
   }

   if (direction == OUTPUT && (initial == LOW || initial == HIGH)) {
      output_gpio(gpio, initial);
   }

   setup_gpio(gpio, direction, pud);
   gpio_direction[gpio] = direction;
   return 0;
}

int gpio_init() {
   for (int i = 0; i < 54; ++i) {
      gpio_direction[i] = -1;
   }

   // detect board revision and set up accordingly
   if (get_rpi_info(&rpiinfo)) {
      printf("This module can only be run on a Raspberry Pi!\n");
      return 1;
   }

   if (rpiinfo.p1_revision == 1) {
      pin_to_gpio = &pin_to_gpio_rev1;
   } else if (rpiinfo.p1_revision == 2) {
      pin_to_gpio = &pin_to_gpio_rev2;
   } else { // assume model B+ or A+ or 2B
      pin_to_gpio = &pin_to_gpio_rev3;
   }

   return 0;
}
