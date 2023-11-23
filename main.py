from threading import Thread
import time
import os
import numpy as np

from installation import Installation
from messages import State

from audio.audio import RadioFuzzApp
from light.mock_lights import update_lights
from light.lights import set_lights, Product

from motor.control import move_motor, read_dials, MOTORS

dial_values = {
    "a": 1,
    "b": 2,
    "c": 3
}
MOTORS_NP = np.array([0,0,0])

Solutions = [None] * (len(Product) - 1)
Solutions[Product.FAN]          = np.array([0   ,0  ,0])
Solutions[Product.ROBOT]        = np.array([50  ,0  ,0])
Solutions[Product.SUPERSONIC]   = np.array([100 ,0  ,0])
Solutions[Product.VACUUM]       = np.array([150 ,0  ,0])
Solutions[Product.ZONE]         = np.array([175 ,0  ,0])

def convert_motors_to_np():
    # One rotation of the motor is 200
    MOTORS_NP[0] = MOTORS['a']['position'] % 200
    MOTORS_NP[1] = MOTORS['b']['position'] % 200
    MOTORS_NP[2] = MOTORS['c']['position'] % 200

def circular_distance(pos1, pos2, max_value=200):
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

def check_solutions():
    if MOTORS_NP == Solutions[Product.FAN]:
        set_lights(Product.FAN)
    elif MOTORS_NP == Solutions[Product.ROBOT]:
        set_lights(Product.ROBOT)
    elif MOTORS_NP == Solutions[Product.SUPERSONIC]:
        set_lights(Product.SUPERSONIC)
    elif MOTORS_NP == Solutions[Product.VACUUM]:
        set_lights(Product.VACUUM)
    elif MOTORS_NP == Solutions[Product.ZONE]:
        set_lights(Product.ZONE)
    else:
        set_lights(Product.NO_PRODUCT)


def main():  # Main function
    HOST, PORT = "localhost", 9999  # We have Raspberry PI with ID 92
    installation = Installation(HOST, PORT, id=92, init_state=State.INTERACTIVE)

    # # ------- CORE 1 Audio -------
    # fuzz_app = RadioFuzzApp(audio_clip_1, audio_clip_2, initial_position, solution1, solution2)
    # fuzz_app.start()  # This starts the thread
    dials_thread = Thread(target=read_dials)
    dials_thread.start()

    # ------- CORE 2 Start the network server -------
    server_thread = Thread(target=installation.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    # --------- CORE 3 Lights --------
    # motor_thread = Thread(target=move_motor)
    # motor_thread.start()
    set_lights(Product.NO_PRODUCT)
    products = [Product.FAN, Product.ROBOT, Product.SUPERSONIC, Product.VACUUM, Product.ZONE]

    global MOTORS

    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            os.system('clear')
            print('--------')
            print(f'Installation state: {State(installation.current_state()).name}')

            # if State(installation.current_state()) == State.OFF:
            #     # OFF
            #     pass

            # elif State(installation.current_state()) == State.DEMO:
            #     # DEMO
            #     pass

            # elif State(installation.current_state()) == State.INTERACTIVE:
            #     # INTERACTIVE

            convert_motors_to_np()
            print(f'MOTORS values:   {MOTORS_NP}')
            check_solutions()

            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
