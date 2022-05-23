#!/usr/bin/env python2.7

import sys
import subprocess
import argparse
import os.path

# this script will run all the parts of the prototype "DeStroid"

def runCreateDefaultAVD():
    try:
        subprocess.check_call(['bash','dynamicDeobfuscation/createDefaultAVD.sh'])
        return True
    except:
        print "DeStroid can't create default AVD. Maybe the required packages not installed."
        return False


def runObfuscationHeuristic(apk):
    try:
        subprocess.check_call(
            ['java', '-jar', 'obfuscationHeuristic/Defuscator.jar', '-i', apk])
    except:
        e = sys.exc_info()[0]
        print "ObfuscationHeuristic-Error: %s" % e
        sys.exit(
            "Template building failed, plz send the apk to danie.baier-[at]-fkie.fraunhofer.de")


def runTemplateInstallation(device):
    try:
        if device is not None:
        	subprocess.check_call(['bash', 'template/installTemplate.sh',device])
        else:
        	subprocess.check_call(['bash', 'template/installTemplate.sh'])
        return True
    except:
        e = sys.exc_info()[0]
        print "TemplateInstallation-Error: %s" % e
        return False


def runRemoveTemplateOnDevice(device):
    try:
        FNULL = open(os.devnull, 'w')
        if device is not None:
            subprocess.check_call(['adb', '-s', device, 'shell', 'rm', '/data/local/tmp/defuscadoTemplate.dex'], stdout=FNULL, stderr=subprocess.STDOUT)
        else:
            subprocess.check_call(['adb', 'shell', 'rm', '/data/local/tmp/defuscadoTemplate.dex'], stdout=FNULL, stderr=subprocess.STDOUT)
        return True
    except:
        e = sys.exc_info()[0]
        print "TemplateRemove-Error: %s" % e
        return False


def runDynamicDeobfuscation(device):
    try:
        print 'Beginning with runtime deobfuscation...'
        if device is not None:
        	subprocess.check_call(['bash', 'dynamicDeobfuscation/executeDynamicDeobfuscador.sh',device])
        else:
        	subprocess.check_call(['bash', 'dynamicDeobfuscation/executeDynamicDeobfuscador.sh'])
        return True
    except:
        e = sys.exc_info()[0]
        print "DynamicDeobfuscation-Error: %s" % e
        return False


def runPatchingRoutine(apk):
    try:
        subprocess.check_call(['bash', 'merge/runPatchingRoutine.sh', apk])
        return True
    except:
        e = sys.exc_info()[0]
        print "PatchingRoutine-Error: %s" % e
        return False


def runCreateResultStructure(apk):
    try:
        subprocess.check_call(['bash', 'merge/resultGenerator.sh', apk])
        return True
    except:
        e = sys.exc_info()[0]
        print "CreateResultStructure-Error: %s" % e
        print "The result creation failed, but you should find the possible deobfuscated results in merge/"
        return False


def doesDeviceExist(device):
    try:
    	FNULL = open(os.devnull, 'w')
        subprocess.check_call(['adb', '-s', device, 'shell', 'stat', '/data/'], stdout=FNULL, stderr=subprocess.STDOUT)
    except:
    	print "DeStroid can't work with emulator/device: %s" % device
    	sys.exit(2)


def main(argv):
    apk = ''
    device = None

    parser = argparse.ArgumentParser(prog='destroid', description='DeStroid - a generic string encryption deobfuscation toolkit for Android APKs', epilog=''' If you encounter a failure or have any problems using DeStroid, feel free to ask. 
    	Please include the file in which the failure encountered in your email at admin-[at]-remoteshell-security.com''')
    parser.add_argument(
        'apk', help='The path to the APK or DEX to deobfuscate the literal encryption')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 0.4')
    parser.add_argument('-s','--android_serial',
                        help='Device ID for Android device or emulator to run the dynamic deobfuscation, default="emulator-5582"', dest='device')

    args = parser.parse_args()

    if os.path.isfile(args.apk):
        apk = args.apk
    else:
        apk = args.apk
        print "DeStroid can't find apk: %s" % apk
        print parser.print_help()
        sys.exit(2)

    if args.device is not None:
    	device = args.device
        doesDeviceExist(device)
    else:
        if runCreateDefaultAVD():
            print 'Successfully created default AVD\n'
        else:
            print 'Error in creating default AVD.\nPlz create it on your own and use the -s parameter in order to run DeStroid on it.'

    print '\t### DeStroid ###'
    print '\n'

    runObfuscationHeuristic(apk)


    if runTemplateInstallation(device):
        print 'Successfully installed APK into our runtime deobfuscation framework\n'

    if runDynamicDeobfuscation(device):
        print 'Successfully finished with the runtime deobfuscation'
        print '------------------------'

    if runPatchingRoutine(apk):
        print 'Successfully patched the obfuscated values with the deobfuscated values\n'

    runRemoveTemplateOnDevice(device)

    if runCreateResultStructure(apk):
        print "\nDeStroid finished!\nHave a nice day :-)\n"


if __name__ == "__main__":
    main(sys.argv[1:])
