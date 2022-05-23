#!/usr/bin/env python2.7

import sys
import subprocess

# methods calls for given method

subprocess.check_call(['bash','installTemplate.sh','defuscadotemplate/'])
print 'successfully installed APK into our runtime deobfuscation framework'
