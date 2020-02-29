#include <stdio.h>
#include <unistd.h>

#include "c_gpio.h"
#include "py_gpio.h"
#include "py_pwm.h"

#define PIN 18

int main_setup() {
  int result;
  result = gpio_init();

  if (result) {
    printf("gpio_init failed with code %d\n", result);
    return 1;
  }

  result = gpio_setup_channel(PIN, OUTPUT, -1);

  if (result) {
    printf("setupPWM failed with code %d\n", result);
    return 2;
  }

  result = setupPWM(PIN, 350);

  if (result) {
    printf("setupPWM failed with code %d\n", result);
    return 3;
  }

  result = startPWM(PIN, 33);

  if (result) {
    printf("startPWM failed with code %d\n", result);
    return 4;
  }

  return 0;
}

void triggerCapture() {
  printf("Start Trigger Capture\n");
  setDutyCycle(PIN, 66);

  // Sleep for 0.2s
  usleep(200000);

  setDutyCycle(PIN, 33);

  // Sleep for 2s
  usleep(2000000);
  printf("Stop Trigger Capture\n");
}

int die(int code) {
  gpio_cleanup();
  return code;
}

int main() {
  int result;

  result = main_setup();

  if (result) {
    printf("setup() failed with code %d\n", result);
    return die(1);
  }

  for (int i = 0; i < 10; ++i) {
    triggerCapture();
  }
}