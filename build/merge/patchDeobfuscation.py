import os
import re
import sys
import mmap
import contextlib
import shutil
import itertools
import io
from collections import OrderedDict

# patchDeobfuscation.py expect in its working directory a file called 
# deobfuscationResultFinal.txt which contains the deobfuscated results


class PatchDeobfuscation(object):
    def __init__(self, rootdir):
        self.rootdir = rootdir
        self.smaliFilesArray = set()
        self.deobfuscationList = []
        self.deobfuscationArrayList = []
        self._currentSmaliFile = None
        self.cnt = 0
        self.parseDeobfuscations()
        self.fillSmaliFilesArray(self.rootdir)
        # self.parseDeobfuscations()

    @property
    def currentSmaliFile(self):
        return self._currentSmaliFile

    @currentSmaliFile.setter
    def currentSmaliFile(self, value):
        self._currentSmaliFile = value

    def fillSmaliFilesArray(self, rootdir):
        for path, subFolders, files in os.walk(rootdir):
            for smaliArray in files:
                if smaliArray.endswith('.smali'):
                    self.smaliFilesArray.add(os.path.join(path, smaliArray))

    def startPatchingSmaliFiles(self):
        for smaliFile in self.smaliFilesArray:
            self.currentSmaliFile = smaliFile
            # for testing purpose, we can only patch a certain file....
            #if smaliFile == "<app>/smali/t.smali":
            #    print "analyze file: %s" % smaliFile
            #else:
            #    continue
            #print "self.deobfuscationList: %s" % self.deobfuscationList
            #print "self.deobfuscationArrayList: %s" % self.deobfuscationArrayList

            for patchingDeobfuscationArray in self.deobfuscationArrayList:
                if self.isArrayFieldInSmaliFile(patchingDeobfuscationArray[1]):
                    self.patchDeobfuscationForArrayField(patchingDeobfuscationArray[
                                                         1], patchingDeobfuscationArray[2], patchingDeobfuscationArray[0])
            for patchingDeobfuscation in self.deobfuscationList:
                if self.isFieldInSmaliFile(patchingDeobfuscation[0]):
                    self.patchDeobfuscationForField(
                        patchingDeobfuscation[0], patchingDeobfuscation[1])

    def parseDeobfuscations(self):
        deobfuscationElement = []
        arrayParsing = False
        lines = open("deobfuscationResultFinal.txt").readlines()
        for line in lines:
            line = line.strip()
            if line == "":
                if len(deobfuscationElement) > 1:
                    self.deobfuscationList.append(deobfuscationElement)
                deobfuscationElement = []
                continue
            if "ArrayStart" in line:
                arrayParsing = True
                arrayTypeCounter = 0
                deobfuscationArray = []
                deobfuscatedValuesOfArray = []
                continue

            if arrayParsing:
                if "ArrayEnd" in line:
                    arrayParsing = False
                    deobfuscationArray.append(deobfuscatedValuesOfArray)
                    self.deobfuscationArrayList.append(deobfuscationArray)
                    continue

                line = line.split("=",1)[-1]
                if arrayTypeCounter > 1:
                    deobfuscatedValuesOfArray.append(line)
                else:
                    deobfuscationArray.append(line)
                arrayTypeCounter += 1
                continue

            line = line.split("=",1)[-1]
            deobfuscationElement.append(line)
            
        if len(self.deobfuscationList) < 1 and len(deobfuscationElement) > 0:
            self.deobfuscationList.append(deobfuscationElement)

        return self.deobfuscationList

        # old function, removed in next release
    def getUsedFieldOfMethodInvocation(self, line):
        m = re.search(r";->(.+$){1}", line)
        if m:
            return m.groups(0)
        else:
            return None


    # getLineOfObjectReference getDeobfuscationRoutineOfObfuscatedField
    def getDeobfuscationRoutineOfObfuscatedField(self, fieldObject):
        deobfuscationList = []
        deobfuscationRoutineSet = []
        fieldObjectEscaped = re.escape(fieldObject)
        regexStartDeobfuscation = "(sget-object.+" + fieldObjectEscaped + ")"
        regex = re.compile(regexStartDeobfuscation)
        file = self.currentSmaliFile
        register = "none"
        continuesInst = False
        lines = open(file)
        linesOfFile = open(file).readlines()
        for line_i, line in enumerate(linesOfFile, 1):
            if regex.search(line) and not continuesInst:
                line = line.rstrip()
                deobfuscationList.extend([line_i, line])
                deobfuscationRoutineSet.append(deobfuscationList)
                register = self.getRegisterOfObject(line)
                continuesInst = True
            m = re.search("(move-result-object .*)", line)
            if m and continuesInst:
                m.group(0)
                register = self.getRegisterOfObject(line)
                # startline-number, line, end-linenumber, line, registerContainingResult
                deobfuscationList.extend([line_i, line.rstrip(), register])
                #deobfuscationRoutineSet.append(deobfuscationList)
                deobfuscationList = []
                register = "none"
                continuesInst = False

            if not m and continuesInst and len(line) > 1:
                deobfuscationList = []
                register = "none"
                continuesInst = False

            m3 = re.search(".end method",line)
            if m3 and continuesInst:
                deobfuscationList = []
                register = "none"
                continuesInst = False
                continue
        lines.close()

        return deobfuscationRoutineSet

    def getDeobfuscationRoutineOfObfuscatedArrayField(self, fieldObject):
        deobfuscationList = []
        deobfuscationRoutineSet = []
        constRegList = []
        #fieldObjectEscaped = re.escape(fieldObject)
        fieldObjectEscaped = fieldObject.replace( '[', '\\' + '[')
        regexStartDeobfuscation = "(sget-object.+" + fieldObjectEscaped + ")"
        regex = re.compile(regexStartDeobfuscation)
        file = self.currentSmaliFile
        register = "none"
        continuesInst = False
        constString = False
        moreConstString = False
        lines = open(file)
        linesOfFile = open(file).readlines()

        for line_i, line in enumerate(linesOfFile, 1):
            if regex.search(line) and not continuesInst:
                line = line.rstrip()
                deobfuscationList.extend([line_i, line])
                register = self.getRegisterOfObject(line)
                continuesInst = True
                secondContinuesInst = False
                continue

            if regex.search(line) and continuesInst:
                line = line.rstrip()
                deobfuscationRoutineSet.append(deobfuscationList)
                deobfuscationList = []
                deobfuscationList.extend([line_i, line])
                register = self.getRegisterOfObject(line)
                continue

            m = re.search("(const/.*)", line)
            if m and continuesInst and not constString:
                m.group(0)
                #    deobfuscationList = deobfuscationList[:-2 or None] # if it's only one sget, than we don't need the inital sget
                constValue = self.getValueOfConst(line)
                deobfuscationList.extend([constValue])
                constString = True # ensure that we use the first const\. value as index
                constRegList.append(self.getRegisterOfConst(line))
                continue

            if m and continuesInst and constString:
                moreConstString = True
                constRegList.append(self.getRegisterOfConst(line))
                continue

            m2 = re.search("(aget-object .*)", line)
            if m2 and continuesInst:
                m2.group(0)
                if moreConstString:
                    del deobfuscationList[-1] # remove last insert (which was a constValue of first detected const v.*,<value>)
                    destReg = self.getDestRegisterOfArrayPos(line)
                    constValue = next((i for i in constRegList if i == destReg), None)
                    if constValue == None:
                        register = self.getDestRegisterOfObjectRef(line)
                        deobfuscationList.extend([line_i, line.rstrip(), register])
                    else:
                        deobfuscationList.extend([constValue])

                    deobfuscationRoutineSet.append(deobfuscationList)
                    continuesInst = False
                    constString = False
                    #secondContinuesInst = False
                    moreConstString = False
                    deobfuscationList = []
                    continue

                if register in line:
                    destRegister = self.getDestRegisterOfObjectRef(line)
                    # startline-number, line, arrayIndex, end-linenumber, line, registerContainingResult
                    deobfuscationList.extend([line_i, line.rstrip(), destRegister])
                else:
                    if constString:
                        del deobfuscationList[-1] # remove the const.value because this value belongs to another array

                deobfuscationRoutineSet.append(deobfuscationList)

                #if constString:
                #    indexOfLastAppend = len(deobfuscationRoutineSet) -1
                #   if deobfuscationRoutineSet[indexOfLastAppend][0] == deobfuscationList[0]:
                #        if "g.smali" in self.currentSmaliFile:
                #            print "hallo: %s" % deobfuscationList
                #        continuesInst = False
                #        deobfuscationList = []
                #        continue
                deobfuscationList = []
                register = "none"
                continuesInst = False
                constString = False
                moreConstString = False
                continue

            m3 = re.search(".end method",line)
            if m3 and continuesInst:
                deobfuscationList = []
                register = "none"
                continuesInst = False
                constString = False
                moreConstString = False
                continue

        lines.close()
        #print deobfuscationRoutineSet
        return deobfuscationRoutineSet

    def getRegisterOfObject(self, line):
        m = re.search("(v\d+)", line)
        if m:
            return m.group(0)
        else:
            return None

    def getValueOfConst(self, line):
        m = re.search("(0x\w+)", line)
        if m:
            return m.group(0)
        else:
            return None

    def getRegisterOfConst(self, line):
        m = re.search("(v\d+)", line)
        if m:
            return m.group(0)
        else:
            return None

    def getDestRegisterOfObjectRef(self, line):
        m = re.search("(v\d+)", line)
        if m:
            return m.group(0)
        else:
            return None

    def getDestRegisterOfArrayPos(self, line):
        m = re.search("(v\d+)$", line)
        if m:
            return m.group(0)
        else:
            return None

    def getObfuscatedFieldName(self, line):
        m = re.search("(obfuscatedVar=)(.*)", line)
        if m:
            return m.groups(2)
        else:
            return None

    def isFieldInSmaliFile(self, field):
        smaliFile = self.currentSmaliFile
        f = open(smaliFile)
        with contextlib.closing(mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)) as s:
            if s.find(field) != -1:
                return True
        return False

    def isArrayFieldInSmaliFile(self, field):
        smaliFile = self.currentSmaliFile
        field = field.encode("utf-8")
        fieldEscaped = field.replace( '[', '\\' + '[')
        with io.open(smaliFile, "r", encoding="utf-8") as f:
            file_size = os.path.getsize(smaliFile)
            mm = mmap.mmap(f.fileno(), file_size, access=mmap.ACCESS_READ)
            return re.search(fieldEscaped, mm)

    def patchDeobfuscationForField(self, field, deobfuscatedValue):
        deobfuscationRoutines = self.getDeobfuscationRoutineOfObfuscatedField(
            field)
        deobfuscationRoutines = deobfuscationRoutines[::-1]
        smaliFile = self.currentSmaliFile
        deobfuscatedValue = repr(deobfuscatedValue)
        deobfuscatedValue = deobfuscatedValue.replace( '"', '\\' + '"')

        for f in deobfuscationRoutines:
            file = open(smaliFile)
            lines = file.readlines()
            replace = open(smaliFile, 'w')

            arrayLength = len(f)

            if arrayLength == 2:
                replace.writelines(lines[0:f[0]])
                #patch = "    # " + deobfuscatedValue
                patch = "    const-string " + self.getRegisterOfConst(f[1])  + ", \"" + deobfuscatedValue + "\""
            else:
                replace.writelines(lines[0:f[0] - 1])
                patch = "    const-string " + \
                f[4] + ", \"" + deobfuscatedValue + "\""

            replace.writelines(patch)
            replace.writelines("\n")

            if arrayLength == 2:
                replace.writelines(lines[f[0]:-1])
            else:
                replace.writelines(lines[f[2]:-1])

            replace.writelines(lines[-1])
            replace.close()
            file.close()


