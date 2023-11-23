import sys
import numpy as np
import soundfile as sf
import sounddevice as sd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QWidget, QGraphicsView,
                             QGraphicsScene, QGraphicsEllipseItem)
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QBrush, QColor


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
        
        self.solution1 = (50, 50)  # These are example positions for solution1 and solution2
        self.solution2 = (250, 250)

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
        self.draw_solutions()  # Call this method to draw the solutions


        layout.addWidget(self.view)

        # Connect the scene's method to adjust_mix
        self.scene.update_mix = self.adjust_mix

        self.show()

# Add a new method to draw solutions on the scene
    def draw_solutions(self):
        # Draw the solution points on the scene
        solution_radius = 10
        solution_pen = QPen(Qt.NoPen)  # No border for the solution
        solution_brush = QBrush(QColor(255, 0, 0, 100))  # Semi-transparent red color

        # Solution 1
        solution1_item = QGraphicsEllipseItem(
            self.solution1[0] - solution_radius, 
            self.solution1[1] - solution_radius, 
            2 * solution_radius, 
            2 * solution_radius
        )
        solution1_item.setBrush(solution_brush)
        solution1_item.setPen(solution_pen)
        self.scene.addItem(solution1_item)

        # Solution 2
        solution2_item = QGraphicsEllipseItem(
            self.solution2[0] - solution_radius, 
            self.solution2[1] - solution_radius, 
            2 * solution_radius, 
            2 * solution_radius
        )
        solution2_item.setBrush(solution_brush)
        solution2_item.setPen(solution_pen)
        self.scene.addItem(solution2_item)

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
        ellipse_center_adjustment = QPointF(self.ellipse.rect().width() / 2, self.ellipse.rect().height() / 2)
    
    # Calculate the scene coordinates from the ratios
        current_pos = QPointF(x_ratio * self.scene.width(), y_ratio * self.scene.height()) - ellipse_center_adjustment

        # Now use current_pos to calculate the distances and mix_ratio
        dist_to_sol1 = np.hypot(current_pos.x() - self.solution1[0], current_pos.y() - self.solution1[1])
        dist_to_sol2 = np.hypot(current_pos.x() - self.solution2[0], current_pos.y() - self.solution2[1])


        # Determine the nearest solution and its distance
        nearest_solution_dist = min(dist_to_sol1, dist_to_sol2)

        # Define a max distance where static is at its peak (can be adjusted)
        max_static_dist = np.sqrt(self.view.width() ** 2 + self.view.height() ** 2)

        # Calculate the static intensity based on how far the nearest solution is
        self.static_intensity = (nearest_solution_dist / max_static_dist) * 0.2

        # Check which solution is closer and set the mix_ratio accordingly
        # Assuming you want a 1:1 ratio when directly over the solution
        if dist_to_sol1 < dist_to_sol2:
            # Closer to the first solution, mix_ratio favors the first audio clip
            self.mix_ratio = 1 - (dist_to_sol1 / max_static_dist)
        else:
            # Closer to the second solution, mix_ratio favors the second audio clip
            self.mix_ratio = (dist_to_sol2 / max_static_dist)

        # Ensure mix_ratio stays between 0 and 1
        self.mix_ratio = max(0, min(self.mix_ratio, 1))

        # Update the audio mix in real time
        self.update_audio_mix()


    # Call this method whenever you need to update the mix
    def update_audio_mix(self):
        pass

    def closeEvent(self, event):
        self.stream.stop()
        event.accept()

if __name__ == "__main__":
    audio_clip_1 = 'rock.wav'
    audio_clip_2 = 'piano.wav'
    app = QApplication(sys.argv)
    radio_fuzz_app = RadioFuzzApp(audio_clip_1, audio_clip_2)
    sys.exit(app.exec_())
