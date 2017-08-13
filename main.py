import uasyncio as asyncio
from machine import Pin, PWM
from encoder import Encoder
from time import sleep_us, sleep_ms

pwm = PWM(Pin(15))
button = Pin(14, Pin.IN, Pin.PULL_UP)
pressed = False

def button_pressed(_):
    global pressed
    pressed = True

button.irq(trigger=Pin.IRQ_FALLING, handler=button_pressed)

queue = []
val = 0

async def switch_loop():
    global pressed
    global queue
    global val
    on = False
    while True:
        if pressed:
            asyncio.sleep(0.100) # Debounce duration
            if on: # Turning off, fading out
                print('Turning off at {}'.format(val))
                queue.append([val, -1])
            else: # Turning on, fading in
                #print('Turning on. val = {}, oldval = {}, enc.val = {}'.format(val, oldval, enc.value))
                queue.append([0, val+1])
                enc._value = val
            pressed = False
            on = not on
        await asyncio.sleep(0.100)

async def encoder_loop(enc):
    global queue
    global val
    oldval = 0
    val = enc.value
    while True:
        val = enc.value
        enc.cur_accel = max(0, enc.cur_accel - enc.accel)
        if oldval != val:
            print(val)
            queue.append([oldval, val])
            oldval = val
        await asyncio.sleep(0.100)

async def fader_loop():
    global queue

    async def fade(old_value, new_value):
        for value in range(old_value, new_value, 1 if new_value >= old_value else -1):
            pwm.duty(value)
            #print('pwm.duty({0})'.format(value))
            await asyncio.sleep(0.001)
            if queue:
                queue[0][0] = value
                break

    while True:
        if queue:
            old_value, new_value = queue.pop(0)
            await fade(old_value, new_value)
        await asyncio.sleep(0.100)

def main(enc):
    global pressed

    rate = 20
    oldval = 0
    on = False

    val = enc.value
    loop = asyncio.get_event_loop()
    loop.create_task(switch_loop())
    loop.create_task(encoder_loop(enc))
    #try:
    loop.run_until_complete(fader_loop())
    #except:
    #    enc.close()


enc = Encoder(pin_clk=13, pin_dt=12, pin_mode=Pin.PULL_UP,
              min_val=40, max_val=1020, clicks=1, accel=5)
enc._value = 1020
main(enc)
