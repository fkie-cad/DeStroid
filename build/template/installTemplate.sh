#!/bin/bash

# This has to be configured somewhere central
#export ANDROID_SDK_ROOT=/data/Android/Sdk
export ANDROID_SDK_ROOT=/home/daniel/Android/Sdk
templateName=defuscadoTemplate.dex
DEVICE_TIMEOUT=100
PROGNAME=$(basename $0)


function installTemplate() {
  
  TEMP_ADB_PATH="/data/local/tmp"
  OUTPUT=`adb -s "${android_device}" shell ls $TEMP_ADB_PATH`
  if [[ $OUTPUT == *"Permission denied"* ]]
  then
    echo "installing Deobfuscation Template to /data/local/"
    TEMP_ADB_PATH="/data/local"
  fi
  echo "installing Deobfuscation Template to /data/local/tmp/"


  if existOldTempplate; then
    removeTemplate
  fi

  # echo -e "\033[31m####\033[m" print in red

  if [ -z "${1}" ]; then
    adb -s "${android_device}" push template/defuscadoTemplate.dex $TEMP_ADB_PATH 1>/dev/null 2> /tmp/Error
  else
    adb -s ${1} push template/defuscadoTemplate.dex $TEMP_ADB_PATH 1>/dev/null 2> /tmp/Error
  fi
  rm template/defuscadoTemplate.dex

  ERROR=$(</tmp/Error)
  if [ ${#ERROR} -ge 5 ]; then echo -e "\033[31m${ERROR}\033[m" ; fi
  #echo "INSTALLED: Deobfuscation Template"
}



function startEmulator() {
  EMULATOR=$(which emulator)
  ${EMULATOR} -avd defuscatorDalvik -use-system-libs -port 5582 >/dev/null 2>&1 &
  #emulator -use-system-libs -avd defuscatorDalvik -port 5582
}



function isEmulatorRunning() {
  emulator_check=$(adb -s "${android_device}" shell stat /data/ | wc -l)
  if [ ${emulator_check} -le 5 ]; then
    echo 2
  else
    echo 0
  fi
}


function showAdbDevices() {
  adb devices
}


function removeTemplate(){
  adb -s "${android_device}" shell rm /data/local/tmp/defuscadoTemplate.dex
}

function existOldTempplate() {
  TEMP_ADB_PATH="/data/local/tmp"
  FILENAME_RESULT=$(adb -s "${android_device}" shell ls ${TEMP_ADB_PATH}/ | tr -d '\015'|grep "^${templateName}$")
  if [ -z "$FILENAME_RESULT" ];
    then
        # 1 = false
        return 1 
  else
        # 0 = true
        return 0 
  fi
}

echo "beginning with template installation"

if [ -z "${1}" ];then
  android_device="emulator-5582"
else
  android_device="${1}"
fi

echo "set device to ${android_device}"
emulatorStatus=$(isEmulatorRunning)

if [ ${emulatorStatus} -ne 0 ]; then
  echo -n "starting and connecting to emulator/device..."
  startEmulator &
  sleep ${DEVICE_TIMEOUT}
fi

installTemplate

