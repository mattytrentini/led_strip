import uasyncio as asyncio

class LedStripController:

    def __init__(self, enc, button_pin, fader_pins):
        ''' enc should be an instance of Encoder.
            button_pin is expected to be an instance of machine.Pin.
            fader_pins is expected to be an iterable of machine.PWM's. 
        '''
        self.enc = enc
        self.is_on = False
        self.enc_cur_val = 0
        self.fader_target_val = 0
        self.button_pin = button_pin
        self.fader_pins = fader_pins
        self.button_pressed = False

    def toggle_led_state(self):
        self.button_pressed = True
        print('Button pressed!')

    async def switch_loop(self, enc):

        self.button_pressed = False

        while True:
            if self.button_pressed:
                # TODO should removedebouncing; should be handled outside of this class.
                # Shouldn't care that it's a button that triggers the change...
                asyncio.sleep_ms(100) # Debounce duration
                # Only alter state if button still pressed (not a transient event)
                if not self.button_pin.value():
                    if self.is_on:
                        # Turning off, fading out
                        print('Turning off at {}'.format(self.enc_cur_val))
                        self.fader_target_val = 0
                    else:
                        # Turning on, fading in
                        print('Turning on at {}'.format(self.enc_cur_val))
                        self.fader_target_val = enc._value = self.enc_cur_val
                    self.button_pressed = False
                    self.is_on = not self.is_on
            await asyncio.sleep_ms(100)

    async def encoder_loop(self, enc):

        oldval = 0

        while True:
            if self.is_on:
                self.enc_cur_val = enc.value
                enc.cur_accel = max(0, enc.cur_accel - enc.accel)
                if oldval != self.enc_cur_val:
                    print('Old enc. val: %i, new enc. val: %i' % (oldval, self.enc_cur_val))
                    self.fader_target_val = oldval = self.enc_cur_val
            await asyncio.sleep_ms(100)

    async def fader_loop(self):

        FADER_MAX_STEP = 5
        FADER_DELAY_MS = 5

        fader_cur_val = 0

        while True:

            if self.fader_target_val > fader_cur_val:
                step = min(FADER_MAX_STEP, self.fader_target_val - fader_cur_val)
            elif self.fader_target_val < fader_cur_val:
                step = -min(FADER_MAX_STEP, fader_cur_val - self.fader_target_val)
            else:
                step = 0

            fader_cur_val += step
            for fader in self.fader_pins:
                fader.duty(fader_cur_val)

            await asyncio.sleep_ms(FADER_DELAY_MS)

    def run(self):

        loop = asyncio.get_event_loop()
        loop.create_task(self.switch_loop(self.enc))
        loop.create_task(self.encoder_loop(self.enc))

        try:
            loop.run_until_complete(self.fader_loop())
        finally:
            self.enc.close()
