"""
My version of a PyPortal alarm clock. Reads alarm time from server, supports long alarm sounds

Author: Ron Guest ronguest@protonmail.com
"""

#pylint:disable=redefined-outer-name,no-member,global-statement
#pylint:disable=no-self-use,too-many-branches,too-many-statements
#pylint:disable=useless-super-delegation, too-many-locals

import time
import json
from secrets import secrets
import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.label import Label
from digitalio import DigitalInOut, Direction, Pull
import analogio
import displayio
import adafruit_logging as logging
import storage
import adafruit_sdcard
import os
import busio

alarm_url = secrets['alarm_url']    # Load this before setting up PyPortal
print('alarm URL ', alarm_url)
force_alarm = False             ### For debugging only
do_once = True                  ### Used to log something only once

####################
# setup hardware
pyportal = PyPortal(url=alarm_url,
                    status_neopixel=board.NEOPIXEL)


####################
# variables

# alarm support
# alarm_file = 'alarm.wav'
alarm_file = 'fnafs.wav'
alarm_time = '1111'             # Value is read from server so this one doesn't matter
alarm_hour = 0                  # Computed from alarm_time string
alarm_minute = 0

# The most recently fetched time
current_time = None

####################
# Load the fonts
time_font = bitmap_font.load_font('/fonts/Anton-Regular-104.bdf')
time_font.load_glyphs(b'0123456789:') # pre-load glyphs for fast printing

alarm_font = bitmap_font.load_font('/fonts/Nunito-Black-17.bdf')
alarm_font.load_glyphs(b'0123456789:Wakeupat ')

####################
# Set up logging
logger = logging.getLogger('alarm_clock')
logger.setLevel(logging.INFO)            # change as desired

backlight_on = 0.8
pyportal.set_backlight(backlight_on)

time_color = 0x00ff00               # bright green
time_position = (70,80)
time_textarea = Label(time_font, max_glyphs=15, color=time_color,
                      x=time_position[0], y=time_position[1])

wakeup_time_color = 0xFFFFFF
wakeup_time_position = (70,220)
wakeup_time_textarea = Label(alarm_font, max_glyphs=30, color=wakeup_time_color,
                             x=wakeup_time_position[0], y=wakeup_time_position[1])

pyportal.splash.append(time_textarea)
pyportal.splash.append(wakeup_time_textarea)

# Get initial time, retry if needed
while True:
    try:
        # print("Getting time from internet!")
        pyportal.get_local_time()
    except RuntimeError as e:
        print("Time set error occured, retrying! -", e)
        continue
    break

def displayTime():
    now = time.localtime()
    hour, minute = now[3:5]
    formatTime(hour, minute)
    time_textarea.text = formatTime(hour, minute)
    return formatTime(hour, minute)

def formatTime(raw_hours, raw_minutes):
    # display the time in a nice big font
    format_str = "%d:%02d"
    if raw_hours >= 12:
        raw_hours -= 12
    if raw_hours == 0:
        raw_hours = 12
    time_str = format_str % (raw_hours, raw_minutes)
    return time_str

### Main Loop
refresh_time = None

while True:
    time_now = time.localtime()
    # only query the online time and alarm time once per hour (and on first run)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting alarm time")
            alarm_time = pyportal.fetch()
            print(alarm_time)
            # Try to protect against a bad return from fetch(). Ignore if not digits.
            if alarm_time.isdigit():
                alarm_hour = int(alarm_time[:2])
                alarm_minute = int(alarm_time[-2:])
        except RuntimeError as e:
            print("Exception getting alarm time - ", e)
        try:
            print("Getting time from internet")
            pyportal.get_local_time()
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Time set exception occured, retrying! -", e)
            continue
    time_str_text = displayTime()

    # We skip alarms on the weekend, also if alarm time is zero (which means disabled from server)
    if (time_now.tm_wday) == 4 or (time_now.tm_wday == 5) or (alarm_time[:4] == "0000"):
        input_wake_up_time_text = "No alarm set for tomorrow"
    else:
        input_wake_up_time_text = "Wake up at " + alarm_time
    wakeup_time_textarea.text = input_wake_up_time_text

    # See if it is time to play the alarm sound, always skip Saturday (5) & Sunday (6)
    if ((time_now.tm_wday) != 5 and (time_now.tm_wday != 6)) or force_alarm:
        if ((alarm_hour == time_now.tm_hour) and (alarm_minute == time_now.tm_min)) or force_alarm:
            # If a file is already playing leave it alone, else start playing
            if pyportal.audio.playing == False:
                print("Start the alarm file")
                pyportal._speaker_enable.value = True
                pyportal.play_file(alarm_file, False)
            # print('audio_playing is ', pyportal.audio.playing)

    # The only purpose of touching the screen is to stop the alarm, so that's all we check here
    # I feel I need to close the WAV file when the audio finishes but I don't see a way to do so
    if pyportal.touchscreen.touch_point != None:
        print('Screen touched')
        pyportal._speaker_enable.value = False
        pyportal.audio.stop()
        force_alarm = False

    # update every half second for timely response to screen touches
    time.sleep(.5)