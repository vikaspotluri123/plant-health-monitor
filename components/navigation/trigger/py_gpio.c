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

#include "Python.h"
#include "c_gpio.h"
#include "event_gpio.h"
#include "py_pwm.h"
#include "cpuinfo.h"
#include "constants.h"
#include "common.h"

static PyObject *rpi_revision; // deprecated
static PyObject *board_info;
static int gpio_warnings = 1;

struct py_callback
{
   unsigned int gpio;
   PyObject *py_cb;
   struct py_callback *next;
};
static struct py_callback *py_callbacks = NULL;

static int mmap_gpio_mem(void)
{
   int result;

   if (module_setup)
      return 0;

   result = setup();
   if (result == SETUP_DEVMEM_FAIL)
   {
      PyErr_SetString(PyExc_RuntimeError, "No access to /dev/mem.  Try running as root!");
      return 1;
   } else if (result == SETUP_MALLOC_FAIL) {
      PyErr_NoMemory();
      return 2;
   } else if (result == SETUP_MMAP_FAIL) {
      PyErr_SetString(PyExc_RuntimeError, "Mmap of GPIO registers failed");
      return 3;
   } else if (result == SETUP_CPUINFO_FAIL) {
      PyErr_SetString(PyExc_RuntimeError, "Unable to open /proc/cpuinfo");
      return 4;
   } else if (result == SETUP_NOT_RPI_FAIL) {
      PyErr_SetString(PyExc_RuntimeError, "Not running on a RPi!");
      return 5;
   } else { // result == SETUP_OK
      module_setup = 1;
      return 0;
   }
}

// python function cleanup(channel=None)
static PyObject *py_cleanup(PyObject *self, PyObject *args, PyObject *kwargs)
{
   int i;
   int chancount = -666;
   int found = 0;
   int channel = -666;
   unsigned int gpio;
   PyObject *chanlist = NULL;
   PyObject *chantuple = NULL;
   PyObject *tempobj;
   static char *kwlist[] = {"channel", NULL};

   void cleanup_one(void)
   {
      // clean up any /sys/class exports
      event_cleanup(gpio);

      // set everything back to input
      if (gpio_direction[gpio] != -1) {
         setup_gpio(gpio, INPUT, PUD_OFF);
         gpio_direction[gpio] = -1;
         found = 1;
      }
   }

   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "|O", kwlist, &chanlist))
      return NULL;

   if (chanlist == NULL) {  // channel kwarg not set
      // do nothing
   } else if (PyLong_Check(chanlist)) {
      channel = (int)PyLong_AsLong(chanlist);
      if (PyErr_Occurred())
         return NULL;
      chanlist = NULL;
   } else if (PyList_Check(chanlist)) {
      chancount = PyList_Size(chanlist);
   } else if (PyTuple_Check(chanlist)) {
      chantuple = chanlist;
      chanlist = NULL;
      chancount = PyTuple_Size(chantuple);
   } else {
      // raise exception
      PyErr_SetString(PyExc_ValueError, "Channel must be an integer or list/tuple of integers");
      return NULL;
   }

   if (module_setup && !setup_error) {
      if (channel == -666 && chancount == -666) {   // channel not set - cleanup everything
         // clean up any /sys/class exports
         event_cleanup_all();

         // set everything back to input
         for (i=0; i<54; i++) {
            if (gpio_direction[i] != -1) {
               setup_gpio(i, INPUT, PUD_OFF);
               gpio_direction[i] = -1;
               found = 1;
            }
         }
         gpio_mode = MODE_UNKNOWN;
      } else if (channel != -666) {    // channel was an int indicating single channel
         if (get_gpio_number(channel, &gpio))
            return NULL;
         cleanup_one();
      } else {  // channel was a list/tuple
         for (i=0; i<chancount; i++) {
            if (chanlist) {
               if ((tempobj = PyList_GetItem(chanlist, i)) == NULL) {
                  return NULL;
               }
            } else { // assume chantuple
               if ((tempobj = PyTuple_GetItem(chantuple, i)) == NULL) {
                  return NULL;
               }
            }

            if (PyLong_Check(tempobj)) {
               channel = (int)PyLong_AsLong(tempobj);
               if (PyErr_Occurred())
                  return NULL;
            } else {
               PyErr_SetString(PyExc_ValueError, "Channel must be an integer");
               return NULL;
            }

            if (get_gpio_number(channel, &gpio))
               return NULL;
            cleanup_one();
         }
      }
   }

   // check if any channels set up - if not warn about misuse of GPIO.cleanup()
   if (!found && gpio_warnings) {
      PyErr_WarnEx(NULL, "No channels have been set up yet - nothing to clean up!  Try cleaning up at the end of your program instead!", 1);
   }

   Py_RETURN_NONE;
}

