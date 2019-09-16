PyPortal Alarm Clock
========

An alarm clock based on the PyPortal from Adafruit. This reads the alarm time from a file on a server so that the time can be set remotely. It is hard coded to skip playing the alarm on the weekends and also if the alarm time is "0000". The alarm sound is played in the background and supports long audio files (limited only by the storage on the PyPortal or the attached SD card). To silence the alarm simply touch the screen.

Changes needed:
* PERIODICALLY MAKE COPIES OF PYPORTAL CONTENTS (write script)

* Alarm DID NOT sound at 7:00. Speaker was hissing. Don't know if related. I think my check for time validity was wrong hence the alarm time wasn't actually set

* Pad out hours and minutes for alarm time display
* Implement my own play_file so I can close the wavfile? If can't close the existing code
* Be sure alarm sound continues and doesn’t end once the minute changes
* Add timeout on PyPortal alarm so it doesn’t sound forever. Something like 10 minutes?
* Hissing sound from speaker on PyPortal when I woke up. Added speake disable code
* Can I re-record the Feather alarm sound so it is usable?

* Trim speaker connection for on-board speaker
Speaker info: https://learn.adafruit.com/adafruit-pyportal/pinouts
Cut on-board speaker when finalized code: https://forums.adafruit.com/viewtopic.php?f=60&t=151715&p=749029&hilit=pyportal+speaker#p749029

* Do I need to find a way to close the alarm file after audio is done, since playing in the background?

* Change the display background while alarm is sounding? Flash it?

* Add back Weather info - requires finding way to fetch two different URLs

* Remove SD card
