import time
import board
import neopixel

LED_COUNT = 225

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

if __name__ == '__main__':
	test_sequence()