# if we can directly determine which array position has been accessed we patch it with the corresponding deobfuscated value, if not we will insert a comment of the whole array
# for now we just insert a comment of the deobfuscated value as a comment behind the real deobfuscated value in order to make the patching process easier
# in a future release we will do the following:
# 1. increase number of .locals value (register num will increased) e.g. from 8 to 9
# 2. a new register is added to .prolouge  with the size of the arrayLength e.g. v8 0x53  //for an array with length 35
# 3. create string array at the posistion where its been accessed
    def patchDeobfuscationForArrayField(self, field, deobfuscatedArray, sizeOfDeobfuscatedArray):
        deobfuscationRoutines = self.getDeobfuscationRoutineOfObfuscatedArrayField(
            field)
        deobfuscationRoutines = deobfuscationRoutines[::-1]

        smaliFile = self.currentSmaliFile
        #print "patching: %s" % smaliFile

        for f in deobfuscationRoutines:
            #print "try to patch (%s): %s" % (smaliFile,f)
            if "aget" in f[1]:
                continue
            file = open(smaliFile)
            lines = file.readlines()
            replace = open(smaliFile, 'w')

            arrayLength = len(f)
            if arrayLength == 5 or arrayLength == 2:
                # comment solution
                replace.writelines(lines[0:f[0]])
                arrayAsComment = ', '.join(deobfuscatedArray)
                arrayAsComment = '['+ arrayAsComment + ']'
                arrayAsComment = repr(arrayAsComment)
                patch = "    # " + arrayAsComment

            elif arrayLength == 3:
                replace.writelines(lines[0:f[0]])
                arrayAsComment = ', '.join(deobfuscatedArray)
                arrayAsComment = '['+ arrayAsComment + ']'
                arrayAsComment = repr(arrayAsComment)
                patch = "    # " + arrayAsComment
                if "0x" in f[2]:
                    replace.writelines(patch)
                    replace.writelines("\n")
                    arrayPos = int(f[2], 16)
                    deobfuscatedValue = deobfuscatedArray[arrayPos]
                    deobfuscatedValue = repr(deobfuscatedValue)
                    patch = "    # " + deobfuscatedValue
            elif arrayLength == 6:
                arrayPos = int(f[2], 16)
                arrayLen = len(deobfuscatedArray)
                if arrayPos >= arrayLen:
                    replace.writelines(lines[0:-1])
                    replace.close()
                    file.close()
                    continue

                deobfuscatedValue = deobfuscatedArray[arrayPos]
                deobfuscatedValue = repr(deobfuscatedValue)
                deobfuscatedValue = deobfuscatedValue.replace( '"', '\\' + '"')
                replace.writelines(lines[0:f[0] - 1])
                # const-string/jumbo when we have more than
                # 65535 strings in one dex...for now we assume
                # we doesn't have that much...
                patch = "    const-string " + \
                    f[5] + ", \"" + deobfuscatedValue + "\""
            else:
                replace.writelines(lines[0:-1])
                #replace.writelines(lines[-1])
                replace.close()
                file.close()
                continue


            replace.writelines(patch)
            replace.writelines("\n")
            if arrayLength == 5 or arrayLength == 2:
                replace.writelines(lines[f[0]:-1])
                replace.writelines(lines[-1])
            elif arrayLength == 6:
                replace.writelines(lines[f[3]:-1])
                replace.writelines(lines[-1])
            elif arrayLength == 3:
                replace.writelines(lines[f[0]:-1])
                replace.writelines(lines[-1])    
            replace.close()
            file.close()


def main(argv):
    root = ''
    if len(sys.argv) < 2:
        print '%s <Path to Smali-Files>' % sys.argv[0]
        sys.exit(2)

    root = str(sys.argv[1])
    p = PatchDeobfuscation(root)
    p.startPatchingSmaliFiles()


if __name__ == "__main__":
    main(sys.argv[1:])
