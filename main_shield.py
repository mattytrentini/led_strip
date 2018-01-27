from ledstripcontroller import LedStripController
from machine import Pin
from encoder import Encoder

def main():

    enc = Encoder(pin_clk=4, pin_dt=5, pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 1020

    controller = LedStripController(enc, button_pin = 2, fader_pins = (13, 12, 14))
    controller.run()


if __name__ == '__main__':
    main()
