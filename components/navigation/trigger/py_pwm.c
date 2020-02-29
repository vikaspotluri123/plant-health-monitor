/*
Copyright (c) 2013-2018 Ben Croston

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

#include "soft_pwm.h"
#include "py_pwm.h"
#include "common.h"
#include "c_gpio.h"

typedef struct
{
    unsigned int gpio;
    float freq;
    float dutycycle;
} PWMObject;

void _requireSetup(char* method) {
    printf("You need to setupPWM() before calling %s\n", method);
}

int setupPWM(unsigned int channel, float frequency) {
    // does soft pwm already exist on this channel?
    if (pwm_exists(channel)) {
        printf("A PWM object already exists for channel%d\n", channel);
        return 1;
    }

    // ensure channel set as output
    if (gpio_direction[channel] != OUTPUT) {
        printf("You must gpio_setup_pin() channel %d first\n", channel);
        return 2;
    }

    if (frequency <= 0.0) {
        printf("frequency must be greater than 0.0\n");
        return 3;
    }

    pwm_set_frequency(channel, frequency);
    return 0;
}

int startPWM(unsigned int channel, float dutyCycle) {
    if (!pwm_exists(channel)) {
        _requireSetup("startPWM");
        return 1;
    }

    if (dutyCycle < 0.0 || dutyCycle > 100.0) {
        printf("dutycycle must have a value from 0.0 to 100.0\n");
        return 2;
    }

    pwm_set_duty_cycle(channel, dutyCycle);
    pwm_start(channel);
    return 0;
}

int setDutyCycle(unsigned int channel, float dutyCycle) {
    if (!pwm_exists(channel)) {
        _requireSetup("setDutyCycle");
        return 1;
    }

    if (dutyCycle < 0.0 || dutyCycle > 100.0) {
        printf("dutycycle must have a value from 0.0 to 100.0\n");
        return 2;
    }

    pwm_set_duty_cycle(channel, dutyCycle);
    return 0;
}

int setFrequency(unsigned int channel, float frequency) {
    if (!pwm_exists(channel)) {
        _requireSetup("setFrequency");
        return 1;
    }

    if (frequency <= 0.0) {
        printf("frequency must be greater than 0.0\n");
        return 1;
    }

    pwm_set_frequency(channel, frequency);
    return 0;
}

int stopPWM(unsigned int channel) {
    if (!pwm_exists(channel)) {
        _requireSetup("stopPWM");
        return 1;
    }

    pwm_stop(channel);
    return 0;
}
