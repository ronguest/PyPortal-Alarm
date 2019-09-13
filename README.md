PyPortal Alarm Clock
========

An alarm clock based on the PyPortal from Adafruit. This reads the alarm time from a file on a server so that the time can be set remotely. It is hard coded to skip playing the alarm on the weekends and also if the alarm time is "0000". The alarm sound is played in the background and supports long audio files (limited only by the storage on the PyPortal or the attached SD card). To silence the alarm simply touch the screen.

Changes needed:
* PERIODICALLY MAKE COPIES OF PYPORTAL CONTENTS (write script)

* Automatically skip alarm on weekends and be sure it works

* Change the display background while alarm is sounding? Flash it?

* Add back Weather info - requires finding way to fetch two different URLs

* Remove SD card