// python function setup(channel(s), direction, pull_up_down=PUD_OFF, initial=None)
static PyObject *py_setup_channel(PyObject *self, PyObject *args, PyObject *kwargs)
{
   unsigned int gpio;
   int channel = -1;
   int direction;
   int i, chancount;
   PyObject *chanlist = NULL;
   PyObject *chantuple = NULL;
   PyObject *tempobj;
   int pud = PUD_OFF + PY_PUD_CONST_OFFSET;
   int initial = -1;
   static char *kwlist[] = {"channel", "direction", "pull_up_down", "initial", NULL};
   int func;

   int setup_one(void) {
      if (get_gpio_number(channel, &gpio))
         return 0;

      func = gpio_function(gpio);
      if (gpio_warnings &&                             // warnings enabled and
          ((func != 0 && func != 1) ||                 // (already one of the alt functions or
          (gpio_direction[gpio] == -1 && func == 1)))  // already an output not set from this program)
      {
         PyErr_WarnEx(NULL, "This channel is already in use, continuing anyway.  Use GPIO.setwarnings(False) to disable warnings.", 1);
      }

      // warn about pull/up down on i2c channels
      if (gpio_warnings) {
         if (rpiinfo.p1_revision == 0) { // compute module - do nothing
         } else if ((rpiinfo.p1_revision == 1 && (gpio == 0 || gpio == 1)) ||
                    (gpio == 2 || gpio == 3)) {
            if (pud == PUD_UP || pud == PUD_DOWN)
               PyErr_WarnEx(NULL, "A physical pull up resistor is fitted on this channel!", 1);
         }
      }

      if (direction == OUTPUT && (initial == LOW || initial == HIGH)) {
         output_gpio(gpio, initial);
      }
      setup_gpio(gpio, direction, pud);
      gpio_direction[gpio] = direction;
      return 1;
   }

   if (!PyArg_ParseTupleAndKeywords(args, kwargs, "Oi|ii", kwlist, &chanlist, &direction, &pud, &initial))
      return NULL;

   if (PyLong_Check(chanlist)) {
      channel = (int)PyLong_AsLong(chanlist);
      if (PyErr_Occurred())
         return NULL;
      chanlist = NULL;
   } else if (PyList_Check(chanlist)) {
      // do nothing
   } else if (PyTuple_Check(chanlist)) {
      chantuple = chanlist;
      chanlist = NULL;
   } else {
      // raise exception
      PyErr_SetString(PyExc_ValueError, "Channel must be an integer or list/tuple of integers");
      return NULL;
   }

   // check module has been imported cleanly
   if (setup_error)
   {
      PyErr_SetString(PyExc_RuntimeError, "Module not imported correctly!");
      return NULL;
   }

   if (mmap_gpio_mem())
      return NULL;

   if (direction != INPUT && direction != OUTPUT) {
      PyErr_SetString(PyExc_ValueError, "An invalid direction was passed to setup()");
      return 0;
   }

   if (direction == OUTPUT && pud != PUD_OFF + PY_PUD_CONST_OFFSET) {
      PyErr_SetString(PyExc_ValueError, "pull_up_down parameter is not valid for outputs");
      return 0;
   }

   if (direction == INPUT && initial != -1) {
      PyErr_SetString(PyExc_ValueError, "initial parameter is not valid for inputs");
      return 0;
   }

   if (direction == OUTPUT)
      pud = PUD_OFF + PY_PUD_CONST_OFFSET;

   pud -= PY_PUD_CONST_OFFSET;
   if (pud != PUD_OFF && pud != PUD_DOWN && pud != PUD_UP) {
      PyErr_SetString(PyExc_ValueError, "Invalid value for pull_up_down - should be either PUD_OFF, PUD_UP or PUD_DOWN");
      return NULL;
   }

   if (chanlist) {
       chancount = PyList_Size(chanlist);
   } else if (chantuple) {
       chancount = PyTuple_Size(chantuple);
   } else {
       if (!setup_one())
          return NULL;
       Py_RETURN_NONE;
   }

   for (i=0; i<chancount; i++) {
      if (chanlist) {
         if ((tempobj = PyList_GetItem(chanlist, i)) == NULL) {
            return NULL;
         }
      } else { // assume chantuple
         if ((tempobj = PyTuple_GetItem(chantuple, i)) == NULL) {
            return NULL;
         }
      }

      if (PyLong_Check(tempobj)) {
         channel = (int)PyLong_AsLong(tempobj);
         if (PyErr_Occurred())
             return NULL;
      } else {
          PyErr_SetString(PyExc_ValueError, "Channel must be an integer");
          return NULL;
      }

      if (!setup_one())
         return NULL;
   }

   Py_RETURN_NONE;
}

// python function setmode(mode)
static PyObject *py_setmode(PyObject *self, PyObject *args)
{
   int new_mode;

   if (!PyArg_ParseTuple(args, "i", &new_mode))
      return NULL;

   if (gpio_mode != MODE_UNKNOWN && new_mode != gpio_mode)
   {
      PyErr_SetString(PyExc_ValueError, "A different mode has already been set!");
      return NULL;
   }

   if (setup_error)
   {
      PyErr_SetString(PyExc_RuntimeError, "Module not imported correctly!");
      return NULL;
   }

   if (new_mode != BOARD && new_mode != BCM)
   {
      PyErr_SetString(PyExc_ValueError, "An invalid mode was passed to setmode()");
      return NULL;
   }

   if (rpiinfo.p1_revision == 0 && new_mode == BOARD)
   {
      PyErr_SetString(PyExc_RuntimeError, "BOARD numbering system not applicable on compute module");
      return NULL;
   }

   gpio_mode = new_mode;
   Py_RETURN_NONE;
}

