import os
import time
import threading
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
from RPi import GPIO

kit = MotorKit(i2c=board.I2C())
GPIO.setmode(GPIO.BCM)

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

MOTOR_A = 0
MOTOR_B = 0

RATIO = 8 # x steps of motor for 1 step of dial

def dial():
    global MOTOR_A, MOTOR_B
    clk_A_last_state = GPIO.input(clk_A)
    clk_B_last_state = GPIO.input(clk_B)
    while True:
        print(f' {MOTOR_A = }, {MOTOR_B = }')
        clk_A_state = GPIO.input(clk_A)
        dt_A_state = GPIO.input(dt_A)
        if clk_A_state != clk_A_last_state:
            if dt_A_state != clk_A_state:
                for x in range(RATIO):
                    kit.stepper1.onestep(
                        direction=stepper.FORWARD
                    )
                    MOTOR_A += 1
            else:
                for x in range(RATIO):
                    kit.stepper1.onestep(
                        direction=stepper.BACKWARD
                    )
                    MOTOR_A -= 1
            clk_A_last_state = clk_A_state

        clk_B_state = GPIO.input(clk_B)
        dt_B_state = GPIO.input(dt_B)
        if clk_B_state != clk_B_last_state:
            if dt_B_state != clk_B_state:
                for x in range(RATIO):
                    kit.stepper2.onestep(
                        direction=stepper.FORWARD
                    )
                    MOTOR_B +=1
            else:
                for x in range(RATIO):
                    kit.stepper2.onestep(
                        direction=stepper.FORWARD
                    )
                    MOTOR_B -=1
            clk_B_last_state = clk_B_state

        time.sleep(0.01)

def main():
    try:
        dial()
    finally:
        GPIO.cleanup()


if __name__ == '__main__':
    main()
