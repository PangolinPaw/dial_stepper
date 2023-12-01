import vlc
import time
import os

#instance = vlc.Instance('--aout=alsa', '--alsa-audio-device=default')
#player = instance.media_player_new()
#media = instance.media_new("your-audio-file.wav")
#player.set_media(media)

# List of .wav files
relative_path = os.path.abspath(os.path.dirname(__file__))

tracks = ["zone_trimmed.wav", "robot_trimmed.wav", "supersonic_trimmed.wav"]  # Replace with your file names

# Function to play a track
def play_track(track):
    player = vlc.MediaPlayer(relative_path + '/' + track)
    player.play()
    return player

# Function to switch track
def switch_track(current_player, new_track):
    if current_player.is_playing():
        current_player.stop()
    return play_track(new_track)

# Start playing the first track
current_player = play_track(tracks[0])

# Example: Switch to next track after 10 seconds
time.sleep(10)
current_player = switch_track(current_player, tracks[1])

time.sleep(10)
# Add your logic to switch between tracks as needed
