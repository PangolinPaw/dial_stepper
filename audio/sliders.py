import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QSlider, QPushButton, QVBoxLayout, QWidget, QFileDialog)
from PyQt5.QtCore import Qt
from pydub import AudioSegment
from pydub.generators import WhiteNoise
from pydub.playback import play

class RadioFuzzApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Radio Fuzz Effect')
        self.initUI()

        self.audio_clip = None

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # Slider for fuzz amount
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(50)
        layout.addWidget(self.slider)

        # Button to load audio
        self.load_button = QPushButton('Load Audio', self)
        self.load_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_button)

        # Button to apply fuzz and play
        self.fuzz_button = QPushButton('Apply Fuzz and Play', self)
        self.fuzz_button.clicked.connect(self.apply_fuzz)
        layout.addWidget(self.fuzz_button)

    def load_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Audio", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if file_path:
            self.audio_clip = AudioSegment.from_file(file_path)

    def apply_fuzz(self):
        if self.audio_clip:
            fuzz_amount = self.slider.value()
            noise = WhiteNoise().to_audio_segment(duration=len(self.audio_clip)).apply_gain(-3 * (100 - fuzz_amount))
            combined = self.audio_clip.overlay(noise)
            play(combined)
        else:
            print("No audio loaded!")

def main():
    app = QApplication(sys.argv)
    ex = RadioFuzzApp()
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
