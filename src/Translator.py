# -*- coding: utf-8 -*-

import argparse
import Toolbox
import Internals


def Main(selfCode, targetCode, who, ttsEngine, translatorEngine, speechEngine,
         callName):
    forWho = Toolbox.whoPrime(who)
    srcParentDir = Toolbox.config()[-2]
    Toolbox.makeNoiseProfile(srcParentDir, who, "00:05")
    success = True
    while True:
        # if success:
        #     Toolbox.beep(True, who)
        # elif not success:
        #     Toolbox.beep(False, who)
        filePath = Internals.speechRecorder(selfCode, who, srcParentDir)
        if filePath is None:
            success = False
        elif filePath is not None:
            selfText = Internals.speech2text(selfCode, filePath, speechEngine)
            if selfText is None:
                success = False
            elif selfText is not None:
                translatedText = Internals.translateText(selfText, selfCode,
                                                         targetCode,
                                                         translatorEngine)
                finalFilePath = Internals.text2speech(translatedText,
                                                      targetCode, who,
                                                      srcParentDir, ttsEngine)
                if finalFilePath is None:
                    success = False
                if finalFilePath is not None:
                    Toolbox.writeLog(translatedText, who, selfText, selfCode,
                                     srcParentDir, callName)
                    Toolbox.playSpeech(finalFilePath, forWho)
                    success = True


def argumentHandler():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--selfCode", required=True,
                        help="Two letter code for self's language", type=str)
    parser.add_argument("-t", "--targetCode", required=True,
                        help="Two letter code for target's language", type=str)
    parser.add_argument("-w", "--who", required=True,
                        help="who initiated the translation? self or target?",
                        type=str, choices=["self", "target"])
    parser.add_argument("-e", "--ttsEngine", required=True,
                        help="Which tts engine should be used?", type=str,
                        choices=["espeak", "google", "bing", "nuance"])
    parser.add_argument("-tr", "--translatorEngine", required=True,
                        help="Which translator engine should be used?",
                        type=str, choices=["google", "bing"])
    parser.add_argument("-sp", "--speechEngine", required=True,
                        help="Which speech to text engine should be used?",
                        type=str, choices=["google", "bing", "nuance"])
    parser.add_argument("-n", "--callName", required=True,
                        help="What's the call/log name?", type=str)
    args = parser.parse_args()
    return (args.selfCode, args.targetCode, args.who, args.ttsEngine,
            args.translatorEngine, args.speechEngine, args.callName)

if __name__ == '__main__':
    (selfCode, targetCode, who, ttsEngine, translatorEngine, speechEngine,
     callName) = argumentHandler()
    Main(selfCode, targetCode, who, ttsEngine, translatorEngine, speechEngine,
         callName)
