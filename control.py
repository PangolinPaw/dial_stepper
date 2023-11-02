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

# Motor initial positions
MOTORS = {
    'a':{
        'position':0
    },
    'b':{
        'position':0
    },
    'c':{
        'position':0
    }
}

# Dial pins & initial positions
DIALS = {
    'a':{
        'clk':17
        'dt':18,
        'position':0
    },
    'b':{
        'clk':17
        'dt':18,
        'position':0
    },
    'c':{
        'clk':17
        'dt':18,
        'position':0
    }
}

# Set up dial GPIO pins
for dial in DIALS:
    GPIO.setup(DIALS['clk'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DIALS['dt'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

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

def read_dials():
    '''Receive signals from rotary encoders & determine rotation direction
    & distance'''
    global DIALS
    for dial in DIALS:
        clk_last_state = GPIO.input(DIALS[dial]['clk'])

    while True:
        for dial in DIALS:
            clk_state = GPIO.input(DIALS[dial]['clk'])
            dt_state = GPIO.input(DIALS[dial]['dt'])
            if clk_state != clk_last_state:
                if dt_state != clk_state:
                    change = dial_smooting('a', 1)
                else:
                    change = dial_smooting('a', -1)
            clk_last_state = clk_state

        DIALS[dial]['position'] += change
        if DIALS[dial]['position'] > 23:
            DIALS[dial]['position'] = 0
        elif DIALS[dial]['position'] < 0:
            DIALS[dial]['position'] = 23

        time.sleep(0.01)

def move_motors(interrupt):
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

def move_motors(interrupt):
    '''Monitor values of DIAL positions and turn motors to match. Runs in a
    separate thread to the input functions to avoid blocking while rotation in progress'''
    global MOTORS
    while True:
        os.system('clear')
        print()
        print(f'    | DIAL | MOTOR |')
        print(f' ---|------|-------|')
        for motor in MOTORS:
            print(f'  {motor.upper()} |   {str(DIALS[motor]).rjust(2)} |    {str(MOTORS[motor]).rjust(3)} |')
            if MOTORS[motor]['position'] < convert(DIALS[motor]['position']):
                MOTORS[motor]['position'] += 1
                if motor == 'a':
                    kit.stepper1.onestep(
                        direction=stepper.FORWARD
                    )
                elif motor == 'b':
                    kit.stepper1.onestep(
                        direction=stepper.BACKWARD
                    )
                elif motor == 'c':
                    #TODO: 3rd motor via 2nd motor controller
                    pass

            elif MOTORS[motor]['position'] > convert(DIALS[motor]['position']):
                MOTORS[motor]['position'] -=1
                if motor == 'a':
                    kit.stepper2.onestep(
                        direction=stepper.BACKWARD
                    )
                elif motor == 'b':
                    kit.stepper2.onestep(
                        direction=stepper.BACKWARD
                    )
                elif motor == 'c':
                    #TODO: 3rd motor via 2nd motor controller
                    pass

        if interrupt.is_set():
            break

def main():
    interrupt = threading.Event()
    motor_thread = threading.Thread(
        target=move_motors,
        args=(interrupt,)
    )
    motor_thread.start()
    try:
        read_dials()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
