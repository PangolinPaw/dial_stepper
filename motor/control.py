import os
import time
import threading
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
from RPi import GPIO

# Initialise GPIO & motor controllers
GPIO.setmode(GPIO.BCM)
kit = MotorKit() # Lower controller (motors A & B)
kit2 = MotorKit(address=0x61) # Upper controller (motor C)

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
        'clk':21,
        'dt':20,
        'position':0
    },
    'b':{
        'clk':19,
        'dt':26,
        'position':0
    },
    'c':{
        'clk':6,
        'dt':5,
        'position':0
    }
}

# Set up dial GPIO pins
for dial in DIALS:
    GPIO.setup(DIALS[dial]['clk'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(DIALS[dial]['dt'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Buffer used to smooth dial positions from noisy inputs
DIAL_BUFFER = {
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
        del DIAL_BUFFER[dial][0]
        if sum(DIAL_BUFFER[dial]) > 1:
            return 1
        elif sum(DIAL_BUFFER[dial]) < 1:
            return -1
        else:
            return 0
    else:
        return 0

def read_dials():
    '''Receive signals from rotary encoders & determine rotation direction
    & distance'''
    global DIALS

    DIALS['a']['position'] = 50


    """
    clk_last_state = {}
    for dial in DIALS:
        clk_last_state[dial] = GPIO.input(DIALS[dial]['clk'])

    while True:
        for dial in DIALS:
            clk_state = GPIO.input(DIALS[dial]['clk'])
            dt_state = GPIO.input(DIALS[dial]['dt'])
            change = 0
            if clk_state != clk_last_state[dial]:
                if dt_state != clk_state:
                    change = dial_smooting(dial, 1)
                else:
                    change = dial_smooting(dial, -1)
            clk_last_state[dial] = clk_state

            DIALS[dial]['position'] += change
    """
    time.sleep(0.01)

def move_motors():
    '''Monitor values of DIAL positions and turn motors to match. Runs in a
    separate thread to the input functions to avoid blocking while rotation in progress'''
    global MOTORS
    while True:
        os.system('clear')
        print()
        print(f'    | DIAL | MOTOR |')
        print(f' ---|------|-------|')
        for motor in MOTORS:
            print(f'  {motor.upper()} |   {str(DIALS[motor]["position"]).rjust(2)} |   {str(MOTORS[motor]["position"]).rjust(3)} |')
            if MOTORS[motor]['position'] < convert(DIALS[motor]['position']):
                MOTORS[motor]['position'] += 1
                if motor == 'a':
                    kit.stepper1.onestep(
                        direction=stepper.FORWARD
                    )
                elif motor == 'b':
                    kit.stepper2.onestep(
                        direction=stepper.FORWARD
                    )
                elif motor == 'c':
                    kit2.stepper1.onestep(
                        direction=stepper.FORWARD
                    )

            elif MOTORS[motor]['position'] > convert(DIALS[motor]['position']):
                MOTORS[motor]['position'] -=1
                if motor == 'a':
                    kit.stepper1.onestep(
                        direction=stepper.BACKWARD
                    )
                elif motor == 'b':
                    kit.stepper2.onestep(
                        direction=stepper.BACKWARD
                    )
                elif motor == 'c':
                    kit2.stepper1.onestep(
                        direction=stepper.BACKWARD
                    )

def test_sequence():
    while True:
        for x in range(200):
            kit.stepper1.onestep(
                direction=stepper.FORWARD
            )
        for x in range(200):
            kit.stepper2.onestep(
                direction=stepper.FORWARD
            )
        for x in range(200):
            kit2.stepper1.onestep(
                direction=stepper.FORWARD
            )
        time.sleep(1)
        for x in range(200):
            kit.stepper1.onestep(
                direction=stepper.BACKWARD
            )
        for x in range(200):
            kit.stepper2.onestep(
                direction=stepper.BACKWARD
            )
        for x in range(200):
            kit2.stepper1.onestep(
                direction=stepper.BACKWARD
            )
        time.sleep(1)

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
#    test_sequence()
