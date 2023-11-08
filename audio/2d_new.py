import sys
import numpy as np
import sounddevice as sd
import soundfile as sf
from PyQt5.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem
from PyQt5.QtCore import Qt, QRectF, QPointF

class RadioFuzzApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.main_window = FuzzWindow()
        self.main_window.show()

class FuzzWindow(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setSceneRect(QRectF(self.viewport().rect()))

        # Load audio files and fuzz
        self.data1, self.fs1 = self.load_audio('rock.wav')
        self.data2, self.fs2 = self.load_audio('piano.wav')
        self.fuzz, self.fs_fuzz = self.load_audio('radio_16.wav')

         # Coordinates where each audio clip plays clearly
        self.source1_position = np.array([100, 100])  # Adjust as needed
        self.source2_position = np.array([200, 200])  # Adjust as needed

        # Ensure all sample rates are the same
        assert self.fs1 == self.fs2 == self.fs_fuzz, "Sample rates do not match!"

        # Initialize the ellipse in the center
        self.initialize_ellipse()
        self.initialize_markers()


        # Set up audio stream
        self.stream = sd.OutputStream(callback=self.audio_callback, samplerate=self.fs1, channels=2)
        self.stream.start()

        # Current position in the audio file
        self.position = 0

    def initialize_ellipse(self):
        ellipse_radius = 10
        scene_center = self.sceneRect().center()
        self.ellipse = QGraphicsEllipseItem(scene_center.x() - ellipse_radius, scene_center.y() - ellipse_radius, ellipse_radius * 2, ellipse_radius * 2)
        self.ellipse.setBrush(Qt.white)
        self.ellipse.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.scene.addItem(self.ellipse)
        
    def initialize_markers(self):
        self.marker1 = self.create_marker(self.source1_position, Qt.red)
        self.marker2 = self.create_marker(self.source2_position, Qt.blue)
        
        # Add markers to the scene
        self.scene.addItem(self.marker1)
        self.scene.addItem(self.marker2)

    def create_marker(self, position, color):
        marker_radius = 5
        marker = QGraphicsEllipseItem(position[0] - marker_radius, position[1] - marker_radius, marker_radius * 2, marker_radius * 2)
        marker.setBrush(color)
        return marker

    def load_audio(self, filepath):
        data, fs = sf.read(filepath, always_2d=True)
        return data, fs

    def audio_callback(self, outdata, frames, time, status):
        chunk_end = self.position + frames
        self.check_buffer_length(chunk_end, frames)

        mix = self.mix_audio(frames)

        outdata[:frames] = mix
        self.position += frames
        if self.position >= len(self.data1):
            self.position = 0

    def check_buffer_length(self, chunk_end, frames):
        if chunk_end > len(self.data1):
            chunk_end = len(self.data1)
            frames = chunk_end - self.position

    def mix_audio(self, frames):
        # Calculate volume and mix based on the position of the ellipse
        pos = np.array([self.ellipse.pos().x(), self.ellipse.pos().y()])
        source1_position = np.array([100, 100])  # Example position for source 1
        source2_position = np.array([200, 200])  # Example position for source 2

        # Calculate distances to source positions
        distance_to_source1 = np.linalg.norm(pos - source1_position)
        distance_to_source2 = np.linalg.norm(pos - source2_position)

        # Fuzz amount based on distance to sources
        fuzz_amount = max(0, 1 - (1 / (distance_to_source1 + distance_to_source2 + 1)))

        # Blend audio sources and fuzz based on distances
        audio1_volume = 1 - distance_to_source1 / (distance_to_source1 + distance_to_source2 + 1)
        audio2_volume = 1 - distance_to_source2 / (distance_to_source1 + distance_to_source2 + 1)

        mix = (self.data1[self.position:self.position + frames] * audio1_volume +
               self.data2[self.position:self.position + frames] * audio2_volume +
               self.fuzz[self.position:self.position + frames] * fuzz_amount)

        return mix

    def closeEvent(self, event):
        self.stream.stop()
        self.stream.close()
        super().closeEvent(event)

if __name__ == '__main__':
    app = RadioFuzzApp(sys.argv)
    sys.exit(app.exec_())
