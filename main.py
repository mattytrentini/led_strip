from machine import Pin, PWM
from encoder import Encoder
from ledstripcontroller import LedStripController

def main():

    enc = Encoder(pin_clk=4, pin_dt=5, pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 1020

    fader_pins = [PWM(Pin(pin_num)) for pin_num in (12, 13, 14)]
    button = Pin(2, Pin.IN, Pin.PULL_UP)
    controller = LedStripController(enc, button_pin=button, fader_pins=fader_pins)
    button.irq(trigger=Pin.IRQ_FALLING, handler=lambda _: controller.toggle_led_state())

    controller.run()


if __name__ == '__main__':
    main()
