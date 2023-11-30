from threading import Thread
import time
import os
import numpy as np

from installation import Installation
from messages import State

from light.mock_lights import update_lights
from light.lights import set_lights, Product

# from playsound import playsound
from motor.control import set_motors, read_dials, MOTORS, release_all

dial_values = {
    "a": 1,
    "b": 2,
    "c": 3
}
MOTORS_NP = np.array([0,0,0])

######## Motor positions for each solutions
POSITION_TOLERANCE = 10 # 5/400, 400 is a full rotation of the motor
Solutions = [None] * (len(Product) + 1)
Solutions[Product.FAN.value]          = np.array([150   ,50     ,150])
Solutions[Product.ROBOT.value]        = np.array([0     ,0      ,0])
Solutions[Product.SUPERSONIC.value]   = np.array([0     ,250    ,0])
Solutions[Product.VACUUM.value]       = np.array([0     ,100    ,50])
Solutions[Product.ZONE.value]         = np.array([300   ,0      ,200])

######## Demo Mode Variables
DEMO_INTERVAL_S = 15
current_solution = Product.OFF
demo_start_time = 0


def convert_motors_to_np():
    # One rotation of the motor is 400
    MOTORS_NP[0] = MOTORS['a']['position'] % 400
    MOTORS_NP[1] = MOTORS['b']['position'] % 400
    MOTORS_NP[2] = MOTORS['c']['position'] % 400

def circular_distance(pos1, pos2, max_value=400):
    """
    Calculate the minimum circular distance between two positions.

    :param pos1: First position (current position of motor).
    :param pos2: Second position (target position/solution).
    :param max_value: Maximum value on the circle (200 for motor positions).
    :return: Minimum distance between the two positions.
    """
    distance = np.abs(pos1 - pos2)
    return np.minimum(distance, max_value - distance)

def solution_distance(current_position, solution):
    """
    Calculate the distance between current motor positions and a solution.

    :param current_position: numpy array of current positions of motors.
    :param solution: numpy array of solution positions.
    :return: Total distance to the solution.
    """
    distances = circular_distance(current_position, solution)
    return np.sum(distances)

def get_distance_to_solutions():
    distance_to_robot = solution_distance(MOTORS_NP, robot_solution)
    distance_to_zone = solution_distance(MOTORS_NP, zone_solution)
    print(f'Distance to robot:   {distance_to_robot}')
    print(f'Distance to zone:   {distance_to_zone}')

sound_solutions = [None] * (len(Product) + 1)
sound_solutions[Product.FAN.value]          = 'fan_trimmed.wav' # You spin me right round
sound_solutions[Product.ROBOT.value]        = 'robot_trimmed.wav' # Harder better faster stronger
sound_solutions[Product.SUPERSONIC.value]   = 'supersonic_trimmed.wav' # In the air
sound_solutions[Product.VACUUM.value]       = 'vacuum_trimmed.wav' #
sound_solutions[Product.ZONE.value]         = 'zone_trimmed.wav' # Jake Dyson Audio
sound_solutions[Product.NO_PRODUCT.value]   = 'radio.wav' # Jake Dyson Audio


def check_solutions():
    global current_solution

    if np.allclose(MOTORS_NP, Solutions[Product.FAN.value], atol= POSITION_TOLERANCE):
        if current_solution != Product.FAN:
            set_lights(Product.FAN)
            # playsound(sound_solutions[Product.FAN.value])
            current_solution = Product.FAN


    elif np.allclose(MOTORS_NP, Solutions[Product.ROBOT.value], atol= POSITION_TOLERANCE):
        if current_solution != Product.ROBOT:
            set_lights(Product.ROBOT)
            # playsound(sound_solutions[Product.ROBOT.value])
            current_solution = Product.ROBOT

    elif np.allclose(MOTORS_NP, Solutions[Product.SUPERSONIC.value], atol= POSITION_TOLERANCE):
        if current_solution != Product.SUPERSONIC:
            set_lights(Product.SUPERSONIC)
            # playsound(sound_solutions[Product.SUPERSONIC.value])
            current_solution = Product.SUPERSONIC

    elif np.allclose(MOTORS_NP, Solutions[Product.VACUUM.value], atol= POSITION_TOLERANCE):
        if current_solution != Product.VACUUM:
            set_lights(Product.VACUUM)
            # playsound(sound_solutions[Product.VACUUM.value])
            current_solution = Product.VACUUM

    elif np.allclose(MOTORS_NP, Solutions[Product.ZONE.value], atol= POSITION_TOLERANCE):
        if current_solution != Product.ZONE:
            set_lights(Product.ZONE)
            # playsound(sound_solutions[Product.ZONE.value])
            current_solution = Product.ZONE
    else:
        if current_solution != Product.NO_PRODUCT:
            set_lights(Product.NO_PRODUCT)
            current_solution = Product.NO_PRODUCT
            # playsound(sound_solutions[Product.NO_PRODUCT.value])

def get_next_solution(current_solution):
    next_solution = Product((current_solution.value + 1) % (len(Product) - 2) + 2)
    return next_solution

def demo_mode():
    new_time = time.time()

    if(new_time - demo_start_time):
        # Display next solution
        demo_start_time = new_time
        set_lights(Product.NO_PRODUCT)
        current_solution = get_next_solution()
        motor_positions = Solutions[current_solution]
        set_motors(motor_positions)
        set_lights(Product(current_solution))

def interactive_mode():
    convert_motors_to_np()
    print(f'MOTORS values:   {MOTORS_NP}')
    check_solutions()

def off():
    motor_positions = Solutions[Product.FAN]
    set_motors(motor_positions)
    set_lights(Product.OFF)

def main():  # Main function
    HOST, PORT = "localhost", 9999  # We have Raspberry PI with ID 92
    installation = Installation(HOST, PORT, id=92, init_state=State.INTERACTIVE)

    # # ------- CORE 1 Dials -------
    dials_thread = Thread(target=read_dials)
    dials_thread.start()

    # ------- CORE 2 Start the network server -------
    server_thread = Thread(target=installation.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # --------- CORE 2 Lights --------
    # motor_thread = Thread(target=move_motor)
    # motor_thread.start()
    global MOTORS

    time.sleep(1)

    set_lights(Product.NO_PRODUCT)
    current_solution = Product.NO_PRODUCT

    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            os.system('clear')
            print('--------')
            print(f'Installation state: {State(installation.current_state()).name}')
            print(f'Current solution:  {current_solution}')
            interactive_mode()

            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Shutting down")
        release_all()

if __name__ == '__main__':
    main()
