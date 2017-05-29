from machine import Pin, PWM
from encoder import Encoder
from time import sleep_ms

pwm = PWM(Pin(4))
button = Pin(14, Pin.IN, Pin.PULL_UP)
pressed = False

def button_pressed(p):
    global pressed
    pressed = True

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

def fade(start=0, end=1000, step=1, sleep=1):
    ''' Adjust the duty of the PWM signal to generate a fade-in or out. '''
    for i in range(start, end, step):
        pwm.duty(i)
        sleep_ms(sleep)

def fio():
    ''' Helper function: Fade in then out '''
    fade()
    fade(999,-1,-1)

def main(enc):
    global pressed

    rate = 20
    oldval = 0
    on = False

    val = enc.value
    try:
        while True:
            if on and not pressed: # On, normal state
                val = enc.value
                enc.cur_accel = max(0, enc.cur_accel - enc.accel)
                if oldval != val:
                    print(val)
                    pwm.duty(val)
                    oldval = val

            if pressed:
                sleep_ms(100) # Debounce duration
                if on: # Turning off, fading out
                    print('Turning off at {}'.format(val))
                    fade(start=val, end=-1, step=-1)
                else: # Turning on, fading in
                    print('Turning on. val = {}, oldval = {}, enc.val = {}'.format(val, oldval, enc.value))
                    fade(start=0, end=val+1)
                    enc._value = val
                pressed = False
                on = not on

            sleep_ms(1000 // rate)
    except:
        enc.close()

enc = Encoder(pin_clk=13, pin_dt=12, pin_mode=Pin.PULL_UP,
              min_val=40, max_val=1020, clicks=1, accel=5)
enc._value = 1020
main(enc)
