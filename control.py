
# https://github.com/modmypi/Rotary-Encoder/blob/master/rotary_encoder.py
# https://learn.adafruit.com/adafruit-dc-and-stepper-motor-hat-for-raspberry-pi/using-stepper-motors

DIAL_POSITION = 0
MOTOR_POSITION = 0

def convert(dial):
	motor = dial * 8
	return motor

'''
Flow:
- Dial turned X steps in Y direction
- Calculate new dial position P
- Covnert P to motor target position T
- Send signal to rotate motor in direction Y until T reached
'''

if __name__ == '__main__':
	print(' dial | motor')
	for x in range(0, 24):
		print(f'   {str(x).rjust(2)} |   {str(convert(x)).rjust(3)}')

