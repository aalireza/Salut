# Salut
Real-time Low-latency open-source phone call translator

---
<h3> How does it work? </h3>

<b>TL;DR</b>

1. Alice's system's usual config: Microphone ---> Skype ---> Speakers
2. Alice's system while running the program: Microphone ---> "self"[VirtualAudioDevice] ---> Skype ---> "target"[VirtualAudioDevice] ---> Speakers
3. No change happens on Bob's and he doesn't need to install anything or be connected to internet or whatever.

+++

Alice and Bob evidently don't speak the same language but for the sake of this example, Alice is trying to call Bob on his phone
from her Skype. Alice installs this software on her computer. Under regular circumstances, the input of Skype is microphone and the output
is the speakers. However two virtual audio devices called "self" and "target" are created and, temporarily and as
long as the program is running, Skype's input device is replaced with the output of 'self' and output device of Skype
is replaced with the input of 'target'.

After calling Bob, as soon as he picks up, a script will run to record and analyze the noise of the environment thus
enabling the program to cancel them when someone speaks and also detecting when someone has stopped speaking. 
After the noise profile is created, the recording of both parties begins in parallel. Alice says 
something. Two seconds after she stops (i.e. detecting silence based on the noise profile previously created), her 
speach is transformed to text and her text is translated and the result is synthesized back to speech. The speech file that'll 
get played to the output of 'self' (i.e. input of Skype) so that Bob can hear it. When Bob says 
something, his original voice will get passed through Skype and all of the processing will be done on Alice's system,
except the virtual audio device would be 'target'. Also, due to the fact that the origin of Bob's speech is not Alice's microphone but
it's Skype's output, an additional noise cancellation will be done on his speech.


---
<h3> Implemented options </h3>

<b>Text to Speech:</b> Available options are as follows:
- `espeak`: The only open-source/free and most reliable of all, though it sounds exceedingly Hawkingian.
- `bing`: You need an account. Enter your information in ./config.txt
- `google`: Not that reliable. It's undocumented and changes rapidly.
- `nuance`: Best, if you have an account. Enter your information in ./config.txt

<b>Translation:</b> Available options are as follows:
- `google`: You have to pay for the API if you're planning to use it extensively.
- `bing`: You need an account. Enter your information in ./config.txt

<b>Speech to Text:</b> Available options are as follows:
- `google`
- `bing`: You need an acount. Enter your information in ./config.txt
- `nuance`: You need an account. Enter your information in ./config.txt

<b>Messengers:</b> Everything! Provided that it can be run via terminal using PulseAudio's environment variables.

<b>Languages:</b>
- English
- French
- German
- Spanish
- Italian

---
<h3> Known Issues </h3>
1. Machine translation is not sufficiently accurate... of course.
2. One should implement Speech to text via Sphinx. Good luck.
3. Excessive requests make Google to request a CAPTCHA rendering the script useless. If that happens to Speech to text, go to the point above. If that happens to translation, pay for it and add your key to the config.txt. If that happens to text to speech, use espeak.
4. Noise profile will be created based on the first five seconds of the call. Any more noise (even Lap top's fan) and you're screwed. You can create a noise profile in parallel while you're not recording, but in Python child processes can't create processes or something. Easiest <b>Solution</b> is to use a microphone!
5. Everything has to run smoothly, don't kill the process abruptly. PulseAudio modules have to be unloaded at the End. Otherwise do `pulseaudio -k` or restart your computer.

---
<h3> Dependencies: </h3>
- Python 2.7
- espeak
- [PulseAudio](https://wiki.freedesktop.org/www/Software/PulseAudio/)
- [Sox](http://sox.sourceforge.net/)
- `libsox-fmt-all` (especifically `libsox-fmt-pulse` and `libsox-fmt-mp3`)
- [gTTS](https://pypi.python.org/pypi/gTTS/)
- [PyAudio](https://pypi.python.org/pypi/PyAudio)
- [Speech Recognition](https://pypi.python.org/pypi/SpeechRecognition/)
- [pyoxford](https://pypi.python.org/pypi/pyoxford)
- [requests](https://pypi.python.org/pypi/requests/)
- Skype or practically any other VoIP client

<b>Remark:</b> This program has only been tested on my Ubuntu machine! :-D

<b>Remark:</b> Making PulseAudio work on OS X may be problematic. Nonetheless I've inserted an AppleScript that's supposed to run the program the same way it would have been run had you had linux provided that all other dependencies are satisfied. Instead of PulseAudio, one could use [Soundflower](https://github.com/RogueAmoeba/Soundflower) with a slight change in subprocess.Popens that call sox... However I haven't had enough time to implement it.

<b>Remark:</b> It won't work on Windows categorically.

<b>Remark:</b> You may install libsox libraries via `apt-get` if you're on Ubuntu.

---
<h3> How to work with it: </h3>
1. Make sure you've got all of the dependencies installed.
2. Clone this project into your machine (or download it as zip and extract it).
3. Go to the program's directory and open up `config.txt`. Enter the location of Skype (or any other
messanger) in MESSENGER, the language you want to speak in SELF_LANG_CODE and that of your target in
TARGET_LANG_CODE 
4. Close your messanger (the program you've putted in `config.txt`) if it's already open.
5. Open up your terminal and enter `python -e google path-to-your-clone/src/main.py` (so if you've downloaded it zip and extracted it in Documents/ the command would be `python Salut-master/src/main.py -e ttsEngine -tr translatorEngine -sp speechEngine`). Look at `python Salut-master/src/main.py -h` for the available options. (A sample command would look like `python Salut-master/src/main.py -e espeak -tr google -sp google`)
6. You'll see that your messanger opens up. Call someone.
7. After they've picked up, press 'y' in the terminal to start making a noise profile. Two other terminals will open up.
8. After noise profile is created, You may speak.
9. To conclude the call, go to the first terminal (not the two that are recording you), press Ctrl+C (You'll see the other two terminals go away with your messanger) then either press 'y' to delete the temporary speech files or 'n' to save them.
