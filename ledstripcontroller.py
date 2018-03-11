import uasyncio as asyncio
import utime

class LedStripController:

    def __init__(self, enc, button_pin, fader_pins):
        ''' enc should be an instance of Encoder.
            button_pin is expected to be an instance of machine.Pin.
            fader_pins is expected to be an iterable of machine.PWM's. 
        '''
        self.enc = enc
        self.is_on = False
        self.fader_target_val = 0
        self.button_pin = button_pin
        self.fader_pins = fader_pins
        self.button_pressed = False
        self.timings = []
        self.pwm_values = []
        self.debug_log = []

    def toggle_led_state(self):
        self.button_pressed = True
        self.log('Button pressed!')

    async def button_loop(self):

        self.button_pressed = False

        while True:
            if self.button_pressed:
                # TODO should remove debouncing; should be handled outside of this class.
                # Shouldn't care that it's a button that triggers the change...
                asyncio.sleep_ms(100) # Debounce duration
                # Only alter state if button still pressed (not a transient event)
                if not self.button_pin.value():
                    if self.is_on:
                        # Turning off, fading out
                        self.log('Turning off at {}'.format(self.enc.value))
                        self.fader_target_val = 0
                    else:
                        # Turning on, fading in
                        self.log('Turning on at {}'.format(self.enc.value))
                        self.fader_target_val = self.enc.value
                    self.button_pressed = False
                    self.is_on = not self.is_on
            await asyncio.sleep_ms(100)

    async def encoder_loop(self):

        oldval = 0

        while True:
            if self.is_on:
                self.enc.cur_accel = max(0, self.enc.cur_accel - self.enc.accel)
                if oldval != self.enc.value:
                    self.log('Old enc. val: %i, new enc. val: %i' % (oldval, self.enc.value))
                    self.fader_target_val = oldval = self.enc.value

                    self.log(','.join([str(round(j-i, 2)) for i, j in zip(self.timings[:-1], self.timings[1:])]))
                    self.log(','.join([str(pv) for pv in self.pwm_values]))

                    self.timings.clear()
                    self.pwm_values.clear()
            await asyncio.sleep_ms(50)

    async def fader_loop(self):

        FADER_MAX_STEP = 5
        FADER_DELAY_MS = 10

        fader_cur_val = 0

        while True:

            if self.fader_target_val > fader_cur_val:
                step = min(FADER_MAX_STEP, self.fader_target_val - fader_cur_val)
            elif self.fader_target_val < fader_cur_val:
                step = -min(FADER_MAX_STEP, fader_cur_val - self.fader_target_val)
            else:
                step = 0

            fader_cur_val += step
            if abs(step) > 0:
                for fader in self.fader_pins:
                    fader.duty(fader_cur_val)
                self.timings.append(utime.ticks_ms())
                self.pwm_values.append(fader_cur_val)

            await asyncio.sleep_ms(FADER_DELAY_MS)

    async def debug_log_loop(self):
        while True:
            if self.debug_log:
                for line in self.debug_log:
                    print(line)
                self.debug_log.clear()
            await asyncio.sleep_ms(500)

    def log(self, debug_string):
        self.debug_log.append(debug_string)

    def run(self):

        loop = asyncio.get_event_loop()
        loop.create_task(self.button_loop())
        loop.create_task(self.encoder_loop())
        loop.create_task(self.debug_log_loop())

        try:
            loop.run_until_complete(self.fader_loop())
        finally:
            self.enc.close()
