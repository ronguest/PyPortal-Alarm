PyPortal Alarm Clock
========

An alarm clock, complete with a display of the current weather, a snooze button, and the ability to trigger another function... for example asking an IoT coffee maker to start brewing that crucial first coffee of the morning.

The clock displays both the time and weather. When the alarm is enabled and the set time is reached, the alarm sounds and the alarm screen is displayed. The alarm sound is taken in the file alarm.wav in the CIRCUITPY directory.

If the screen is touched anywhere, the alarm is silenced until the next day. If the snooze button is pressed instead, the alarm is silenced for 10 minutes. In both cases, the main time screen is displayed. If snoozing is active, an indicator is displayed on the time screen and if the snooze button is pressed, snoozing is canceled. Snoozing is also canceled if you switch to the alarm settings screen.

If you press the alarm button on the time screen (at the top left, next to the weather icon) it switches to the alarm setting screen. There are three touch areas on the left and the alarm time displayed in a large font. On this screen you can enable (by touching the green area) and disable (the red area) as well as adjust the alarm time. You do this by slowly swiping up or down over the hours and minutes. 
When you're done, touch the yellow arrow area between the green and red areas. This returns you to the main time screen.

I don't think this code syncs with Internet time, unlike the light version.

The final piece of functionality is what the author has done as a Mugsy command. The intent with this is to use it to send a command to another IoT device; in this case a Mugsy coffee maker, but it could as easily be to tell your IoT lighting to turn on, or the motorized blinds to open.
