/*! @file mission_sample.cpp
 *  @version 3.3
 *  @date Jun 05 2017
 *
 *  @brief
 *  GPS Missions API usage in a Linux environment.
 *  Shows example usage of the Waypoint Missions and Hotpoint Missions through
 * the
 *  Mission Manager API.
 *
 *  @Copyright (c) 2017 DJI
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 */

#include <iostream>
#include <fstream>
#include <sstream>
#include <dji_open_protocol.hpp>

#include <stdio.h>
#include <unistd.h>

#include "mission_sample.hpp"


//#include "./trigger/c_gpio.h"
#include "./trigger/py_gpio.h"
#include "./trigger/py_pwm.h"

using namespace DJI::OSDK;
using namespace DJI::OSDK::Telemetry;

#define PIN 18
#define OUTPUT 0

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

int trigger() {
  int result;

  result = main_setup();

  if (result) {
    printf("setup() failed with code %d\n", result);
    return die(1);
  }

  for (int i = 0; i < 10; ++i) {
    triggerCapture();
  }

  return 0;
}

void onWayPoint(Vehicle* vehicle, RecvContainer recvFrame, UserData userData) {
  std::cout << "\tWaypoint Index:" << (unsigned)recvFrame.recvData.wayPointReachedData.waypoint_index << '\n';
  std::cout << "\tIncident Type:" << (unsigned)recvFrame.recvData.wayPointReachedData.incident_type << '\n';
  std::cout << "\tCurrent Status:" << (unsigned)recvFrame.recvData.wayPointReachedData.current_status << '\n';
  trigger();
}

bool
runDPHMMission(Vehicle* vehicle, int responseTimeout)
{
  // Waypoint Mission : Initialization
  WayPointInitSettings fdata;
  setWaypointInitDefaults(&fdata);

  float32_t start_alt = 12;

  std::cout << "Initializing DPHM Mission..\n";

  // Obtain Control Authority
  ACK::ErrorCode ctrlAck = vehicle->obtainCtrlAuthority(responseTimeout);
  if (ACK::getError(ctrlAck)) {
    ACK::getErrorCodeMessage(ctrlAck, __func__);
  } else {
    std::cout << "Obtained drone control authority.\n";
  }

  ACK::ErrorCode initAck = vehicle->missionManager->init(DJI_MISSION_TYPE::WAYPOINT, responseTimeout, &fdata);
  if (ACK::getError(initAck)) {
    ACK::getErrorCodeMessage(initAck, __func__);
  }

  vehicle->missionManager->wpMission->setWaypointCallback(&onWayPoint, nullptr);
  vehicle->missionManager->wpMission->setWaypointEventCallback(&onWayPoint, nullptr);
  vehicle->missionManager->printInfo();

  // Waypoint Mission: Create Waypoints
  std::cout << "Creating Waypoints..\n";
  std::vector<WayPointSettings> generatedWaypts =
    createDPHMWaypoints(vehicle, start_alt);

  // Waypoint Mission: Upload the waypoints
  std::cout << "Uploading Waypoints..\n";
  uploadWaypoints(vehicle, generatedWaypts, responseTimeout);

  // Takeoff
  ACK::ErrorCode takeoffAck = vehicle->control->takeoff(responseTimeout);
  if (ACK::getError(takeoffAck))
  {
    ACK::getErrorCodeMessage(takeoffAck, __func__);

    if(takeoffAck.info.cmd_set == OpenProtocolCMD::CMDSet::control
       && takeoffAck.data == ErrorCode::CommonACK::START_MOTOR_FAIL_MOTOR_STARTED)
    {
      DSTATUS("Take off command sent failed. Please Land the drone and disarm the motors first.\n");
    }

    return false;
  }
  else
  {
    std::cout << "Took off. Waiting 15 seconds...\n";
    sleep(15);
  }


  std::cout << "Starting DPHM Mission.\n";
  // Waypoint Mission: Start
  ACK::ErrorCode startAck =
    vehicle->missionManager->wpMission->start(responseTimeout);
  if (ACK::getError(startAck))
  {
    ACK::getErrorCodeMessage(startAck, __func__);
  }
  else
  {
    std::cout << "Started DPHM Mission.\n";
  }

  // Counters
  int elapsedTimeInMs = 0;
  int timeToPrintInMs = 60000;

  // We will listen to five broadcast data sets:
  // 1. Flight Status
  // 2. Global Position
  // 3. RC Channels
  // 4. Velocity
  // 5. Quaternion
  // 6. Avoid obstacle data

  // Please make sure your drone is in simulation mode. You can
  // fly the drone with your RC to get different values.

  Telemetry::Status         status;
  Telemetry::GlobalPosition globalPosition;
  Telemetry::RC             rc;
  Telemetry::Vector3f       velocity;
  Telemetry::Quaternion     quaternion;

  const int TIMEOUT = 20;

  // Re-set Broadcast frequencies to their default values
  ACK::ErrorCode ack = vehicle->broadcast->setBroadcastFreqDefaults(TIMEOUT);

  // Print in a loop for x seconds
  while (elapsedTimeInMs < timeToPrintInMs)
  {
    // Matrice 100 broadcasts only flight status
    status         = vehicle->broadcast->getStatus();
    globalPosition = vehicle->broadcast->getGlobalPosition();
    rc             = vehicle->broadcast->getRC();
    velocity       = vehicle->broadcast->getVelocity();
    quaternion     = vehicle->broadcast->getQuaternion();

    std::cout << "Counter = " << elapsedTimeInMs << ":\n";
    std::cout << "-------\n";
    std::cout << "Flight Status (Flight, mode)          = "
              << (unsigned)status.flight << ", " << status.mode << "\n";
    std::cout << "Position              (LLA)           = "
              << globalPosition.latitude << ", " << globalPosition.longitude
              << ", " << globalPosition.altitude << "\n";
    std::cout << "RC Commands           (r/p/y/thr)     = " << rc.roll << ", "
              << rc.pitch << ", " << rc.yaw << ", " << rc.throttle << "\n";
    std::cout << "Velocity              (vx,vy,vz)      = " << velocity.x
              << ", " << velocity.y << ", " << velocity.z << "\n";
    std::cout << "Attitude Quaternion   (w,x,y,z)       = " << quaternion.q0
              << ", " << quaternion.q1 << ", " << quaternion.q2 << ", "
              << quaternion.q3 << "\n";
    std::cout << "-------\n\n";

    usleep(500000);
    elapsedTimeInMs += 500;
  }

  std::cout << "Done printing!\n";

  /*sleep(2000);

  // Stop
  std::cout << "Stop" << std::endl;
  ACK::ErrorCode stopAck =
    vehicle->missionManager->wpMission->stop(responseTimeout);

  std::cout << "Land" << std::endl;
  ACK::ErrorCode landAck = vehicle->control->land(responseTimeout);
  if (ACK::getError(landAck))
  {
    ACK::getErrorCodeMessage(landAck, __func__);
  }
  else
  {
    // No error. Wait for a few seconds to land
    sleep(10);
  }*/

  return true;
}

