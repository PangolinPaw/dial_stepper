import os
import time
import threading

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
        direction = input(' Turn Clockwise or Anticlockwise? ')
        if len(direction) > 0:
            if direction[0].upper() == 'C':
                DIAL_POSITION += 1
                if DIAL_POSITION > 23:
                    DIAL_POSITION = 0
            elif direction[0].upper() == 'A':
                DIAL_POSITION -= 1
                if DIAL_POSITION < 0:
                    DIAL_POSITION = 23

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
    except KeyboardInterrupt:
        interrupt.set()


if __name__ == '__main__':
    main()
