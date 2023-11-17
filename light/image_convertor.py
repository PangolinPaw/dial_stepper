import cv2
import numpy as np
import os

LED_COUNT = 225  # For a 15x15 matrix

# Assuming LED_COUNT is the total number of LEDs

def convert_image(path):
        
    # Read the image and resize it
    img = cv2.imread(path, cv2.IMREAD_ANYCOLOR)
    resized_img = cv2.resize(img, (15, 15))

    # Initialize the LED array
    led_array = np.zeros((LED_COUNT, 3), dtype=int)  # for storing RGB values

    # Map the pixels to the LED array
    for row in range(15):  # since the matrix is 15x15
        for col in range(15):
            if row % 2 == 0:
                # Even rows go right to left
                index = (15 * (14 - row)) + (14 - col)
            else:
                # Odd rows go left to right
                index = (15 * (14 - row)) + col

            # Assign the pixel value to the correct LED
            led_array[index] = resized_img[row, col]
    return led_array


print("-----------------")
print(os.cwd())
fan_array = convert_image("./light/dilated/fan.jpeg")
robot_array = convert_image("./light/dilated/robot.jpeg")
supersonic_array = convert_image("./light/dilated/supersonic.jpeg")
vacuum_array = convert_image("./light/dilated/vacuum.jpeg")
zone_array = convert_image("./light/dilated/zone.jpeg")
all_white_array = np.ones((LED_COUNT, 3), dtype=int)
