#! /bin/bash

#   runPatchingRoutine.sh
#	requirements: apktool, python version 2.7:


getPythonVersion() {
	# detect python version
	pyver=$($PYTHON -c 'import sys; print(".".join(map(str, sys.version_info[:3])))')
}


error() {
  local parent_lineno="$1"
  local message="$2"
  local code="${3:-1}"
  if [[ -n "$message" ]] ; then
    echo "Error on or near line ${parent_lineno}: ${message}; exiting with status ${code}"
  else
    echo "Error on or near line ${parent_lineno}; exiting with status ${code}"
  fi

  if [[ -z $APKTOOL ]]; then
	echo -e "${PROGNAME}: can't find apktool. Plz install apktool into PATH. \nFollow instructions at https://ibotpeaches.github.io/Apktool/install/"
  fi

  exit "${code}"
}
trap 'error ${LINENO}' ERR

APKTOOL=$(which apktool 2>/dev/null)
PYTHON=$(which python2.7 2>/dev/null)

getPythonVersion

if [[ ! "$pyver" =~ "2.7." ]]; then
	PYTHON=$(which python2.7 2>/dev/null)
	getPythonVersion
	if [[ ! "$pyver" =~ "2.7." ]]; then
		echo "${PROGNAME}: can't find python 2.7.x. Plz install python in version 2.7.x"
	fi
fi


filename=$1
obfuscatedBinary="${filename%.*}"



if [ -d "merge/${obfuscatedBinary}/" -a ! -z "${obfuscatedBinary}" ]; then
  rm -rf "merge/${obfuscatedBinary}/"
fi

# create the orignal smali code
$APKTOOL d -o "merge/${obfuscatedBinary}/" $1 >/dev/null


#python2.7 merge/patchDeobfuscation.py "merge/${obfuscatedBinary}/"
$PYTHON merge/patchDeobfuscation.py "merge/${obfuscatedBinary}/"

# build the deobfuscated apk
$APKTOOL b -f -o "${obfuscatedBinary}_deobfuscated.apk" "merge/${obfuscatedBinary}/"  >/dev/null