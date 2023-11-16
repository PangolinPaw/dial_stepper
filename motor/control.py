import time
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
from RPi import GPIO

# Initialise GPIO & motor controllers
GPIO.setmode(GPIO.BCM)
kit = MotorKit()  # Lower controller (motors A & B)
kit2 = MotorKit(address=0x61)  # Upper controller (motor C)

# Motor positions for use in other scripts
MOTORS = {
    'a': {'position': 0, 'motor': kit.stepper1},
    'b': {'position': 0, 'motor': kit.stepper2},
    'c': {'position': 0, 'motor': kit2.stepper1}
}

# Ratio between dial steps & motor steps
RATIO = 8

# Level of 'smoothing' applied to dial input
SMOOTHING = 8
DEBOUNCE_TIME = 0.01  # Debounce time in seconds

def dial_smoothing(dial, signal):
    dial['buffer'].append(signal)
    if len(dial['buffer']) > SMOOTHING:
        del dial['buffer'][0]
        buffer_sum = sum(dial['buffer'])
        if buffer_sum > SMOOTHING / 2:
            return 1
        elif buffer_sum < -SMOOTHING / 2:
            return -1
    return 0

def initialise():
    dials = {
        'a': {'clk': 20, 'dt': 21, 'position': 0, 'buffer': [], 'clk_last_state': False, 'motor': kit.stepper1},
        'b': {'clk': 19, 'dt': 26, 'position': 0, 'buffer': [], 'clk_last_state': False, 'motor': kit.stepper2},
        'c': {'clk': 6, 'dt': 5, 'position': 0, 'buffer': [], 'clk_last_state': False, 'motor': kit2.stepper1}
    }
    for dial in dials:
        GPIO.setup(dials[dial]['clk'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(dials[dial]['dt'], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        dials[dial]['clk_last_state'] = GPIO.input(dials[dial]['clk'])
    return dials

def move_motor(motor_name, motor, direction, steps):
    global MOTORS
    for _ in range(steps):
        motor.onestep(direction=direction)
    MOTORS[motor_name]['position'] = (MOTORS[motor_name]['position'] + (1 if direction == stepper.FORWARD else -1) * steps) % 200

def read_dials():
    dials = initialise()
    last_dial_check_time = time.time()

    while True:
        for dial in dials:
            if time.time() - last_dial_check_time < DEBOUNCE_TIME:
                continue

            clk_state = GPIO.input(dials[dial]['clk'])
            if clk_state != dials[dial]['clk_last_state']:
                dt_state = GPIO.input(dials[dial]['dt'])
                change = dial_smoothing(dials[dial], 1 if dt_state != clk_state else -1)
                if change != 0:
                    move_motor(dial, dials[dial]['motor'], stepper.FORWARD if change > 0 else stepper.BACKWARD, abs(change))
                    print(f"[ {dial.upper()} ] : dial = {str(dials[dial]['position']).rjust(3)}\t motor = {str(MOTORS[dial]['position']).rjust(3)}")
                last_dial_check_time = time.time()

            dials[dial]['clk_last_state'] = clk_state
            dials[dial]['position'] = (dials[dial]['position'] + change) % 24
        time.sleep(0.01)

if __name__ == '__main__':
    read_dials()
