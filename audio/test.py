import vlc
import os
import csv

from light.lights import Product

# List of .wav files
relative_path = os.path.abspath(os.path.dirname(__file__))

sound_solutions = [None] * (len(Product) + 1)
sound_solutions[Product.FAN.value]          = 'fan_trimmed.wav' # You spin me right round
sound_solutions[Product.ROBOT.value]        = 'robot_trimmed.wav' # Harder better faster stronger
sound_solutions[Product.SUPERSONIC.value]   = 'supersonic_trimmed.wav' # In the air
sound_solutions[Product.VACUUM.value]       = 'vacuum_trimmed.wav' #
sound_solutions[Product.ZONE.value]         = 'zone_trimmed.wav' # Jake Dyson Audio
sound_solutions[Product.NO_PRODUCT.value]   = 'radio.wav' # Jake Dyson Audio

# Function to play a track
def play_track(product):
    player = vlc.MediaPlayer(relative_path + '/' + sound_solutions[product.value])
    player.play()
    return player

# Function to switch track
def switch_track(current_player, new_product):
    if current_player.is_playing():
        current_player.stop()
    return play_track(new_product)

if __name__ == '__main__':
    # Start playing the first track
    current_solution = Product.ZONE
    current_player = play_track(Product.ZONE)

    while True:
        if os.path.exists('current_solution.csv'):
            with open('current_solution.csv', 'r') as csv_file:
                csv_reader = csv.reader(csv_file)
                solution = next(csv_reader)[0]

                if solution != current_solution:
                    current_solution = solution
                    current_player = switch_track(current_player, Product(solution))
