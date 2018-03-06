serialport = COM4

deploy: 
	 python -m mp.mpfshell -n -c "open $(serialport); put ledstripcontroller.py; put main.py; lcd micropython-stm-lib/encoder; put Encoder.py;ls"