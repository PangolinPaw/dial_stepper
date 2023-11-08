import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, QRectF, QPointF
import sounddevice as sd
import soundfile as sf

# Replace these with the paths to your actual audio files
AUDIO_CLIP_1 = "rock.wav"
AUDIO_CLIP_2 = "piano.wav"

# Load audio clips
data1, fs1 = sf.read(AUDIO_CLIP_1)
data2, fs2 = sf.read(AUDIO_CLIP_2)

# Ensure same sample rate for both clips
assert fs1 == fs2

# Mix audio depending on the position on the plane
def mix_audio(position, clip1, clip2, vol1, vol2):
    # Add radio fuzz effect by introducing random noise
    fuzz = np.random.normal(0, 0.005, clip1.shape).astype(clip1.dtype)
    # Mix the clips with their respective volumes
    return (clip1 * vol1 + clip2 * vol2 + fuzz * (1 - vol1 - vol2))

class FuzzWindow(QMainWindow):
    def __init__(self, parent=None):
        super(FuzzWindow, self).__init__(parent)
        self.setMinimumSize(400, 400)
        self.marker1 = QPointF(100, 100)  # Point for audio clip 1
        self.marker2 = QPointF(300, 300)  # Point for audio clip 2
        self.dragging = False
        self.current_pos = QPointF(self.width() / 2, self.height() / 2)

        self.initUI()

        # Audio stream setup
        self.stream = sd.OutputStream(
            samplerate=fs1,
            channels=data1.shape[1] if data1.ndim > 1 else 1,
            blocksize=1024,
            callback=self.audio_callback
        )

        # Start the audio stream
        self.start_audio_stream()

    def initUI(self):
        # Your UI initialization code
        self.setWindowTitle('Audio Fuzz Mixer')
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw markers
        painter.setPen(QPen(Qt.red, 8, Qt.SolidLine))
        painter.drawPoint(self.marker1)
        painter.drawPoint(self.marker2)

        # Draw draggable position
        painter.setBrush(QBrush(Qt.white, Qt.SolidPattern))
        painter.drawEllipse(self.current_pos, 10, 10)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.current_pos = event.pos()
            self.update()

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.current_pos = event.pos()
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

    def calculate_volume(self, current_pos, marker_pos):
        distance = np.linalg.norm(np.array([current_pos.x(), current_pos.y()]) - np.array([marker_pos.x(), marker_pos.y()]))
        max_distance = np.linalg.norm([self.width(), self.height()])
        volume = 1 - (distance / max_distance)
        return max(min(volume, 1), 0)

    def start_audio_stream(self):
        self.position = 0
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)
        chunk_start = self.position
        chunk_end = chunk_start + frames
        if chunk_end > len(data1):
            chunk_end = len(data1)
            self.position = 0  # Loop back to the beginning

        vol1 = self.calculate_volume(self.current_pos, self.marker1)
        vol2 = self.calculate_volume(self.current_pos, self.marker2)

        clip1 = data1[chunk_start:chunk_end]
        clip2 = data2[chunk_start:chunk_end]

        mix = mix_audio(self.position, clip1, clip2, vol1, vol2)

        outdata[:] = mix
        self.position += frames
        if chunk_end == len(data1):
            self.position = 0  # Loop back to the beginning

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWin = FuzzWindow()
    sys.exit(app.exec_())
