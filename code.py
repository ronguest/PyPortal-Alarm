"""
PyPortal based alarm clock.

Adafruit invests time and resources providing this open source code.
Please support Adafruit and open source hardware by purchasing
products from Adafruit!

Written by Dave Astels for Adafruit Industries
Copyright (c) 2019 Adafruit Industries
Licensed under the MIT license.

All text above must be included in any redistribution.
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

alarm_time = "9999"
ALARM_URL = 'http://10.0.1.38/ashley_alarm.txt'

####################
# setup hardware
pyportal = PyPortal(url=ALARM_URL,
                    status_neopixel=board.NEOPIXEL)

light = analogio.AnalogIn(board.LIGHT)

#print('-> the sd directory follows:', os.listdir('/sd'))

####################
# variables

# alarm support
alarm_file = 'alarm.wav'
alarm_armed = True
alarm_enabled = True
alarm_hour = 0
alarm_minute = 0
alarm_interval = 10.0

# display/data refresh timers

refresh_time = None
update_time = None

# The most recently fetched time
current_time = None

# track whether we're in low light mode
low_light = False

# screen touched
touched = False

####################
# Load the fonts
time_font = bitmap_font.load_font('/fonts/Anton-Regular-104.bdf')
time_font.load_glyphs(b'0123456789:') # pre-load glyphs for fast printing

alarm_font = bitmap_font.load_font('/fonts/Helvetica-Bold-36.bdf')
alarm_font.load_glyphs(b'0123456789:')

####################
# Set up logging
logger = logging.getLogger('alarm_clock')
logger.setLevel(logging.INFO)            # change as desired
do_once = True                           # Debug flag for something to log once

####################
# Functions

def create_text_areas(configs):
    """Given a list of area specifications, create and return test areas."""
    text_areas = []
    for cfg in configs:
        textarea = Label(cfg['font'], text=' '*cfg['size'])
        textarea.x = cfg['x']
        textarea.y = cfg['y']
        textarea.color = cfg['color']
        text_areas.append(textarea)
    return text_areas


def clear_splash():
    for _ in range(len(pyportal.splash) - 1):
        pyportal.splash.pop()


####################
# states

class State(object):
    """State abstract base class"""

    def __init__(self):
        pass


    @property
    def name(self):
        """Return the name of teh state"""
        return ''


    def tick(self, now):
        """Handle a tick: one pass through the main loop"""
        pass


    #pylint:disable=unused-argument
    def touch(self, t, touched):
        """Handle a touch event.
        :param (x, y, z) - t: the touch location/strength"""
        return bool(t)


    def enter(self):
        """Just after the state is entered."""
        pass


    def exit(self):
        """Just before the state exits."""
        clear_splash()


class Time_State(State):
    """This state manages the primary time display screen/mode"""

    def __init__(self):
        super().__init__()
        self.refresh_time = None
        self.update_time = None
        text_area_configs = [dict(x=88, y=170, size=5, color=0xFFFFFF, font=time_font),
                             dict(x=210, y=50, size=5, color=0xFF0000, font=alarm_font)]
        self.text_areas = create_text_areas(text_area_configs)

        # each button has it's edges as well as the state to transition to when touched
        self.buttons = [dict(left=0, top=50, right=80, bottom=120, next_state='settings'),
                        dict(left=0, top=155, right=80, bottom=220, next_state='mugsy')]


    @property
    def name(self):
        return 'time'


    def adjust_backlight_based_on_light(self, force=False):
        """Check light level. Adjust the backlight and background image if it's dark."""
        global low_light
        if light.value <= 1000 and (force or not low_light):
            pyportal.set_backlight(0.01)
            low_light = True
        elif force or (light.value >= 2000 and low_light):
            pyportal.set_backlight(1.00)
            low_light = False


    def tick(self, now):
        global alarm_armed, update_time, current_time, alarm_time, alarm_hour, alarm_minute
        global do_once

        # only query the online time once per hour (and on first run), 3600
        if (not self.refresh_time) or ((now - self.refresh_time) > 3600):
            logger.info('Fetching alarm time')
            alarm_time = pyportal.fetch()
            alarm_time = '0924'         ##### !!!!!! Override alarm time for debugging
            logger.info('Alarm time %s', alarm_time)
            alarm_hour = alarm_time[:2]
            logger.info('Alarm hour %s', alarm_hour)
            alarm_minute = alarm_time[-2:]
            logger.info('Alarm minute %s', alarm_minute)
            if alarm_enabled:
                self.text_areas[1].text = '%2d:%02d' % (int(alarm_hour), int(alarm_minute))            
            logger.debug('Fetching time')
            try:
                pyportal.get_local_time(location=secrets['timezone'])
                self.refresh_time = now
            except RuntimeError as e:
                self.refresh_time = now - 3000   # delay 10 minutes before retrying
                logger.error('Time update error occured, retrying! - %s', str(e))

        if (not update_time) or ((now - update_time) > 30):
            # Update the time
            update_time = now
            current_time = time.localtime()
            time_string = '%02d:%02d' % (current_time.tm_hour,current_time.tm_min)
            self.text_areas[0].text = time_string
            board.DISPLAY.refresh_soon()
            board.DISPLAY.wait_for_frame()

        # Check if alarm should sound, never on a weekend
        if (current_time is not None):
            minutes_now = current_time.tm_hour * 60 + current_time.tm_min
            minutes_alarm = int(alarm_hour) * 60 + int(alarm_minute)
            if do_once:
                print('Minutes now %s', minutes_now)
                print('Minutes alarm %s',minutes_alarm)
                do_once = False
            if minutes_now == minutes_alarm:
                if alarm_armed:
                    change_to_state('alarm')
            else:
                alarm_armed = alarm_enabled


    def touch(self, t, touched):
        if t and not touched:             # only process the initial touch
            for button_index in range(len(self.buttons)):
                b = self.buttons[button_index]
                if touch_in_button(t, b):
                    change_to_state(b['next_state'])
                    break
        return bool(t)


    def enter(self):
        self.adjust_backlight_based_on_light(force=True)
        for ta in self.text_areas:
            pyportal.splash.append(ta)
        current_time = time.localtime()
        print(current_time.tm_wday)
        if alarm_enabled and (current_time.tm_wday != 3):
            self.text_areas[1].text = '%2d:%02d' % (alarm_hour, alarm_minute)
        else:
            self.text_areas[1].text = '     '
        board.DISPLAY.refresh_soon()
        board.DISPLAY.wait_for_frame()


    def exit(self):
        super().exit()

