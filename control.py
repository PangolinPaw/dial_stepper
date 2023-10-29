import os
import time
import threading
from RPi import GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # CLK
GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # DT

DIAL_POSITION = 0
MOTOR_POSITION = 0

def convert(dial):
    motor = dial * 8
    return motor

def dial():
    global DIAL_POSITION
    while True:
        os.system('cls')
        print()
        print(f' DIAL_POSITION:  {str(DIAL_POSITION).rjust(3)}')
        print(f' MOTOR_POSITION: {str(MOTOR_POSITION).rjust(3)}')
        
        clkLastState = GPIO.input(clk)
        while True:
            clkState = GPIO.input(clk)
            dtState = GPIO.input(dt)
            if clkState != clkLastState:
                if dtState != clkState:
                    DIAL_POSITION += 1
                    if DIAL_POSITION > 23:
                        DIAL_POSITION = 0
                else:
                    DIAL_POSITION -= 1
                    if DIAL_POSITION < 0:
                        DIAL_POSITION = 23
            clkLastState = clkState
            sleep(0.01)
    

def motor(interrupt):
    global MOTOR_POSITION
    while True:
        if MOTOR_POSITION < convert(DIAL_POSITION):
            MOTOR_POSITION += 1
        elif MOTOR_POSITION > convert(DIAL_POSITION):
            MOTOR_POSITION -=1
        if interrupt.is_set():
            break
        else:
            time.sleep(1)

def main():
    interrupt = threading.Event()
    motor_thread = threading.Thread(
        target=motor,
        args=(interrupt,)
    )
    motor_thread.start()
    try:
        dial()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
