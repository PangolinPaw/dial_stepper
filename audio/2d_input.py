import sys
import numpy as np
import soundfile as sf
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView,
                             QGraphicsScene, QGraphicsEllipseItem)
from PyQt5.QtCore import Qt, QRectF

class CustomEllipse(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h):
        super().__init__(x, y, w, h)
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        if self.scene():
            # Ensure the item stays within the scene bounds
            rect = self.scene().sceneRect()
            if not rect.contains(self.pos()):
                # Keep the item within the scene rect bounds
                new_x = min(rect.right(), max(self.pos().x(), rect.left()))
                new_y = min(rect.bottom(), max(self.pos().y(), rect.top()))
                self.setPos(new_x, new_y)
            # Emit a signal to update the mix and static levels
            self.scene().update_mix(self.pos().x() / rect.width(), self.pos().y() / rect.height())


class RadioFuzzApp(QMainWindow):
    def __init__(self, audio_file_path1, audio_file_path2):
        super().__init__()
        self.setWindowTitle('Audio Mixer with Static and 2D Control')
        self.audio_file_path1 = audio_file_path1
        self.audio_file_path2 = audio_file_path2
        self.data1, self.samplerate = sf.read(self.audio_file_path1)
        self.data2, _ = sf.read(self.audio_file_path2)
        self.mix_ratio = 0.5
        self.static_intensity = 0.5
        self.position = 0
        self.initUI()
        self.init_audio_stream()

    def initUI(self):
        # Main widget and layout
        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # 2D plane setup using QGraphicsView and QGraphicsScene
        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setFixedSize(400, 400)
        self.scene.setSceneRect(0, 0, 300, 300)

        # Draggable ellipse item
        self.ellipse = CustomEllipse(0, 0, 20, 20)
        self.ellipse.setPos(150, 150)  # Starting position at center
        self.scene.addItem(self.ellipse)

        layout.addWidget(self.view)

        # Connect the scene's method to adjust_mix
        self.scene.update_mix = self.adjust_mix

        self.show()

    def init_audio_stream(self):
        self.stream = sd.OutputStream(
            samplerate=self.samplerate,
            channels=max(self.data1.shape[1], self.data2.shape[1]),
            callback=self.audio_callback,
        )
        self.stream.start()

    def audio_callback(self, outdata, frames, time, status):
        if status:
            print(status, file=sys.stderr)

        chunk_end = self.position + frames
        if chunk_end > len(self.data1):
            chunk_end = len(self.data1)
            self.position = 0  # Loop back to the beginning

        # Scale the static based on y position
        scaled_static = np.random.normal(0, self.static_intensity, (frames, self.data1.shape[1])).astype('float32')

        # Mix the audio according to the x position
        mix_chunk = ((1 - self.mix_ratio) * self.data1[self.position:chunk_end] +
                     self.mix_ratio * self.data2[self.position:chunk_end] +
                     scaled_static).astype('float32')

        outdata[:] = mix_chunk

        self.position += frames

    def adjust_mix(self, x_ratio, y_ratio):
        self.mix_ratio = x_ratio
        self.static_intensity = y_ratio * 0.2  # Reduce static intensity

    def closeEvent(self, event):
        self.stream.stop()
        event.accept()

if __name__ == "__main__":
    audio_clip_1 = 'rock.wav'
    audio_clip_2 = 'piano.wav'
    app = QApplication(sys.argv)
    radio_fuzz_app = RadioFuzzApp(audio_clip_1, audio_clip_2)
    sys.exit(app.exec_())