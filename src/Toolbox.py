# -*- coding: utf-8 -*-

from subprocess import Popen
from subprocess import check_output
import ConfigParser
import time
import os
import sys


def config():
    configParser = ConfigParser.RawConfigParser()
    srcDir = os.path.dirname(os.path.abspath(__file__))
    srcParentDir = os.path.dirname(srcDir)
    configFilePath = '{}/config.txt'.format(srcParentDir)
    configParser.read(configFilePath)
    messenger = configParser.get('System', 'MESSENGER')
    selfCode = configParser.get('Languages', 'SELF_LANG_CODE')
    targetCode = configParser.get('Languages', 'TARGET_LANG_CODE')
    oneDingFile = configParser.get('System', 'SAY')
    oneDing = "{}/{}".format(srcParentDir, oneDingFile)
    twoDingFile = configParser.get('System', 'REPEAT')
    twoDing = "{}/{}".format(srcParentDir, twoDingFile)
    platform = sys.platform
    return (messenger, selfCode, targetCode, oneDing, twoDing,
            srcDir, srcParentDir, platform)


def microsoftConfig():
    configParser = ConfigParser.RawConfigParser()
    srcDir = os.path.dirname(os.path.abspath(__file__))
    srcParentDir = os.path.dirname(srcDir)
    configFilePath = '{}/config.txt'.format(srcParentDir)
    configParser.read(configFilePath)
    clientID = configParser.get('MicrosoftAzure', 'CLIENT_ID')
    clientSecret = configParser.get('MicrosoftAzure', 'CLIENT_TRANSLATE_SECRET')
    clientKey = configParser.get('MicrosoftAzure', 'CLIENT_OXFORD_KEY')
    return clientID, clientSecret, clientKey


def nuanceConfig():
    configParser = ConfigParser.RawConfigParser()
    srcDir = os.path.dirname(os.path.abspath(__file__))
    srcParentDir = os.path.dirname(srcDir)
    configFilePath = '{}/config.txt'.format(srcParentDir)
    configParser.read(configFilePath)
    appID = configParser.get('Nuance', 'APP_ID')
    appKey = configParser.get('Nuance', 'APP_KEY')
    return appID, appKey


def timeStamp():
    return str(time.time()).replace(".", "")


def checkDataDir(srcParentDir):
    if not os.path.exists("{}/data".format(srcParentDir)):
        os.makedirs("{}/data".format(srcParentDir))
    if not os.path.exists("{}/data/self".format(srcParentDir)):
        os.makedirs("{}/data/self".format(srcParentDir))
    if not os.path.exists("{}/data/self/log".format(srcParentDir)):
        os.makedirs("{}/data/self/log".format(srcParentDir))
    if not os.path.exists("{}/data/target".format(srcParentDir)):
        os.makedirs("{}/data/target".format(srcParentDir))
    if not os.path.exists("{}/data/target/log".format(srcParentDir)):
        os.makedirs("{}/data/target/log".format(srcParentDir))


def soxCardHandler(who):
    assert who in ["self", "target"], "'who' is neither self nor target"
    if who == "self":
        return "alsa default"
    elif who == "target":
        return "pulseaudio target.monitor"


def langCodeRegularize(langCode):
    if langCode == "en":
        langCode = "en-US"
    elif langCode == "es":
        langCode = "es-MX"
    elif langCode == "fr":
        langCode = "fr-FR"
    elif langCode == "de":
        langCode = "de-DE"
    elif langCode == "it":
        langCode = "it-IT"
    return langCode


def whoPrime(who):
    return str((set(["self", "target"]) - set([who])).pop())


