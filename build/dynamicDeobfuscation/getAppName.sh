APKLIST=listOfInstalledApps.txt

getLineNumOfLastInstalledAPK(){
	getListOfInstalledApps
	grep -n firstInstallTime= ${APKLIST} | awk -F'=' '{print $1 " " $2}' | sort -k2 | tail -n 1 | awk -F':' '{print $1}'
}

getListOfInstalledApps(){
	adb shell dumpsys package | awk '{if(/pkg=Package/) {print $2} else if(/firstInstallTime/) {print $1" "$2} else if(/lastUpdateTime/) {print $1" "$2"\n"} }'  | tr -d '}' > ${APKLIST}
}

uninstallMalware(){
	resultUnfiltered=$(( adb shell pm uninstall ${malwareName} ) 2>&1)
	result=$(strings <<<$resultUnfiltered)
}


stopMalware(){
	adb shell am force-stop ${malwareName}
}

num=$(getLineNumOfLastInstalledAPK)
numOfLastAPK=$((num-1))


#malwareName="$(sed "${numOfLastAPK}q;d" ${APKLIST})"
malwareNameUnfiltered=$(cat ${APKLIST} | head -n ${numOfLastAPK} | tail -n 1)
malwareName=$(strings <<< $malwareNameUnfiltered)

echo $malwareName
