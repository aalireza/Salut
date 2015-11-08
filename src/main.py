# -*- coding: utf-8 -*-

from multiprocessing import Process
import argparse
import Toolbox
import subprocess
import time


def init():
    ttsEngine, translatorEngine, speechEngine = argumentHandler()
    (messenger, selfCode, targetCode, oneDing, twoDing,
     srcDir, srcParentDir, platform) = Toolbox.config()
    Toolbox.checkDataDir(srcParentDir)
    selfID = Toolbox.loadNull("self")
    targetID = Toolbox.loadNull("target")
    Toolbox.callMessenger(messenger)
    startCallStamp = Toolbox.timeStamp()
    return (selfID, selfCode, targetID, targetCode, srcDir, srcParentDir,
            platform, ttsEngine, translatorEngine, speechEngine, startCallStamp)


def terminate(selfID, targetID):
    Toolbox.unloadNull(selfID)
    Toolbox.unloadNull(targetID)


def Main(selfCode, targetCode, who, srcParentDir, platform, ttsEngine,
         translatorEngine, speechEngine, callName):
    translatorScriptPath = Toolbox.translatorScriptCreator(
        srcParentDir, selfCode, targetCode, who, ttsEngine,
        translatorEngine, speechEngine, callName)
    logScriptPath = Toolbox.readLogScriptCreator(who, srcParentDir, callName)
    if ((translatorScriptPath is not None) and (logScriptPath is not None)):
        script = "splitvt -t {} -upper {} -lower {}".format(
            who, translatorScriptPath, logScriptPath)
    if platform == 'linux2':
        linuxScript = ('x-terminal-emulator -e "{}"').format(script)
        subprocess.Popen(linuxScript, shell=True).communicate()
    elif platform in ['win32', 'cygwin']:
        print "Windows is not supported."
        time.sleep(3)
        raise SystemExit
    else:
        print ("If you think your platform should be supported, comment the" +
               " 'else clause' of Main function in main.py and copy the " +
               "content of 'linux2' or 'darwin' or whatever")
        time.sleep(6)
        raise SystemExit


def argumentHandler():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--ttsEngine", required=True,
                        help="Should I use espeak or google for text2speech?",
                        type=str, choices=["espeak", "google", "bing",
                                           "nuance"])
    parser.add_argument("-tr", "--translatorEngine", required=True,
                        help="Which translator engine should be used?",
                        type=str, choices=["google", "bing"])
    parser.add_argument("-sp", "--speechEngine", required=True,
                        help="Which speech to text engine should be used?",
                        type=str, choices=["google", "bing", "nuance"])
    args = parser.parse_args()
    return args.ttsEngine, args.translatorEngine, args.speechEngine

if __name__ == '__main__':
    (selfID, selfCode, targetID, targetCode, srcDir, srcParentDir,
     platform, ttsEngine, translatorEngine, speechEngine,
     startCallStamp) = init()
    start = None
    while start not in ["y", "n"]:
        start = str(raw_input("Enter 'y' to start, enter 'n' to terminate: "))
    if start is "y":
        try:
            selfProcess = Process(target=Main,
                                  args=(selfCode, targetCode, "self",
                                        srcParentDir, platform, ttsEngine,
                                        translatorEngine, speechEngine,
                                        startCallStamp,))
            targetProcess = Process(target=Main,
                                    args=(targetCode, selfCode, "target",
                                          srcParentDir, platform, ttsEngine,
                                          translatorEngine, speechEngine,
                                          startCallStamp,))
            selfProcess.start()
            targetProcess.start()
            while selfProcess.is_alive() and targetProcess.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            selfProcess.terminate()
            targetProcess.terminate()
            selfProcess.join()
            targetProcess.join()
            print "Program is about to be terminated"
    terminate(selfID, targetID)
    print "Program is terminated"
    delete = None
    while delete not in ["y", "n"]:
        delete = str(raw_input("Do you wish to delete recorded files? " +
                               "Enter either 'y' or 'n': "))
    if delete == "y":
        subprocess.Popen("rm -r {}/data/*/*".format(srcParentDir),
                         shell=True).communicate()
