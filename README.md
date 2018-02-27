# LED strip controller
Control an LED strip using an ESP8266, PWM, an N-Channel MOSFET, a rotary encoder and some Micropython

Uses SpotlightKid's [Rotary Encoder Library](https://github.com/SpotlightKid/micropython-stm-lib/tree/master/encoder). 
Just copy `encoder.py`, `ledstripcontroller.py`, and either `main.py` or `main_shield.py` (will need to be renamed to `main.py` once copied) to the ESP8266; tweak if your hardware is different!