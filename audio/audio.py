import pygame
from pydub import AudioSegment
import random

pygame.init()

def play_audio(audio_file):
    pygame.mixer.init()
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()


def add_distortion(input_audio, output_audio, distortion_factor):
    audio = AudioSegment.from_file(input_audio)
    distorted_audio = audio + distortion_factor
    distorted_audio.export(output_audio, format="mp3")


def add_radio_fuzz(input_audio, output_audio, distortion_factor):
    audio = AudioSegment.from_file(input_audio)

    # Generate random noise
    noise = AudioSegment.from_file("radio_long.mp3")  # Replace with your noise file

    # Apply the distortion effect
    distorted_audio = audio.overlay(noise, position=0)
    # distorted_audio = distorted_audio - distortion_factor  # Adjust audio levels for distortion
    distorted_audio = distorted_audio.set_channels(1)  # Convert to mono for a radio-like effect

    # Export the distorted audio
    distorted_audio.export(output_audio, format="mp3")

input_audio = "test_audio.mp3"
output_audio_distorted = "audio_distorted.mp3"
output_audio_fuzz = "audio_fuzz.mp3"

distortion_factor = 100  # Adjust as needed
# add_distortion(input_audio, output_audio_distorted, distortion_factor)
add_radio_fuzz(input_audio, output_audio_fuzz, distortion_factor)

# audio_file = "sweet_child_o_mine.mp3"
play_audio(output_audio_fuzz)

while pygame.mixer.music.get_busy():
    pygame.time.Clock().tick(10)