from machine import Pin, PWM, Timer
from encoder import Encoder
from ledstripcontroller import LedStripController
import uasyncio as asyncio
from sys import platform

# Declarations
debounce_check = False
controller = None
countdown_timer = Timer(-1)
BUTTON_PIN = None
PIR_PIN = None

def get_pin_num(pin):
    return int(str(pin).split('(')[1].split(')')[0])

def irq_handler(pin):
    global controller, BUTTON_PIN, PIR_PIN
    pin_num = get_pin_num(pin)
    if pin_num == BUTTON_PIN:
        global debounce_check
        if not debounce_check:
            debounce_check = True
            asyncio.sleep_ms(100) # Debounce duration
            # Only alter state if button still pressed (not a transient event)
            if not pin.value():
                controller.toggle_led_state()
            debounce_check = False
    elif pin_num == PIR_PIN:
        global countdown_timer
        if pin.value():
            countdown_timer.deinit()
            print("Motion detected!")
            controller.led_state_on()
        else:
            print("Motion ceased...")
            countdown_timer.init(period=300000, mode=Timer.ONE_SHOT, callback=controller.led_state_off)


def main():
    global BUTTON_PIN, PIR_PIN
    dev_type = platform
    if dev_type == 'esp8266': # WEMOS D1 Mini (or similar)
        ENC_PINS = {'clk':4, 'dt':5}
        FADER_PINS = (12, 13, 14)
        FADER_FREQ = 1000
        BUTTON_PIN = 2
        PIR_PIN = 0
    elif dev_type == 'esp32': # TTGO
        ENC_PINS = {'clk':21, 'dt':22}
        FADER_PINS = (19, 23, 18)
        FADER_FREQ = 50000
        BUTTON_PIN = 16
        PIR_PIN = 17
    else: # Defaults
        ENC_PINS = {'clk':None, 'dt':None, 'button':None}
        FADER_PINS = (None, None, None)
        FADER_FREQ = None
        BUTTON_PIN = None
        PIR_PIN = None
    
    enc = Encoder(pin_clk=ENC_PINS['clk'], pin_dt=ENC_PINS['dt'], pin_mode=Pin.PULL_UP,
                  min_val=40, max_val=1020, clicks=1, accel=5)
    enc._value = 0

    fader_pins = [PWM(Pin(pin_num), freq=FADER_FREQ, duty=0) for pin_num in FADER_PINS]
    controller = LedStripController(enc, fader_pins=fader_pins)
    
    button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
    button.irq(trigger=Pin.IRQ_FALLING, handler=irq_handler)
    
    pir = Pin(PIR_PIN, Pin.IN)
    pir.irq(trigger=(Pin.IRQ_FALLING | Pin.IRQ_RISING), handler=irq_handler)

    loop = asyncio.get_event_loop()
    loop.create_task(controller.switch_loop(controller.enc))
    loop.create_task(controller.encoder_loop(controller.enc))
    loop.create_task(controller.fader_loop())
    loop.run_forever()
    controller.enc.close()

if __name__ == '__main__':
    main()
