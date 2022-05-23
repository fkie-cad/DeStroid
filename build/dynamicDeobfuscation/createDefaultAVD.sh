#!/bin/bash

androidID=

getLatestAvaibleAndroidVersion() {
	#androidID=$(android list targets | grep "android-" | sort -t'-' -k2nr | head -n 1| awk '{ print $2}')
	androidID=$(android list targets | grep "android-" | sort -t'-' -k2 | head -n 1| awk '{ print $2}')
}

createDefaultAVD(){
	getLatestAvaibleAndroidVersion
	echo no | android create avd -n defuscatorDalvik -f -t $androidID -c 100M --abi "default/armeabi-v7a" 2> /dev/null 1>&2
}

hasDefaultAVD(){
	android list avd | grep "defuscatorDalvik" | wc -l
}

if (( $(hasDefaultAVD) < 1 ))
then
	createDefaultAVD
else
	echo "Default AVD already exist. No AVD creation."
fi

