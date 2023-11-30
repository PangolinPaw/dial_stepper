import threading
import numpy as np
import soundfile as sf
import sounddevice as sd

class RadioFuzzApp(threading.Thread):
    def __init__(self, audio_file_path1, audio_file_path2, position, solution1, solution2):
        super().__init__()
        self.audio_file_path1 = audio_file_path1
        self.audio_file_path2 = audio_file_path2
        
        # Read the audio files
        self.data1, self.samplerate = sf.read(self.audio_file_path1)
        self.data2, _ = sf.read(self.audio_file_path2)

        # Set initial mix ratio and static intensity
        self.mix_ratio = 0.5
        self.static_intensity = 0.5
        
        # Position is now a 3D tuple (x, y, z)
        self.position = position
        
        # Solutions are now points in 3D space
        self.solution1 = solution1
        self.solution2 = solution2
        
        # Index in the audio buffer
        self.sample_index = 0

        # Initialize the audio stream
        self.init_audio_stream()
        
        # Set the thread as a daemon
        self.daemon = True

    def run(self):
        # Start the audio stream
        self.stream.start()

    def init_audio_stream(self):
        # Determine the number of channels in the audio files
        channels1 = self.data1.shape[1] if self.data1.ndim > 1 else 1
        channels2 = self.data2.shape[1] if self.data2.ndim > 1 else 1
        
        # Initialize the output stream with the callback
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=max(channels1, channels2),
            callback=self.audio_callback,
        )

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        # Calculate the end of the current chunk
        chunk_end = self.sample_index + frames
        if chunk_end > len(self.data1):
            chunk_end = len(self.data1)
            self.sample_index = 0  # Loop back to the beginning if needed

        # Generate scaled static based on static_intensity
        scaled_static = np.random.normal(0, self.static_intensity, frames).astype('float32')

        # Mix the audio according to the mix_ratio
        mix_chunk = ((1 - self.mix_ratio) * self.data1[self.sample_index:chunk_end] +
                     self.mix_ratio * self.data2[self.sample_index:chunk_end] +
                     scaled_static).astype('float32')

        # Ensure mix_chunk is reshaped to match the outdata shape, which is (frames, channels)
        mix_chunk = mix_chunk.reshape(-1, 1)

        # Write the mixed audio to the output buffer
        outdata[:] = mix_chunk

        # Update the sample index
        self.sample_index = (self.sample_index + frames) % len(self.data1)

    def adjust_mix(self, position):
        # Adjust mix based on the 3D position
        # Calculate the Euclidean distance from the position to both solutions in 3D
        dist_to_sol1 = np.linalg.norm(np.subtract(position, self.solution1))
        dist_to_sol2 = np.linalg.norm(np.subtract(position, self.solution2))

        # Find the nearest solution and its distance
        nearest_solution_dist = min(dist_to_sol1, dist_to_sol2)
        # Assuming a 300x300x300 cube for max distance
        max_static_dist = np.linalg.norm([300, 300, 300])

        # Calculate the static intensity based on how far the nearest solution is
        self.static_intensity = (nearest_solution_dist / max_static_dist) * 0.2

        # Check which solution is closer and set the mix_ratio accordingly
        if dist_to_sol1 < dist_to_sol2:
            self.mix_ratio = 1 - (dist_to_sol1 / max_static_dist)
        else:
            self.mix_ratio = (dist_to_sol2 / max_static_dist)

        # Ensure mix_ratio stays between 0 and 1
        self.mix_ratio = max(0, min(self.mix_ratio, 1))

    def update_position(self, position):
        # Update the 3D position
        self.position = position
        # Adjust the audio mix based on the new position
        self.adjust_mix(position)
        print(f'AUDIO:   {self.position}')
    
    def close_stream(self):
        # Safely close the audio stream
        self.stream.stop()
