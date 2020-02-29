#include <stdio.h>
#include <unistd.h>

#include "c_gpio.h"
#include "py_gpio.h"
#include "py_pwm.h"

#define PIN 18

int main() {
  int result;

  int ret(int code) {
    gpio_cleanup();
    return code;
  }

  result = gpio_init();

  if (result) {
    printf("gpio_init failed with code %d\n", result);
    return ret(1);
  }

  result = gpio_setup_channel(PIN, OUTPUT, -1);

  if (result) {
    printf("setupPWM failed with code %d\n", result);
    return ret(2);
  }

  result = setupPWM(PIN, 350);

  if (result) {
    printf("setupPWM failed with code %d\n", result);
    return ret(3);
  }

  result = startPWM(PIN, 33);

  if (result) {
    printf("startPWM failed with code %d\n", result);
    return ret(4);
  }

  // Sleep for half a second
  usleep(500000);

  setDutyCycle(PIN, 66);

  // Sleep for 0.2s
  usleep(200000);

  setDutyCycle(PIN, 33);

  // Sleep for half a second
  usleep(500000);

  return ret(0);
}