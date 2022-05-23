# DeStroid alpha version

This folder contains an early version of our prototype (the version used in our paper will be open sourced by the end of the year). 

## Why not the newest version and the full source code?

We are still working on improving the patching part. We wanted it to be more automatic, smooth and complete.
Unfortunately, it turned out that this is way more complicated than we expected. On the other hand, as this was a side project on which we
worked during our free time mostly, we are not able to continue the work right now. However, we still plan to release a version some time this year.

## So what does this version provides?

It provides an early version of our prototype which is able to decrypt strings when simple obfuscations are used. Further the patching routine is not able to patch all deobfuscated strings.
Furthermore this prototype was build for python2.7 and is using an older version of dexlib2 (library for parsing the bytecode from the target app).


## How to run DeStroid?

Best is using your own physical research device and provide it to destroid.py:

```bash
$ python2.7 destroid.py -s 807KPHG2003969 obfuscated.apk
	### DeStroid ###


Begin with identifying obfuscations in obfuscated.apk
DeStroid Heuristic v0.91
Number of Classes in DEX: 1459
MethodName: Lcom/obfuscation/rot13/Rot13;->rot13(Ljava/lang/String;)Ljava/lang/String;      ReturnType: Ljava/lang/String;   treshold: 11
Used bit operations: [add-int/lit8, int-to-char, add-int/lit8, add-int/lit8, int-to-char, add-int/lit8, int-to-char, add-int/lit8, int-to-char]
Used bit operations (unique): [add-int/lit8, int-to-char]


Number of CLINITs in DEX: 2
Number of classes in DEX: 1459
Number of implemented methods in DEX: 10
Number of static string invokes: 
Num of probably obfuscated CLINITs: 1
------------------------
We have a lot to analyze plz keep calm while building the template...
This is the possible deobfuscationRoutine: Lcom/obfuscation/rot13/Rot13;->rot13(Ljava/lang/String;)Ljava/lang/String;
DeobfuscationType: SmaliLayer.DEOBFUSCATION_TYPE_FIELD
Found 1 possible Core-Instances...
Finished analyzing...
Start building the template, this may take a while :-) ...
SingleCore Solution

Successfully written template to: /home/daniel/research/destroid_research/destroid_new/destroid_alpha/template/defuscadoTemplate.dex
Successfully created deobfuscation template of obfuscated.apk
------------------------
Finished analyzing...
beginning with template installation
set device to 807KPHG2003969
installing Deobfuscation Template to /data/local/tmp/
Successfully installed APK into our runtime deobfuscation framework

Beginning with runtime deobfuscation...


Successfully finished with the runtime deobfuscation
------------------------
Successfully patched the obfuscated values with the deobfuscated values

moving results to results/results_obfuscated/
all results can be found in: results/results_obfuscated
the patched smali code can be found here: results/results_obfuscated/obfuscated/smali/
the patched APK can be found here: results/results_obfuscated/obfuscated_deobfuscated.apk
plz keep in mind that the APK has to be signed in order to run it

DeStroid finished!
Have a nice day :-)

```
