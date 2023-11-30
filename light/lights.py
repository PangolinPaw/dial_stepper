import time
import board
import neopixel
from enum import Enum


from light.image_convertor import fan_array, robot_array, zone_array, vacuum_array, supersonic_array, all_white_array, off_array

LED_COUNT = 225

class Product(Enum):
	OFF = 0
	NO_PRODUCT = 1
	FAN = 2
	ROBOT = 3
	SUPERSONIC = 4
	VACUUM = 5
	ZONE = 6


pixels = neopixel.NeoPixel(board.D18, LED_COUNT)

def test_sequence():
	'''Illuminate each LED in turn to check operation'''
	pixels.fill((0, 0, 0))
	for x in range(LED_COUNT):
		pixels[x] = (0, 255, 255)
		time.sleep(0.25)
	for x in range(LED_COUNT):
		pixels[x] = (0, 0, 0)
		time.sleep(0.25)

def set_lights(state):
	if state == Product.OFF:
		display_product(off_array)
	elif state == Product.NO_PRODUCT:
		display_product(all_white_array)
	elif state == Product.FAN:
		display_product(fan_array)
	elif state == Product.ROBOT:
		display_product(robot_array)
	elif state == Product.ZONE:
		display_product(zone_array)
	elif state == Product.VACUUM:
		display_product(vacuum_array)
	elif state == Product.SUPERSONIC:
		display_product(supersonic_array)


def display_product(led_values):
	for x in range(LED_COUNT):
		if sum(led_values[x] < 200):
			pixels[x] = led_values[x]
		else:
			pixels[x] = [0,0,0]


if __name__ == '__main__':
	image_path = "disk-image.png"
	arrays = fan_array, robot_array, zone_array, vacuum_array, supersonic_array, all_white_array
	while True:
		for x in arrays:
			display_product(x)
			time.sleep(3)


