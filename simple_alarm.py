"""
Reads an alarm time from a URL
Plays a music file at the alarm time, touching screen halts the alarm
No alarms on weekends
"""
import time
import board
from adafruit_pyportal import PyPortal
from adafruit_bitmap_font import bitmap_font
from adafruit_display_text.Label import Label

days_str = ("Mon.", "Tues.", "Wed.", "Thurs.", "Fri.", "Sat.", "Sun.")

alarm_time = "9999"
ALARM_URL = 'http://10.0.1.38/ashley_alarm.txt'
# determine the current working directory
# needed so we know where to find files
cwd = ("/"+__file__).rsplit('/', 1)[0]

# initialize the pyportal object and let us know what data to fetch and where
# to display it
pyportal = PyPortal(url=ALARM_URL, status_neopixel=board.NEOPIXEL,
                    default_bg=0x000000)

backlight_off = 0
backlight_on = 0.8
pyportal.set_backlight(backlight_on)

# assign fonts
big_font = bitmap_font.load_font(cwd+"/fonts/Nunito-Light-75.bdf")
big_font.load_glyphs(b'0123456789:AP') # pre-load glyphs for fast printing
print('loading fonts...')
info_font = bitmap_font.load_font(cwd+"/fonts/Nunito-Black-17.bdf")
info_font.load_glyphs(b'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-,.:/ ')

time_color = 0xFFFFFF
time_position = (30,80)
time_textarea = Label(big_font, max_glyphs=15, color=time_color,
                      x=time_position[0], y=time_position[1])

wakeup_time_color = 0xFFFFFF
wakeup_time_position = (15,200)
wakeup_time_textarea = Label(info_font, max_glyphs=30, color=wakeup_time_color,
                             x=wakeup_time_position[0], y=wakeup_time_position[1])

pyportal.splash.append(time_textarea)
pyportal.splash.append(wakeup_time_textarea)

while True:
    try:
        print("Getting time from internet!")
        pyportal.get_local_time()
    except RuntimeError as e:
        print("Some error occured, retrying! -", e)
        continue
    break

# parse given time string into hour minute and AM_PM elements
def parseTime(time_before):
    hours_before, minutes_before = time_before.split(":")
    AM_PM_str = minutes_before[-1:]
    minutes_before = int(minutes_before[:-1])
    if (hours_before != '12') and AM_PM_str == 'pm':
        hours_before = int(hours_before) + 12
    elif ((hours_before == '12') and (AM_PM_str == 'pm')):
        hours_before = int(hours_before)
    elif ((hours_before == '12') and (AM_PM_str == 'am')):
        hours_before = 0
    else:
        hours_before = int(hours_before)
    parsed_time = [hours_before, minutes_before]
    return parsed_time

def displayTime():
    now = time.localtime()
    hour, minute = now[3:5]
    #print(now)
    #print("Current time: %02d:%02d" % (hour, minute))
    formatTime(hour, minute)
    time_textarea.text = formatTime(hour, minute)
    return formatTime(hour, minute)

def formatTime(raw_hours, raw_minutes):
    # display the time in a nice big font
    format_str = "%d:%02d"
    if raw_hours >= 12:
        raw_hours -= 12
        format_str = format_str+"pm"
    else:
        format_str = format_str+"am"
    if raw_hours == 0:
        raw_hours = 12
    time_str = format_str % (raw_hours, raw_minutes)
    return time_str

def backLight():
    now = time.localtime()
    now_val = time.mktime((now[0], now[1], now[2], now[3], now[4], now[5], now[6], now[7], now[8]))
    # if time is more than 9 hours after current day's wake up time,
    # or time is before light start time, backlight off, tap to turn on
    if (now_val - alarm_time) > 32400 or (now_val - alarm_time) < -1800:
        pyportal.set_backlight(backlight_off)
        if pyportal.touchscreen.touch_point:
            pyportal.set_backlight(backlight_on)
            time.sleep(5)
            pyportal.set_backlight(backlight_off)
    else:
        pyportal.set_backlight(backlight_on)

refresh_time = None

while True:
    time_now = time.localtime()
    # only query the online time once per hour (and on first run)
    if (not refresh_time) or (time.monotonic() - refresh_time) > 3600:
        try:
            print("Getting alarm time: ")
            alarm_time = pyportal.fetch()
            #alarm_time = value[4:]
            print(alarm_time)
            print("Getting time from internet!")
            pyportal.get_local_time()
            refresh_time = time.monotonic()
        except RuntimeError as e:
            print("Some error occured, retrying! -", e)
            continue
    time_str_text = displayTime()
    print(time_str_text)
    input_wake_up_time_text = "Wake up at " + alarm_time
    wakeup_time_textarea.text = input_wake_up_time_text
    print(wakeup_time_textarea.text)
    # determine which wake up time to choose based on the day
    #wake_up_day = whichDay()
    # if time is more than 9 hours after previous day's wake up time,
    # backlight off and can tap to turn on
    #backLight()
    # If current day is same as wake up day and
    # wake up time - 30 minutes equals current time, start the light
    if alarm_time == time_now[6]:
        print("Starting wake up light")
        # turn on backlight
        pyportal.set_backlight(backlight_on)
        for i in range(light_minutes - 1):
            BRIGHTNESS = BRIGHTNESS + (MAX_BRIGHTNESS/light_minutes) # max 0.25, min 0.0
            displayTime()
            time.sleep(60) # 60 for once per min
        while not pyportal.touchscreen.touch_point: # turn strip off
            displayTime()
            time.sleep(1)
            continue
    # update every second so that screen can be tapped to view time
    time.sleep(1)
