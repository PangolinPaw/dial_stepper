import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
import sounddevice as sd
import soundfile as sf

class RadioFuzzApp(QMainWindow):
    def __init__(self, audio_file_path):
        super().__init__()
        self.setWindowTitle('Radio Fuzz Effect')
        self.audio_file_path = audio_file_path
        self.initUI()
        self.init_audio_stream()

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Slider for fuzz amount
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)  # Set initial value to 0
        self.slider.valueChanged.connect(self.adjust_fuzz)
        layout.addWidget(self.slider)

        self.show()

    def init_audio_stream(self):
        # Open the audio file
        self.data, self.fs = sf.read(self.audio_file_path, dtype='float32')
        self.stream = sd.OutputStream(samplerate=self.fs, channels=self.data.shape[1], callback=self.audio_callback)
        self.stream.start()

        # State
        self.fuzz_amount = 0
        self.position = 0

    def adjust_fuzz(self):
        self.fuzz_amount = self.slider.value()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        
        chunk_end = self.position + frames
        chunk = self.data[self.position:chunk_end]

        # Apply the fuzz effect
        noise = np.random.normal(0, self.fuzz_amount / 100, chunk.shape).astype('float32')
        outdata[:] = chunk + noise

        self.position += frames
        if chunk_end >= len(self.data):
            self.position = 0  # Loop back to the beginning

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

def main():
    # Set the path to your audio file here
    audio_file_path = 'test_audio.wav'  # Make sure it's a WAV file

    app = QApplication(sys.argv)
    radio_fuzz_app = RadioFuzzApp(audio_file_path)
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
