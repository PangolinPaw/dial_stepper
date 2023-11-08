import sys
import io
from PyQt5.QtWidgets import QApplication, QMainWindow, QSlider, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt
from pydub import AudioSegment
from pydub.generators import WhiteNoise
import pygame

class RadioFuzzApp(QMainWindow):
    def __init__(self, audio_file_path):
        super().__init__()
        self.setWindowTitle('Radio Fuzz Effect')
        self.audio_file_path = audio_file_path
        self.audio_clip = AudioSegment.from_file(self.audio_file_path)
        self.noise = WhiteNoise().to_audio_segment(duration=len(self.audio_clip))
        self.initUI()
        self.init_pygame()
        self.playing = False

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Slider for fuzz amount
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(85, 100)
        self.slider.setValue(85)
        self.slider.valueChanged.connect(self.adjust_fuzz)
        layout.addWidget(self.slider)

    def init_pygame(self):
        # Initialize pygame mixer
        pygame.mixer.init(frequency=self.audio_clip.frame_rate)

    def adjust_fuzz(self):
        if not self.playing:
            self.playing = True
            self.apply_fuzz()
        else:
            # Stop the playback and start again with the new fuzz value
            pygame.mixer.music.stop()
            self.apply_fuzz()

    def apply_fuzz(self):
        fuzz_amount = self.slider.value()
        adjusted_noise = self.noise.apply_gain(-3 * (100 - fuzz_amount))
        combined = self.audio_clip.overlay(adjusted_noise)
        
        # Export combined audio to a byte buffer
        byte_io = io.BytesIO()
        combined.export(byte_io, format='mp3')
        byte_io.seek(0)
        
        # Load the byte buffer into pygame's mixer
        pygame.mixer.music.load(byte_io)
        pygame.mixer.music.play(loops=-1)  # Loop indefinitely

def main():
    # Set the path to your audio file here
    audio_file_path = 'test_audio.mp3'

    app = QApplication(sys.argv)
    ex = RadioFuzzApp(audio_file_path)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
