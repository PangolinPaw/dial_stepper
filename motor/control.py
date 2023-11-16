import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from RPi import GPIO

# Initialise GPIO & motor controllers
GPIO.setmode(GPIO.BCM)
kit = MotorKit() # Lower controller (motors A & B)
kit2 = MotorKit(address=0x61) # Upper controller (motor C)

# Motor positions for use in other scripts
MOTORS = {
    'a':{
        'position':0,
        'motor':kit.stepper1
    },
    'b':{
        'position':0,
        'motor':kit.stepper2
    },
    'c':{
        'position':0,
        'motor':kit2.stepper1
    }
}

# Ratio between dial steps & motor steps
RATIO = 20

# Level of 'smoothing' applied to dial input
SMOOTHING = 16

def dial_smooting(dial, signal):
    '''Dial can 'wobble' between clockwise & anticlockwise so this function smoothes
    the changes before they're used as signals for motor movement'''
    dial['buffer'].append(signal)
    
    if len(dial['buffer']) > SMOOTHING:
        del dial['buffer'][0]
        return sum(dial['buffer'])
    else:
        return 0

def initialise():
    '''Set up GPIO pins and initial positions for dials'''
    dials = {
        'a':{
            'clk':20,
            'dt':21,
            'position':0,
            'buffer':[],
            'clk_last_state':False,
            'motor':kit.stepper1
        },
        'b':{
            'clk':19,
            'dt':26,
            'position':0,
            'buffer':[],
            'clk_last_state':False,
            'motor':kit.stepper2
        },
        'c':{
            'clk':6,
            'dt':5,
            'position':0,
            'buffer':[],
            'clk_last_state':False,
            'motor':kit2.stepper1
        }
    }
    for dial in dials:
        GPIO.setup(dials[dial]['clk'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dials[dial]['dt'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        dials[dial]['clk_last_state'] = GPIO.input(dials[dial]['clk'])
    return dials

def move_motor(motor_name, motor, direction):
    global MOTORS
    change = 0
    for x in range(RATIO):
        motor.onestep(
            direction=direction
        )
        change += 1
    new_position = MOTORS[motor_name]['position'] + change
    MOTORS[motor_name]['position'] = new_position % 200

def read_dials():
    '''Receive signals from rotary encoders & determine rotation direction
    & distance'''
    dials = initialise()
    counter = 0

    while True:
        counter += 1

        if counter == 25:
            dial_smooting(dials['a'], 0)
            dial_smooting(dials['b'], 0)
            dial_smooting(dials['c'], 0)
            counter = 0
        
        for dial in dials:
            clk_state = GPIO.input(dials[dial]['clk'])
            dt_state = GPIO.input(dials[dial]['dt'])
            change = 0
            if clk_state != dials[dial]['clk_last_state']:
                if dt_state != clk_state:
                    change = dial_smooting(dials[dial], 1)
                    for x in range(change):
                        move_motor(
                            dial,
                            dials[dial]['motor'],
                            stepper.FORWARD
                        )
                else:
                    change = dial_smooting(dials[dial], -1)
                    for x in range(change):
                        move_motor(
                            dial,
                            dials[dial]['motor'],
                            stepper.BACKWARD
                        )
                
                print(f"[ {dial.upper()} ] : dial ={str(dials[dial]['position']).rjust(3)}\t motor ={str(MOTORS[dial]['position']).rjust(3)}")
            dials[dial]['clk_last_state'] = clk_state

            dials[dial]['position'] = (dials[dial]['position'] + change) % 24
        time.sleep(0.01)

def set_motor(motor_name, position):
    '''Intended for demo mode, move motor to specified position'''
    global MOTORS
    while position != MOTORS[motor_name]['position']:
        if position > MOTORS[motor_name]['position']:
            MOTORS[motor_name]['motor'].onestep(direction=stepper.FORWARD)
            MOTORS[motor_name]['position'] += 1
        else:
            MOTORS[motor_name]['motor'].onestep(direction=stepper.BACKWARD)
            MOTORS[motor_name]['position'] -= 1
        time.sleep(0.01)

if __name__ == '__main__':
    read_dials()

