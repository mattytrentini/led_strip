from machine import Pin, PWM
from encoder import Encoder
from ledstripcontroller import LedStripController
from uasyncio import get_event_loop

def main():
    enc = Encoder(pin_clk=21, pin_dt=22, pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 1020

    fader_pins = [PWM(Pin(pin_num), freq=50000) for pin_num in (19,23,18)]
    button = Pin(16, Pin.IN, Pin.PULL_UP)
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
