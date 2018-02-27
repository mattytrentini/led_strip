from machine import Pin, PWM
from encoder import Encoder
from ledstripcontroller import LedStripController

def main():

    enc = Encoder(pin_clk=4, pin_dt=5, pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 1020

    controller = LedStripController(enc, button_pin=2, fader_pins=(12, 13, 14))
    controller.run()


if __name__ == '__main__':
    main()