class Alarm_State(State):
    """This state shows/sounds the alarm.
    Touching anywhere on the screen cancells the alarm."""

    def __init__(self):
        super().__init__()
        self.sound_alarm_time = None


    @property
    def name(self):
        return 'alarm'


    def tick(self, now):

        # is it time to sound the alarm?
        if self.sound_alarm_time and (now - self.sound_alarm_time) > alarm_interval:
            self.sound_alarm_time = now
            pyportal.play_file(alarm_file)


    def touch(self, t, touched):
        if t and not touched:
            change_to_state('time')
        return bool(t)


    def enter(self):
        global low_light
        self.sound_alarm_time = time.monotonic() - alarm_interval
        pyportal.set_backlight(1.00)
        low_light = False
        board.DISPLAY.refresh_soon()
        board.DISPLAY.wait_for_frame()


    def exit(self):
        global alarm_armed
        super().exit()
        # alarm_armed = bool(snooze_time)


class Setting_State(State):
    """This state lets the user enable/disable the alarm and set its time.
    Swiping up/down adjusts the hours & miniutes separately."""

    def __init__(self):
        super().__init__()
        self.previous_touch = None
        text_area_configs = [dict(x=88, y=120, size=5, color=0xFFFFFF, font=time_font)]

        self.text_areas = create_text_areas(text_area_configs)
        self.buttons = [dict(left=0, top=30, right=80, bottom=93),    # on
                        dict(left=0, top=98, right=80, bottom=152),   # return
                        dict(left=0, top=155, right=80, bottom=220),  # off
                        dict(left=100, top=0, right=200, bottom = 240), # hours
                        dict(left=220, top=0, right=320, bottom = 240)]   # minutes


    @property
    def name(self):
        return 'settings'

    def touch(self, t, touched):
        global alarm_hour, alarm_minute, alarm_enabled
        if t:
            if touch_in_button(t, self.buttons[0]):   # on
                logger.debug('ON touched')
                alarm_enabled = True
                self.text_areas[0].text = '%02d:%02d' % (alarm_hour, alarm_minute)
            elif touch_in_button(t, self.buttons[1]):   # return
                logger.debug('RETURN touched')
                change_to_state('time')
            elif touch_in_button(t, self.buttons[2]): # off
                logger.debug('OFF touched')
                alarm_enabled = False
                self.text_areas[0].text = '     '
            elif alarm_enabled:
                if not self.previous_touch:
                    self.previous_touch = t
                else:
                    if touch_in_button(t, self.buttons[3]):   # HOURS
                        logger.debug('HOURS touched')
                        if t[1] < (self.previous_touch[1] - 5):   # moving up
                            alarm_hour = (alarm_hour + 1) % 24
                            logger.debug('Alarm hour now: %d', alarm_hour)
                        elif t[1] > (self.previous_touch[1] + 5): # moving down
                            alarm_hour = (alarm_hour - 1) % 24
                            logger.debug('Alarm hour now: %d', alarm_hour)
                        self.text_areas[0].text = '%02d:%02d' % (alarm_hour, alarm_minute)
                    elif touch_in_button(t, self.buttons[4]): # MINUTES
                        logger.debug('MINUTES touched')
                        if t[1] < (self.previous_touch[1] - 5):   # moving up
                            alarm_minute = (alarm_minute + 1) % 60
                            logger.debug('Alarm minute now: %d', alarm_minute)
                        elif t[1] > (self.previous_touch[1] + 5): # moving down
                            alarm_minute = (alarm_minute - 1) % 60
                            logger.debug('Alarm minute now: %d', alarm_minute)
                        self.text_areas[0].text = '%02d:%02d' % (alarm_hour, alarm_minute)
                    self.previous_touch = t
            board.DISPLAY.refresh_soon()
            board.DISPLAY.wait_for_frame()
        else:
            self.previous_touch = None
        return bool(t)

    def enter(self):
        for ta in self.text_areas:
            pyportal.splash.append(ta)
        if alarm_enabled:
            self.text_areas[0].text = '%02d:%02d' % (alarm_hour, alarm_minute) # set time textarea
        else:
            self.text_areas[0].text = '     '


####################
# State management

states = {'time': Time_State(),
          'alarm': Alarm_State(),
          'settings': Setting_State()}

current_state = None


def change_to_state(state_name):
    global current_state
    if current_state:
        logger.debug('Exiting %s', current_state.name)
        current_state.exit()
    current_state = states[state_name]
    logger.debug('Entering %s', current_state.name)
    current_state.enter()

####################
# And... go

clear_splash()
change_to_state("time")

while True:
    touched = current_state.touch(pyportal.touchscreen.touch_point, touched)
    current_state.tick(time.monotonic())
