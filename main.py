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

robot_solution = np.array([0,0,0])
zone_solution = np.array([0,50,0])


def convert_motors_to_np():
    # One rotation of the motor is 200
    MOTORS_NP[0] = MOTORS['a']['position'] % 200
    MOTORS_NP[1] = MOTORS['b']['position'] % 200
    MOTORS_NP[2] = MOTORS['c']['position'] % 200

def listen_for_dial():
    while True:
        dial_values['a'], dial_values['b'], dial_values['c'] = get_dial_values()
        time.sleep(0.1)  # Sleep to prevent this from running too fast

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

    

def main():  # Main function
    HOST, PORT = "localhost", 9999  # We have Raspberry PI with ID 92
    installation = Installation(HOST, PORT, id=92, init_state=State.INTERACTIVE)

    # Paths to your audio files
    audio_clip_1 = 'audio/rock.wav'
    audio_clip_2 = 'audio/piano.wav'
    
    # Starting position and solution positions
    initial_position = (50, 50, 50)
    solution1 = (25, 25, 25)
    solution2 = (75, 75, 75)

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
    
    counter = 0
    product_i = 0
    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            counter += 1
            if counter == 20:
                set_lights(products[product_i % len(products)])
                product_i += 1


            os.system('clear')
            print('--------')
            print(f'Installation state: {State(installation.current_state()).name}')
            
            convert_motors_to_np()
            print(f'MOTORS values:   {MOTORS_NP}')
            get_distance_to_solutions()
            
            # update_lights(val_tuple)
            # update_motors(val_tuple)
            #fuzz_app.update_position(val_tuple)
            
            time.sleep(0.2)
    except KeyboardInterrupt:
        print("Shutting down")

if __name__ == '__main__':
    main()
