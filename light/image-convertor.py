import cv2
import numpy as np

# Assuming LED_COUNT is the total number of LEDs
LED_COUNT = 225  # For a 15x15 matrix

# Read the image and resize it
img = cv2.imread("disk-image.png", cv2.IMREAD_ANYCOLOR)
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

print(led_array)


# At this point, led_array will contain the mapped RGB values for each LED
while True:
    cv2.imshow("Sheep", resized_img)
    cv2.waitKey(0)
    sys.exit() # to exit from all the processes
 
cv2.destroyAllWindows() # destroy all windows