void
setWaypointDefaults(WayPointSettings* wp)
{
  wp->damping         = 0;
  wp->yaw             = 0;
  wp->gimbalPitch     = 0;
  wp->turnMode        = 0;
  wp->hasAction       = 1;
  wp->actionTimeLimit = 10000;
  wp->actionNumber    = 1;
  wp->actionRepeat    = 1;
  wp->commandList[0] = 0;
  wp->commandParameter[0] = 1000;
  for (int i = 1; i < 16; ++i)
  {
    wp->commandList[i]      = 0;
    wp->commandParameter[i] = 0;
  }
}

void
setWaypointInitDefaults(WayPointInitSettings* fdata)
{
  fdata->indexNumber    = 3;
  fdata->maxVelocity    = 2;
  fdata->idleVelocity   = 1;
  fdata->finishAction   = 0;
  fdata->executiveTimes = 1;
  fdata->yawMode        = 1;
  fdata->traceMode      = 0;
  fdata->RCLostAction   = 0;
  fdata->gimbalPitch    = 0;
  fdata->latitude       = 0.53436962199939;
  fdata->longitude      = -1.6627376835400;
  fdata->altitude       = 0;
}

std::vector<DJI::OSDK::WayPointSettings>
createDPHMWaypoints(DJI::OSDK::Vehicle* vehicle, float32_t start_alt)
{
  // Create Start Waypoint
  WayPointSettings start_wp;
  setWaypointDefaults(&start_wp);


  // Global position retrieved via broadcast
  Telemetry::GlobalPosition broadcastGPosition;

  broadcastGPosition = vehicle->broadcast->getGlobalPosition();
  start_wp.latitude  = broadcastGPosition.latitude;
  start_wp.longitude = broadcastGPosition.longitude;
  start_wp.altitude  = start_alt;
  /*printf("Waypoint created at (LLA): %f \t%f \t%f\n",
          broadcastGPosition.latitude, broadcastGPosition.longitude,
          start_alt);*/

  std::vector<DJI::OSDK::WayPointSettings> wpVector =
    generateWaypointsFromFile(&start_wp);
  return wpVector;
}

std::vector<DJI::OSDK::WayPointSettings>
generateWaypointsFromFile(WayPointSettings* start_data)
{
  // Let's create a vector to store our waypoints in.
  std::vector<DJI::OSDK::WayPointSettings> wp_list;

  // First waypoint
  start_data->index = (uint8_t) 0;
  // wp_list.push_back(*start_data);

  // Read in waypoints from file
  std::ifstream inFile;
  inFile.open("/home/test_points.txt"); // @todo: decide where the waypoints file will be located
  // waypoints file: each line should be
  //lat lon alt
  std::string line;
  uint8_t i = 0;

  while(std::getline(inFile, line)) {
    if(line == "") {
      break;
    }

    std::istringstream ss(line);

    std::string lat_str;
    std::string lon_str;
    std::string alt_str;

    ss >> lat_str;
    ss >> lon_str;
    ss >> alt_str;

    double latitude = std::stod(lat_str);
    double longitude = std::stod(lon_str);
    double altitude = std::stod(alt_str);
    double pi = 3.14159265358979323846;

    latitude = (latitude / 360) * 2 * pi;
    longitude = (longitude / 360) * 2 * pi;

    WayPointSettings wp;
    setWaypointDefaults(&wp);
    wp.index     = i;
    wp.latitude  = latitude;
    wp.longitude = longitude;
    wp.altitude  = altitude;
    // wp.toString();
    wp_list.push_back(wp);

    i++;
  }

  // Come back home
  //start_data->index = num_wp;
  //wp_list.push_back(*start_data);

  return wp_list;
}

void
uploadWaypoints(Vehicle*                                  vehicle,
                std::vector<DJI::OSDK::WayPointSettings>& wp_list,
                int                                       responseTimeout)
{
  for (std::vector<WayPointSettings>::iterator wp = wp_list.begin();
       wp != wp_list.end(); ++wp)
  {
    printf("Waypoint created at (LLA): %f \t%f \t%f\n ", wp->latitude,
           wp->longitude, wp->altitude);
    ACK::WayPointIndex wpDataACK =
      vehicle->missionManager->wpMission->uploadIndexData(&(*wp),
                                                          responseTimeout);

    ACK::getErrorCodeMessage(wpDataACK.ack, __func__);
  }
}
