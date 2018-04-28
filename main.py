from machine import Pin, PWM
from encoder import Encoder
from ledstripcontroller import LedStripController
from uasyncio import get_event_loop
from sys import platform

def main():
    dev_type = platform
    if dev_type == 'esp8266': # WEMOS D1 Mini (or similar)
        ENC_PINS = {'clk':4, 'dt':5, 'button':2}
        FADER_PINS = (12, 13, 14)
        FADER_FREQ = 1000
    elif dev_type == 'esp32': # TTGO
        ENC_PINS = {'clk':21, 'dt':22, 'button':16}
        FADER_PINS = (19, 23, 18)
        FADER_FREQ = 50000
    else: # Defaults
        ENC_PINS = {'clk':None, 'dt':None, 'button':None}
        FADER_PINS = (None, None, None)
        FADER_FREQ = None
    
    enc = Encoder(pin_clk=ENC_PINS['clk'], pin_dt=ENC_PINS['dt'], pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 0

    fader_pins = [PWM(Pin(pin_num), freq=FADER_FREQ) for pin_num in FADER_PINS]
    button = Pin(ENC_PINS['button'], Pin.IN, Pin.PULL_UP)
    controller = LedStripController(enc, button_pin=button, fader_pins=fader_pins)
    button.irq(trigger=Pin.IRQ_FALLING, handler=lambda _: controller.toggle_led_state())

    loop = get_event_loop()
    loop.create_task(controller.switch_loop(controller.enc))
    loop.create_task(controller.encoder_loop(controller.enc))
    loop.create_task(controller.fader_loop())
    loop.run_forever()
    controller.enc.close()

if __name__ == '__main__':
    main()
