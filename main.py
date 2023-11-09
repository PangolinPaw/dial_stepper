from installation import Installation
from threading import Thread
import time
from messages import State

from light.mock_lights import update_lights
from motor.mock_motor import update_motors
from dials.mock_dial import get_dial_values

dial_values = {
    "a" : 1,
    "b" : 2,
    "c" : 3
}

def listen_for_dial(installation): # CORE 2
    while True:
        dial_values['a'], dial_values['b'], dial_values['c'] = get_dial_values()
        time.sleep(1)  # Sleep to prevent this from running too fast

def main(): # 
    HOST, PORT = "localhost", 9999  # We have Raspberry PI with ID 92
    installation = Installation(HOST, PORT, id=92, init_state=State.INTERACTIVE)

    # ----- CORE 1 Start the network server in a separate thread -----
    server_thread = Thread(target=installation.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    
    # --------- CORE 2 Start the dial listener in a separate thread --------
    dial_thread = Thread(target=listen_for_dial, args=(installation,))
    dial_thread.daemon = True
    dial_thread.start()
    
    # Keep the main thread alive to prevent the program from exiting
    try:
        while True:
            print('--------')
            print(f'Dial values:   {dial_values}')
            print(f'Installation state: {State(installation.current_state()).name}')
            update_lights(dial_values)
            update_motors(dial_values)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down")


if __name__ == '__main__':
    main()
