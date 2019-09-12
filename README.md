PyPortal Alarm Clock
========

Possible way to change text color: https://forums.adafruit.com/viewtopic.php?f=60&t=150952&p=770829&hilit=PyPortal#p770829

Changes needed:
* PERIODICALLY MAKE COPIES OF PYPORTAL CONTENTS (write script)

* Add retrieval of alarm time - requires replace weather fetch with alarm fetch
* Automatically skip alarm on weekends
* Remove ability to change the alarm time
* Remove Mugsy code
* Center Time display
* Either remove background BMPs or replace with something else
* Change or remove display of current alarm time
* Change the display background while alarm is sounding? Flash it?
* Remove Snooze button code
* Add back Weather info - requires finding way to fetch two different URLs
* Remove my dead SD card access code and imports if not needed or fix it per the above idea
* Remove unnecessary files from the SD card

Part of original description
An alarm clock, complete with a display of the current weather, a snooze button, and the ability to trigger another function... for example asking an IoT coffee maker to start brewing that crucial first coffee of the morning.

The clock displays both the time and weather. When the alarm is enabled and the set time is reached, the alarm sounds and the alarm screen is displayed. The alarm sound is taken in the file alarm.wav in the CIRCUITPY directory.

If the screen is touched anywhere, the alarm is silenced until the next day. If the snooze button is pressed instead, the alarm is silenced for 10 minutes. In both cases, the main time screen is displayed. If snoozing is active, an indicator is displayed on the time screen and if the snooze button is pressed, snoozing is canceled. Snoozing is also canceled if you switch to the alarm settings screen.

If you press the alarm button on the time screen (at the top left, next to the weather icon) it switches to the alarm setting screen. There are three touch areas on the left and the alarm time displayed in a large font. On this screen you can enable (by touching the green area) and disable (the red area) as well as adjust the alarm time. You do this by slowly swiping up or down over the hours and minutes. When you're done, touch the yellow arrow area between the green and red areas. This returns you to the main time screen.