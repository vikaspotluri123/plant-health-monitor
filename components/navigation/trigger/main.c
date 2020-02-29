#include <stdio.h>
#include "py_gpio.h"
#include "py_pwm.h"

int main() {
  write(stdout, "Testing", sizeof("Testing"));

  gpio_init();
  gpio_cleanup();
  return 0;
}