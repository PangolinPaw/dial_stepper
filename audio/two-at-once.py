import sys
import numpy as np
import soundfile as sf
import sounddevice as sd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSlider
from PyQt5.QtCore import Qt

class RadioFuzzApp(QMainWindow):
    def __init__(self, audio_file_path1, audio_file_path2):
        super().__init__()
        self.setWindowTitle('Audio Mixer with Static')
        self.audio_file_path1 = audio_file_path1
        self.audio_file_path2 = audio_file_path2
        self.initUI()
        self.init_audio_stream()

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Slider for blending audio and static
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 35)  # Set range from 0 to 35
        self.slider.setValue(0)  # Start with only the first clip playing
        self.slider.valueChanged.connect(self.adjust_mix)
        layout.addWidget(self.slider)

        self.show()

    def init_audio_stream(self):
        # Load both audio files
        self.data1, self.fs1 = sf.read(self.audio_file_path1, dtype='float32')
        self.data2, self.fs2 = sf.read(self.audio_file_path2, dtype='float32')

        # Ensure both audio clips are the same length and sample rate
        assert self.fs1 == self.fs2, "Sample rates do not match!"
        min_len = min(len(self.data1), len(self.data2))
        self.data1, self.data2 = self.data1[:min_len], self.data2[:min_len]

        # Audio stream setup
        self.stream = sd.OutputStream(samplerate=self.fs1, channels=self.data1.shape[1], callback=self.audio_callback)
        self.stream.start()

        # Initial mix is just the first audio clip
        self.mix_ratio = 0  # Ratio of how much of each audio clip to play
        self.position = 0

    def adjust_mix(self):
        # Adjust the mix ratio based on the slider's position
        self.mix_ratio = self.slider.value() / 35

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        
        chunk_end = self.position + frames
        if chunk_end > len(self.data1):
            chunk_end = len(self.data1)
            self.position = 0  # Loop back to the beginning

        # Calculate the mix and the amount of static
        static_intensity = 1 - abs(self.mix_ratio - 0.5) * 2
        static = np.random.normal(0, static_intensity, (frames, self.data1.shape[1])).astype('float32')

        # Mix the audio according to the slider position
        mix_chunk = ((1 - self.mix_ratio) * self.data1[self.position:chunk_end] +
                     self.mix_ratio * self.data2[self.position:chunk_end] +
                     static).astype('float32')

        outdata[:] = mix_chunk

        self.position += frames

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = RadioFuzzApp('test_audio.wav', 'piano_trim.wav')
    sys.exit(app.exec_())