static unsigned int chan_from_gpio(unsigned int gpio)
{
   int chan;
   int chans;

   if (gpio_mode == BCM)
      return gpio;
   if (rpiinfo.p1_revision == 0)   // not applicable for compute module
      return -1;
   else if (rpiinfo.p1_revision == 1 || rpiinfo.p1_revision == 2)
      chans = 26;
   else
      chans = 40;
   for (chan=1; chan<=chans; chan++)
      if (*(*pin_to_gpio+chan) == (int)gpio)
         return chan;
   return -1;
}

static void run_py_callbacks(unsigned int gpio)
{
   PyObject *result;
   PyGILState_STATE gstate;
   struct py_callback *cb = py_callbacks;

   while (cb != NULL)
   {
      if (cb->gpio == gpio) {
         // run callback
         gstate = PyGILState_Ensure();
         result = PyObject_CallFunction(cb->py_cb, "i", chan_from_gpio(gpio));
         if (result == NULL && PyErr_Occurred()){
            PyErr_Print();
            PyErr_Clear();
         }
         Py_XDECREF(result);
         PyGILState_Release(gstate);
      }
      cb = cb->next;
   }
}

static int add_py_callback(unsigned int gpio, PyObject *cb_func)
{
   struct py_callback *new_py_cb;
   struct py_callback *cb = py_callbacks;

   // add callback to py_callbacks list
   new_py_cb = malloc(sizeof(struct py_callback));
   if (new_py_cb == 0)
   {
      PyErr_NoMemory();
      return -1;
   }
   new_py_cb->py_cb = cb_func;
   Py_XINCREF(cb_func);         // Add a reference to new callback
   new_py_cb->gpio = gpio;
   new_py_cb->next = NULL;
   if (py_callbacks == NULL) {
      py_callbacks = new_py_cb;
   } else {
      // add to end of list
      while (cb->next != NULL)
         cb = cb->next;
      cb->next = new_py_cb;
   }
   add_edge_callback(gpio, run_py_callbacks);
   return 0;
}

// python function setwarnings(state)
static PyObject *py_setwarnings(PyObject *self, PyObject *args)
{
   if (!PyArg_ParseTuple(args, "i", &gpio_warnings))
      return NULL;

   if (setup_error)
   {
      PyErr_SetString(PyExc_RuntimeError, "Module not imported correctly!");
      return NULL;
   }

   Py_RETURN_NONE;
}

static struct PyModuleDef rpigpiomodule = {
   PyModuleDef_HEAD_INIT,
   "RPi._GPIO",      // name of module
   moduledocstring,  // module documentation, may be NULL
   -1,               // size of per-interpreter state of the module, or -1 if the module keeps state in global variables.
   rpi_gpio_methods
};

PyMODINIT_FUNC PyInit__GPIO(void)
{
   int i;
   PyObject *module = NULL;

   if ((module = PyModule_Create(&rpigpiomodule)) == NULL)
      return NULL;

   define_constants(module);

   for (i=0; i<54; i++)
      gpio_direction[i] = -1;

   // detect board revision and set up accordingly
   if (get_rpi_info(&rpiinfo))
   {
      PyErr_SetString(PyExc_RuntimeError, "This module can only be run on a Raspberry Pi!");
      setup_error = 1;
      return NULL;
   }
   board_info = Py_BuildValue("{sissssssssss}",
                              "P1_REVISION",rpiinfo.p1_revision,
                              "REVISION",&rpiinfo.revision,
                              "TYPE",rpiinfo.type,
                              "MANUFACTURER",rpiinfo.manufacturer,
                              "PROCESSOR",rpiinfo.processor,
                              "RAM",rpiinfo.ram);
   PyModule_AddObject(module, "RPI_INFO", board_info);

   if (rpiinfo.p1_revision == 1) {
      pin_to_gpio = &pin_to_gpio_rev1;
   } else if (rpiinfo.p1_revision == 2) {
      pin_to_gpio = &pin_to_gpio_rev2;
   } else { // assume model B+ or A+ or 2B
      pin_to_gpio = &pin_to_gpio_rev3;
   }

   rpi_revision = Py_BuildValue("i", rpiinfo.p1_revision);     // deprecated
   PyModule_AddObject(module, "RPI_REVISION", rpi_revision);   // deprecated

   // Add PWM class
   if (PWM_init_PWMType() == NULL)
      return NULL;
   Py_INCREF(&PWMType);
   PyModule_AddObject(module, "PWM", (PyObject*)&PWMType);

   if (!PyEval_ThreadsInitialized())
      PyEval_InitThreads();

   // register exit functions - last declared is called first
   if (Py_AtExit(cleanup) != 0)
   {
      setup_error = 1;
      cleanup();
      return NULL;
   }

   if (Py_AtExit(event_cleanup_all) != 0)
   {
      setup_error = 1;
      cleanup();
      return NULL;
   }

   return module;
}
