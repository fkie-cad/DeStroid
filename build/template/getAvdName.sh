#!/bin/bash

# helper script to get the associaten of adb device id to adb name


# get ports of running android emulators:
getProjectName(){
portsOfAVDEmulators=( $(adb devices | awk '{ print $1}' | grep em | awk -F'-' '{ print $2}') )
}

getProjectName

# creates lists for each binary
for avdPort in "${portsOfAVDEmulators[@]}"; do
  (sleep 2; echo 'avd name') | telnet 127.0.0.1 ${avdPort} 2>/dev/null | grep -i avd | awk '{ print $0 ": emulator-" '"${avdPort}"'}'
  sleep 2
done
