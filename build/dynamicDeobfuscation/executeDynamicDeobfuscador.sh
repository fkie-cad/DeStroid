#!/bin/bash

# we should also enable the possibility to run the generated template on a real device, for now just future work

export ANDROID_SDK_ROOT=/data/Android/Sdk
android_device=

# for now not used
function getApiLevelOfRunningEmulator(){
	adb -s "${android_device}" shell getprop ro.build.version.sdk
}

function isNotInstalled() {
	check=$(adb shell pm list packages com.obfuscation.dynamicdeobfuscator | wc -l)
	return ${check}
}


function installDynamicDefuscador(){
	apiLevel=$(getApiLevelOfRunningEmulator)
	if [ "${apiLevel}" -le 23 ] || isNotInstalled; then
		adb -s "${android_device}" uninstall com.obfuscation.dynamicdeobfuscator 2>/dev/null 1>&2
		adb -s "${android_device}" install dynamicDeobfuscation/dynamicDeobfuscator.apk 2>/dev/null 1>&2
	fi
	
    #adb push dynamicDeobfuscator.apk $TEMP_ADB_PATH
    #/opt/android-sdk/build-tools/25.0.0/apksigner sign --ks /data/Android/masterthesis.jks app-dynamicDeobfuscator.apk
    

    TEMP_ADB_PATH="/data/local/tmp"
	OUTPUT=`adb -s "${android_device}" shell ls $TEMP_ADB_PATH`
	if [[ $OUTPUT == *"Permission denied"* ]]
		then
		TEMP_ADB_PATH="/data/local"
    fi
}


function startDynamicDeobfuscation(){
	#adb shell dalvikvm -cp $TEMP_ADB_PATH/dynamicDeobfuscator.apk DynamicDeobfuscador
	# adb shell am start -n com.obfuscation.dynamicdeobfuscador/.DynamicDeobfuscador
    # Starting: Intent { cmp=com.obfuscation.dynamicdeobfuscador/.DynamicDeobfuscador }
    adb -s "${android_device}" logcat -c
	adb -s "${android_device}" shell am start -n com.obfuscation.dynamicdeobfuscator/com.obfuscation.dynamicdeobfuscator.DynamicDeobfuscator  2>/dev/null 1>&2
}


function getDeobfuscation(){
	if [ -z "deobfuscationResultFinal.txt" ];
    then
        rm deobfuscationResultFinal.txt
  	fi
	tmpDeobFileUnfiltered=$(filterAdbOutputForWriter)
	tmpDeobFile=$(strings <<< $tmpDeobFileUnfiltered)
	adb -s "${android_device}" pull ${tmpDeobFile} 2>/dev/null 1>&2
	deobFilename="${tmpDeobFile##*/}"
	mv "${deobFilename}" deobfuscationResultFinal.txt
	cp deobfuscationResultFinal.txt merge/

    # if an error accours during the runtime deobfuscation it will be printed here:

    printf "\n"
	filterAdbOutputForErrMsg | grep "DeobfuscationError"
	printf "\n"
}


function filterAdbOutputForWriter(){
	adb -s "${android_device}" logcat -ds "DeobfuscationWriter"  | grep AdbPath= | tail -n 1 | awk -F'=' '{print $2}'
}


function filterAdbOutputForStdout(){
	adb -s "${android_device}" logcat -ds "DeobfuscationContent"
}


function checkForDeobfuscationFinished(){
	
	adb -s "${android_device}" logcat -ds "DeobfuscationWriter"  | grep "Deobfuscation=finished"
	if [ $? -ne 0 ]; then
		sleep 2
      		while ${runLoop}; do
          		adb -s "${android_device}" logcat -ds "DeobfuscationWriter"  | grep "Deobfuscation=finished"  2>/dev/null 1>&2
          		if [ $? -eq 0 ]; then
            		runLoop=false
          		fi
          		sleep 2
     		done

		

	fi
	sleep 5
}

function filterAdbOutputForErrMsg(){
	adb -s "${android_device}" logcat -ds "DeobfuscationError"
}

if [ -z "${1}" ];then
	# android_device="emulator-5554"
	android_device="emulator-5582"
else
	android_device="${1}"
fi

installDynamicDefuscador
startDynamicDeobfuscation
#sleep 5000
checkForDeobfuscationFinished
#sleep 600
sleep 30
getDeobfuscation
#echo "finished"
#filterAdbOutputForStdout

# DeobfuscationContent
# DeobfuscationHandler
