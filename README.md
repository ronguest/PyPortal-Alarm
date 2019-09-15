PyPortal Alarm Clock
========

An alarm clock based on the PyPortal from Adafruit. This reads the alarm time from a file on a server so that the time can be set remotely. It is hard coded to skip playing the alarm on the weekends and also if the alarm time is "0000". The alarm sound is played in the background and supports long audio files (limited only by the storage on the PyPortal or the attached SD card). To silence the alarm simply touch the screen.

Changes needed:
* PERIODICALLY MAKE COPIES OF PYPORTAL CONTENTS (write script)

* Trim speaker connection for on-board speaker
Speaker info: https://learn.adafruit.com/adafruit-pyportal/pinouts
Cut on-board speaker when finalized code: https://forums.adafruit.com/viewtopic.php?f=60&t=151715&p=749029&hilit=pyportal+speaker#p749029

* Do I need to find a way to close the alarm file after audio is done, since playing in the background?

* Change the display background while alarm is sounding? Flash it?

* Add back Weather info - requires finding way to fetch two different URLs

* Remove SD card
