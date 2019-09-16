PyPortal Alarm Clock
========

An alarm clock based on the PyPortal from Adafruit. This reads the alarm time from a file on a server so that the time can be set remotely. It is hard coded to skip playing the alarm on the weekends and also if the alarm time is "0000". The alarm sound is played in the background and supports long audio files (limited only by the storage on the PyPortal or the attached SD card). To silence the alarm simply touch the screen.

Changes needed:
* PERIODICALLY MAKE COPIES OF PYPORTAL CONTENTS (write script)

* Implement my own play_file so I can close the wavfile? If can't close the existing code

* TEST: Be sure alarm sound continues and doesn’t end once the minute changes
* TEST: Hissing sound from speaker on PyPortal when I woke up. Added speaker disable code. Cut on-board connector.
* TEST: Does alarm sound at 7am? How about a forced time slot?

* Can I re-record the Feather alarm sound so it is usable?

* Trim speaker connection for on-board speaker
Speaker info: https://learn.adafruit.com/adafruit-pyportal/pinouts
Cut on-board speaker when finalized code: https://forums.adafruit.com/viewtopic.php?f=60&t=151715&p=749029&hilit=pyportal+speaker#p749029

* Change the display background while alarm is sounding? Flash it?

* Add back Weather info - requires finding way to fetch two different URLs. Not sure how to display this though