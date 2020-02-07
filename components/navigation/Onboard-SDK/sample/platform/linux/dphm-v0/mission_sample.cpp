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

#include <fstream>
#include <sstream>
#include "mission_sample.hpp"

using namespace DJI::OSDK;
using namespace DJI::OSDK::Telemetry;

bool
runDPHMMission(Vehicle* vehicle, int responseTimeout)
{
  // Waypoint Mission : Initialization
  WayPointInitSettings fdata;
  setWaypointInitDefaults(&fdata);

  float64_t increment = 0.000001;
  float32_t start_alt = 10;

  std::cout << "Initializing DPHM Mission..\n";
  ACK::ErrorCode initAck = vehicle->missionManager->init(
    DJI_MISSION_TYPE::WAYPOINT, responseTimeout, &fdata);
  if (ACK::getError(initAck))
  {
    ACK::getErrorCodeMessage(initAck, __func__);
  }

  vehicle->missionManager->printInfo();

  // Waypoint Mission: Create Waypoints
  std::cout << "Creating Waypoints..\n";
  std::vector<WayPointSettings> generatedWaypts =
    createDPHMWaypoints(vehicle, start_alt);

  // Waypoint Mission: Upload the waypoints
  std::cout << "Uploading Waypoints..\n";
  uploadWaypoints(vehicle, generatedWaypts, responseTimeout);

  // Waypoint Mission: Start
  ACK::ErrorCode startAck =
    vehicle->missionManager->wpMission->start(responseTimeout);
  if (ACK::getError(startAck))
  {
    ACK::getErrorCodeMessage(initAck, __func__);
  }
  else
  {
    std::cout << "Starting DPHM Mission.\n";
  }

  // The mission isn't done yet, but it doesn't need any
  // more input from our side.

  return true;
}

void
setWaypointDefaults(WayPointSettings* wp)
{
  wp->damping         = 0;
  wp->yaw             = 0;
  wp->gimbalPitch     = 0;
  wp->turnMode        = 0;
  wp->hasAction       = 0;
  wp->actionTimeLimit = 100;
  wp->actionNumber    = 0;
  wp->actionRepeat    = 0;
  for (int i = 0; i < 16; ++i)
  {
    wp->commandList[i]      = 0;
    wp->commandParameter[i] = 0;
  }
}

void
setWaypointInitDefaults(WayPointInitSettings* fdata)
{
  fdata->maxVelocity    = 10;
  fdata->idleVelocity   = 5;
  fdata->finishAction   = 0;
  fdata->executiveTimes = 1;
  fdata->yawMode        = 0;
  fdata->traceMode      = 0;
  fdata->RCLostAction   = 1;
  fdata->gimbalPitch    = 0;
  fdata->latitude       = 0;
  fdata->longitude      = 0;
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
  printf("Waypoint created at (LLA): %f \t%f \t%f\n",
          broadcastGPosition.latitude, broadcastGPosition.longitude,
          start_alt);

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
  start_data->index = 0;
  wp_list.push_back(*start_data);

  // Read in waypoints from file
  std::ifstream inFile;
  inFile.open("/home/......"); // @todo: decide where the waypoints file will be located
  // waypoints file: each line should be 
  //lat lon alt
  std::string line;
  int i = 1;
  
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
    
    double latitude;
    double longitude;
    double altitude;
    
    latitude = std::stod(lat_str);
    longitude = std::stod(lon_str);
    altitude = std::stod(alt_str);

    double pi = 3.14159265358979323846;
    latitude = (latitude / 360) * 2 * pi;
    longitude = (longitude / 360) * 2 * pi;
    
    WayPointSettings wp;
    setWaypointDefaults(&wp);
    wp.index     = i;
    wp.latitude  = latitude;
    wp.longitude = longitude;
    wp.altitude  = altitude;
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
