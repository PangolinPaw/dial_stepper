import os
import time
import threading
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
from RPi import GPIO

# Initialise GPIO & motor controllers
GPIO.setmode(GPIO.BCM)
kit = MotorKit(i2c=board.I2C())
# TODO: Add 2nd motor controller to allow 3rd motor

# Dial A, first from left
dt_A = 18
clk_A = 17
GPIO.setup(clk_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk_A
GPIO.setup(dt_A, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt_A

# Dial B, 2nd from left
dt_B = 23
clk_B = 22
GPIO.setup(clk_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk_B
GPIO.setup(dt_B, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt_B

# Dial C, 3rd from left
dt_C = 25
clk_C = 24
GPIO.setup(clk_C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # clk_C
GPIO.setup(dt_C, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # dt_C

# Current dial & motor positions (in steps)
DIAL_A = 0
DIAL_B = 0
DIAL_C = 0
MOTOR_A = 0
MOTOR_B = 0
MOTOR_C = 0

# Buffer used to smooth dial positions from noisy inputs
DIAL_BUFFER {
    'a':[],
    'b':[],
    'c':[]
}

def convert(dial):
    '''Dial Step to Motor Step conversion. Dials have 24 and motors have 200
    steps in a full 360` rotation'''
    motor = dial * 8
    return motor

def dial_smooting(dial, signal):
    '''Dial can 'wobble' between clockwise & anticlockwise so this function smoothes
    the changes before they're used as signals for motor movement'''
    global DIAL_BUFFER
    DIAL_BUFFER[dial].append(signal)
    if len(DIAL_BUFFER[dial]) > 3:
        del DIAL_BUFFER[dial]
        if sum(DIAL_BUFFER[dial]) > 1:
            return 1
        elif sum(DIAL_BUFFER[dial]) < 1:
            return -1
        else:
            return 0

def dial():
    '''Receive signals from rotary encoders & determine rotation direction
    & distance'''
    global DIAL_A, DIAL_B, DIAL_C
    clk_A_last_state = GPIO.input(clk_A)
    clk_B_last_state = GPIO.input(clk_B)
    while True:
        clk_A_state = GPIO.input(clk_A)
        dt_A_state = GPIO.input(dt_A)
        if clk_A_state != clk_A_last_state:
            if dt_A_state != clk_A_state:
                change = dial_smooting('a', 1)
            else:
                change = dial_smooting('a', -1)
            clk_A_last_state = clk_A_state
        DIAL_A += change
        if DIAL_A > 23:
            DIAL_A = 0
        elif DIAL_A < 0:
            DIAL_A = 23

        clk_B_state = GPIO.input(clk_B)
        dt_B_state = GPIO.input(dt_B)
        if clk_B_state != clk_B_last_state:
            if dt_B_state != clk_B_state:
                change = dial_smooting('b', 1)
            else:
                change = dial_smooting('b', -1)
            clk_B_last_state = clk_B_state
        DIAL_B += change
        if DIAL_B > 23:
            DIAL_B = 0
        elif DIAL_B < 0:
            DIAL_B = 23

        clk_C_state = GPIO.input(clk_C)
        dt_C_state = GPIO.input(dt_C)
        if clk_C_state != clk_C_last_state:
            if dt_C_state != clk_C_state:
                change = dial_smooting('c', 1)
            else:
                change = dial_smooting('c', -1)
            clk_C_last_state = clk_C_state
        DIAL_C += change
        if DIAL_C > 23:
            DIAL_C = 0
        elif DIAL_C < 0:
            DIAL_C = 23

        time.sleep(0.01)

def motor(interrupt):
    '''Monitor values of DIAL_* variables and turn motors to match. Runs in a
    separate thread to the input functions to avoid blocking while rotation in progress'''
    global MOTOR_A, MOTOR_B
    # TODO: Add 3rd motor
    while True:
        os.system('clear')
        print()
        print(f' DIAL_A:  {str(DIAL_A).rjust(3)}')
        print(f' MOTOR_A: {str(MOTOR_A).rjust(3)}')
        print(f' DIAL_B:  {str(DIAL_B).rjust(3)}')
        print(f' MOTOR_B: {str(MOTOR_B).rjust(3)}')

        if MOTOR_A < convert(DIAL_A):
            MOTOR_A += 1
            kit.stepper1.onestep(
                direction=stepper.FORWARD
            )
        elif MOTOR_A > convert(DIAL_A):
            MOTOR_A -=1
            kit.stepper1.onestep(
                direction=stepper.BACKWARD
            )
        if MOTOR_B < convert(DIAL_B):
            MOTOR_B += 1
        elif MOTOR_B > convert(DIAL_B):
            MOTOR_B -=1

        if interrupt.is_set():
            break

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
