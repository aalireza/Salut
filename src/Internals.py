# -*- coding: utf-8 -*-

from Azure import azure_translate_api as azure
from gtts import gTTS
import GoogleTranslate as gt
import Toolbox
import pyoxford
import requests
import speech_recognition as sr
import subprocess
import os


def googleSpeech(filePath, langCode):
    recognizerModule = sr.Recognizer(language=langCode)
    with sr.WavFile(filePath) as source:
        audio = recognizerModule.record(source)
    try:
        text = str(recognizerModule.recognize(audio).encode("utf-8"))
        return text
    except LookupError:
        print "Speech is unintelligible."
        return None


def bingSpeech(filePath, langCode):
    clientID, _, clientKey = Toolbox.microsoftConfig()
    api = pyoxford.speech(clientID, clientKey)
    langCode = Toolbox.langCodeRegularize(langCode)
    try:
        text = api.speech_to_text(filePath)
        return text
    except:
        print "Speech is unintelligible"
        return None


def nuanceSpeech(filePath, langCode):
    appID, appKey = Toolbox.nuanceConfig()
    headers = {'Content-Type': 'audio/x-wav;codec=pcm;bit=16;rate=16000',
               'Accept': 'text/plain',
               'Accept-Language': Toolbox.langCodeRegularize(langCode)}
    params = {'appId': appID,
              'appKey': appKey,
              'ttsLang': Toolbox.langCodeRegularize(langCode),
              'id': '123456'}
    with open(filePath, 'rb') as f:
        data = f.read()
        try:
            text = requests.post("https://dictation.nuancemobility.net/NMDPAsrCmdServlet/dictation",
                                headers=headers, params=params, data=data)
            detected = text.content
            if '\n' in detected:
                candidates = detected.split('\n')
            if "<html>" not in candidates[0]:
                return candidates[0]
            elif "<html>" in candidates[0]:
                print "Speech is unintelligible"
                return None
        except:
            print "Speech is unintelligible"
            return None


def speechRecognizer(filePath, langCode, speechEngine):
    text = globals()[str(speechEngine).lower() + "Speech"](filePath, langCode)
    return text


def speechRecorder(langCode, who, srcParentDir):
    assert who in ["self", "target"], "'who' is neither self nor target"
    soxCard = Toolbox.soxCardHandler(who)
    stamp = Toolbox.timeStamp()
    filePath = str("{}/data/{}/{}-rec-{}-{}.wav").format(srcParentDir, who, who,
                                                         langCode, stamp)
    fileDir = os.path.dirname(filePath)
    subprocess.Popen(str("sox -t {} {} rate 16000 noisered {}/noise.prof 0.26" +
                         " silence 2 1 5% 1.5 2.0 0.5%").format(soxCard,
                                                                filePath,
                                                                fileDir),
                     shell=True).communicate()
    print filePath
    if os.path.exists(filePath):
        directory = "{}/".format(os.path.dirname(filePath))
        baseName = str("mono-" + os.path.basename(filePath))
        monoPath = directory + baseName
        print monoPath
        subprocess.Popen(str("sox {} {} channels 1".format(filePath, monoPath)),
                         shell=True).communicate()
        if os.path.exists(monoPath):
            return monoPath
    return None


def speech2text(langCode, filePath, speechEngine):
    selfText = speechRecognizer(filePath, langCode, speechEngine)
    if selfText is not None:
        return selfText


def googleTranslate(text, targetCode, selfCode):
    textTranslate = gt.translate(text, targetCode, selfCode)
    return textTranslate.replace("&#39;", "'")


def bingTranslate(text, targetCode, selfCode):
    clientID, clientSecret, _ = Toolbox.microsoftConfig()
    client = azure.MicrosoftTranslatorClient(clientID, clientSecret)
    textTranslate = client.TranslateText(text, selfCode, targetCode)
    cleanText = textTranslate[textTranslate.find('"') + 1:
                              textTranslate.find('"',
                                                 textTranslate.find('"') + 1)]
    return cleanText.replace("&#39;", "'")


def translateText(text, selfCode, targetCode, translatorEngine):
    textTranslate = globals()[str(translatorEngine) + "Translate"](text,
                                                                   targetCode,
                                                                   selfCode)
    return textTranslate


def googleTTS(inputText, langCode, filePath):
    speech = gTTS(text=str(inputText), lang=langCode)
    speech.save(filePath)


def espeakTTS(inputText, langCode, filePath):
    subprocess.Popen("""espeak -v {} -s 110 "{}" --stdout > "{}" """.format(
        langCode, inputText, filePath), shell=True).communicate()


def bingTTS(inputText, langCode, filePath):
    clientID, _, clientKey = Toolbox.microsoftConfig()
    api = pyoxford.speech(clientID, clientKey)
    langCode = Toolbox.langCodeRegularize(langCode)
    binarySound = api.text_to_speech(inputText, langCode)
    with open(filePath, "wb") as f:
        f.write(binarySound)
    return filePath


def nuanceTTS(inputText, langCode, filePath):
    appID, appKey = Toolbox.nuanceConfig()
    headers = {'Content-Type': 'text/plain',
               'Accept': 'audio/x-wav'}
    params = {'appId': appID,
              'appKey': appKey,
              'ttsLang': Toolbox.langCodeRegularize(langCode),
              'id': '123456'}
    soundFile = requests.post("https://tts.nuancemobility.net:443/NMDPTTSCmdServlet/tts",
                              params=params, headers=headers, data=inputText)
    with open(filePath, 'wb') as f:
        f.write(soundFile.content)
    return filePath


def text2speech(inputText, langCode, who, srcParentDir, ttsEngine):
    assert who in ["self", "target"], ("'who' argument is neither " +
                                       "self nor target.")
    stamp = Toolbox.timeStamp()
    filePath = "{}/data/{}/{}-speech-{}-{}.mp3".format(srcParentDir, who, who,
                                                       langCode, stamp)
    try:
        globals()[str(ttsEngine).lower() + "TTS"](inputText, langCode, filePath)
    except:
        print "Language Not Supported"
        return None
    if not os.path.exists(filePath):
        print "Something went wrong with {} tts".format(ttsEngine)
        return None
    return filePath