def translatorScriptCreator(srcParentDir, selfCode, targetCode, who, ttsEngine,
                            translatorEngine, speechEngine, callName):
    script = ("python {}/src/Translator.py -s {} -t {} -w {} -e {} " +
              "-tr {} -sp {} -n {}").format(srcParentDir, selfCode, targetCode,
                                            who, ttsEngine, translatorEngine,
                                            speechEngine, callName)
    scriptPath = "{}/data/{}/{}-TranslatorScript.sh".format(srcParentDir,
                                                            who, who)
    Popen("echo '#!/bin/bash' > {}".format(scriptPath),
          shell=True).communicate()
    Popen("echo '{}' >> {}".format(script, scriptPath),
          shell=True).communicate()
    if not os.path.exists(scriptPath):
        print "Something went wrong with script generator of {}".format(who)
        return None
    else:
        Popen("chmod +x {}".format(scriptPath), shell=True).communicate()
        return scriptPath


def writeLog(text, who, original, langCode, srcParentDir, callName):
    filePath = "{}/data/{}/log/{}-{}.txt".format(srcParentDir, who, who,
                                                 callName)
    if not os.path.exists(filePath):
        Popen("""echo ">>>>>>>> {}'s LangCode: {}" > {}""".format(who, langCode,
                                                                  filePath),
              shell=True).communicate()
    Popen("""echo "{} ---> {}" >> {}""".format(original, text, filePath),
          shell=True).communicate()


def readLogScriptCreator(who, srcParentDir, callName):
    logScriptPath = "{}/data/{}/log/{}-{}.sh".format(srcParentDir, who, who,
                                                     callName)
    logPath = "{}/data/{}/log/{}-{}.txt".format(srcParentDir, who, who,
                                                callName)
    Popen("touch {}".format(logPath), shell=True).communicate()
    command = "watch -n1 'cat {}'".format(logPath)
    Popen("echo '#!/bin/bash' > {}".format(logScriptPath),
          shell=True).communicate()
    Popen("echo '{}' >> {}".format(command, logScriptPath),
          shell=True).communicate()
    if not os.path.exists(logScriptPath):
        print "Something went wrong with log script generator of {}".format(who)
        return None
    else:
        Popen("chmod +x {}".format(logScriptPath), shell=True).communicate()
        return logScriptPath


def makeNoiseProfile(srcParentDir, who, length):
    assert who in ["self", "target"], ("'who' argument is neither self nor " +
                                       "target")
    filePath = "{}/data/{}/noise.wav".format(srcParentDir, who)
    fileDir = os.path.dirname(filePath)
    soxCard = soxCardHandler(who)
    Popen("sox -t {} {} trim 0 {}".format(soxCard, filePath, length),
          shell=True).communicate()
    if not os.path.exists(filePath):
        print "Something went wrong with initial background noise recording"
        return None
    Popen("sox {} -n noiseprof {}/noise.prof".format(filePath, fileDir),
          shell=True).communicate()
    print "We got to this point"
    if not os.path.exists("{}/noise.prof".format(fileDir)):
        print "Something went wrong with noise profile generation"
        return None
    return True


def playSpeech(path, forWho):
    assert forWho in ["self", "target"], "'forwho' neither self nor target"
    if forWho == "target":
        Popen("PULSE_SINK=self play -v 2 {}".format(path),
              shell=True).communicate()
    elif forWho == "self":
        Popen("play -v 1 {}".format(path), shell=True).communicate()


def beep(itWasPlayed, who):
    if itWasPlayed:
        oneDing = config()[3]
        playSpeech(oneDing, who)
    elif not itWasPlayed:
        twoDing = config()[4]
        playSpeech(twoDing, who)


def loadNull(who):
    assert who in ["self", "target"], "'who' is neither self nor target"
    procID = check_output("pactl load-module module-null-sink " +
                          "sink_name={}".format(who), shell=True)
    procID = int(procID.rstrip('\n'))
    if type(procID) != int:
        print "Loading module for '{}' failed".format(who)
        raise SystemExit
    print ("Loaded module-null-sync with index: " + str(procID) +
           ", for '{}' successfuly.".format(who))
    return procID


def unloadNull(ID):
    Popen("pactl unload-module " + str(ID), shell=True)


def callMessenger(messenger):
    Popen("PULSE_SOURCE=self.monitor PULSE_SINK=target {}".format(messenger),
          shell=True)
