#! /bin/bash

globalProjectName=""


createResultStructure(){
	projectName="${globalProjectName}"

	mkdir -p "results/results_${projectName}"
	echo "results/results_${projectName}"
}


getProjectName(){
	filename=$1
	projectNamePrefix="${filename%.*}"
	echo "${projectNamePrefix}"
}

moveResults(){
	echo "moving results to $1/"
	mv --backup=numbered deobfuscationResultFinal.txt "$1"
	mv --backup=numbered "merge/${globalProjectName}/" "$1"
	mv --backup=numbered "${globalProjectName}_deobfuscated.apk" "$1"
	rm merge/deobfuscationResultFinal.txt
}

mkdir -p results

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit
fi

globalProjectName=`getProjectName $1`

destProjectName=`createResultStructure`
moveResults "${destProjectName}"

echo "all results can be found in: ${destProjectName}"
echo "the patched smali code can be found here: ${destProjectName}/${globalProjectName}/smali/"
echo "the patched APK can be found here: ${destProjectName}/${globalProjectName}_deobfuscated.apk"
echo "plz keep in mind that the APK has to be signed in order to run it"
