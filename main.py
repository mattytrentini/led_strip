import uasyncio as asyncio
from machine import Pin, PWM
from encoder import Encoder


class LedStripController:

    def __init__(self, enc):

        self.enc = enc
        self.is_on = False
        self.enc_cur_val = 0
        self.fader_target_val = 0

    async def switch_loop(self, enc):

        def button_handler(_):
            nonlocal button_pressed 
            button_pressed = True

        button_pressed = False

        button = Pin(14, Pin.IN, Pin.PULL_UP)
        button.irq(trigger=Pin.IRQ_FALLING, handler=button_handler)

        while True:
            if button_pressed:
                asyncio.sleep(0.100) # Debounce duration
                if self.is_on:
                    # Turning off, fading out
                    print('Turning off at {}'.format(self.enc_cur_val))
                    self.fader_target_val = 0
                else:
                    # Turning on, fading in
                    #print('Turning on. self.enc_cur_val = {}, oldval = {}, enc.val = {}'.format(self.enc_cur_val, oldval, enc.value))
                    self.fader_target_val = enc._value = self.enc_cur_val
                button_pressed = False
                self.is_on = not self.is_on
            await asyncio.sleep(0.100)

    async def encoder_loop(self, enc):

        oldval = 0

        while True:
            if self.is_on:
                self.enc_cur_val = enc.value
                enc.cur_accel = max(0, enc.cur_accel - enc.accel)
                if oldval != self.enc_cur_val:
                    #print(self.enc_cur_val)
                    self.fader_target_val = oldval = self.enc_cur_val
            await asyncio.sleep(0.100)

    async def fader_loop(self):

        FADER_MAX_STEP = 5
        FADER_DELAY = 0.005

        fader = PWM(Pin(15))
        fader_cur_val = 0

        while True:

            if self.fader_target_val > fader_cur_val:
                step = min(FADER_MAX_STEP, self.fader_target_val - fader_cur_val)
            elif self.fader_target_val < fader_cur_val:
                step = -min(FADER_MAX_STEP, fader_cur_val - self.fader_target_val)
            else:
                step = 0

            fader_cur_val += step
            fader.duty(fader_cur_val)

            await asyncio.sleep(FADER_DELAY)

    def run(self):

        loop = asyncio.get_event_loop()
        loop.create_task(self.switch_loop(self.enc))
        loop.create_task(self.encoder_loop(self.enc))

        try:
            loop.run_until_complete(self.fader_loop())
        finally:
            self.enc.close()


def main():

    enc = Encoder(pin_clk=13, pin_dt=12, pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 1020

    controller = LedStripController(enc)
    controller.run()


if __name__ == '__main__':
    main()
