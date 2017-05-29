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
    last_set_to = val
    try:
        while True:
            if not on and pressed:
                
                enc._value = last_set_to
                print('Turning on. last_set_to = {}, val = {}, oldval = {}, enc.val = {}'.format(last_set_to, val, oldval, enc.value))
                
                # Could debounce here. Wait here for x milliseconds. Check button again.
                fade(start=0, end=last_set_to+1)
                sleep_ms(100)
                pressed = False
                on = True
            elif on and pressed:
                print('Turning off at {}'.format(val))
                last_set_to = val
                #enc._value = oldval
                fade(start=val, end=-1, step=-1)
                sleep_ms(100)
                pressed = False
                on = False

            if on and not pressed:
                val = enc.value
                if oldval != val:
                    print(val)
                    pwm.duty(val)
                    oldval = val

                enc.cur_accel = max(0, enc.cur_accel - enc.accel)
            sleep_ms(1000 // rate)
    except:
        enc.close()

enc = Encoder(pin_clk=13, pin_dt=12, pin_mode=Pin.PULL_UP,
              min_val=1, max_val=1020, clicks=1, accel=5)
enc._value = 1020
main(enc)
