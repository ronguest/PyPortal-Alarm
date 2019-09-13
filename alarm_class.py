class Alarm_State(State):
    """This state shows/sounds the alarm.
    Touching anywhere on the screen cancells the alarm.
    Pressing the snooze button turns of the alarm, starting it again in 10 minutes."""

    def __init__(self):
        super().__init__()
        self.sound_alarm_time = None
        #self.audio = audioio.AudioOut(board.SPEAKER)
        #self.sine_wave_sample = audioio.RawSample(sine_wave)

    @property
    def name(self):
        return 'alarm'

    def tick(self, now):
        global snooze_time
        #print("alarm.tick()");
        # is the snooze button pushed
        if not snooze_button.value:
            snooze_time = now
            change_to_state('time')
            return
        #return;
        # is it time to sound the alarm?
        #if self.sound_alarm_time and (now - self.sound_alarm_time) > alarm_interval:
        if True:
            #print("alarm: playing audio");
            self.sound_alarm_time = now

            #self.audio.play(sine_wave_sample, loop=True);
            if(not pyportal.audio.playing):
                logger.info("alarm: playing audio");
                pyportal._speaker_enable.value = True
                pyportal.play_file(alarm_file, False)

    def touch(self, t, touched):
        global snooze_time
        #print("alarm.touch()", t, touched);
        if t and not touched:
            #self.audio.stop();
            snooze_time = None
            change_to_state('time')
        return bool(t)

    def enter(self):
        global low_light
        #print("entered alarm state");
        self.sound_alarm_time = time.monotonic() - alarm_interval
        pyportal.set_backlight(1.00)
        pyportal.set_background(alarm_background)
        low_light = False
        board.DISPLAY.refresh_soon()
        board.DISPLAY.wait_for_frame()
        #print("alarm.enter() end of method");

    def exit(self):
        global alarm_armed, pyportal
        super().exit()
        pyportal.audio.stop()
        pyportal._speaker_enable.value = False
        alarm_armed = bool(snooze_time)