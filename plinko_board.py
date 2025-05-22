import random
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRectF
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect

class PlinkoBoard(QGraphicsView):
    def __init__(self, reward_labels, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints())
        self.setMinimumSize(300, 400)
        self.pegs = []
        self.slots = []
        self.reward_labels = reward_labels
        self.bounce_sound = QSoundEffect()
        self.bounce_sound.setSource(QUrl.fromLocalFile("assets/bounce.wav"))
        self.land_sound = QSoundEffect()
        self.land_sound.setSource(QUrl.fromLocalFile("assets/land.wav"))
        self.init_board()

    def resizeEvent(self, event):
        self.init_board()
        super().resizeEvent(event)

    def init_board(self):
        self.scene.clear()
        self.pegs = []
        self.slots = []
        w = self.viewport().width()
        h = self.viewport().height()
        self.scene.setSceneRect(0, 0, w, h)
        spacing_x = w / 10
        spacing_y = h / 12
        peg_d = min(spacing_x, spacing_y) / 2
        for row in range(8):
            for col in range(10):
                offset_x = spacing_x / 2 if row % 2 == 0 else 0
                x = col * spacing_x + offset_x + spacing_x * 0.1
                y = row * spacing_y + spacing_y * 0.8
                peg = QGraphicsEllipseItem(x, y, peg_d, peg_d)
                peg.setBrush(Qt.black)
                self.scene.addItem(peg)
                self.pegs.append(peg)
        slot_width = w / 10
        slot_height = h / 13
        for i, label in enumerate(self.reward_labels):
            slot = QGraphicsRectItem(i * slot_width + spacing_x * 0.1, h - slot_height * 1.2, slot_width - spacing_x * 0.2, slot_height)
            slot.setBrush(QColor("lightblue"))
            self.scene.addItem(slot)
            self.slots.append((slot, label))

    def drop_chip(self, player_name, chip_color):
        w = self.viewport().width()
        chip_d = min(w / 20, 30)
        chip = QGraphicsEllipseItem(w / 2 - chip_d / 2, 0, chip_d, chip_d)
        chip.setBrush(QColor(chip_color))
        self.scene.addItem(chip)
        self.animate_chip(chip, player_name)

    def animate_chip(self, chip, player_name):
        def step():
            y = chip.y() + self.viewport().height() / 60
            jitter = random.randint(-10, 10) * (self.viewport().width() / 600)
            x = chip.x() + jitter
            chip.setPos(x, y)
            self.bounce_sound.play()
            if y >= self.viewport().height() - self.viewport().height() / 13 * 1.2:
                QTimer.singleShot(100, lambda: self.resolve_chip(chip, player_name))
                timer.stop()
        timer = QTimer()
        timer.timeout.connect(step)
        timer.start(50)

    def resolve_chip(self, chip, player_name):
        chip_center_x = chip.x() + chip.rect().width() / 2
        w = self.viewport().width()
        slot_width = w / 10
        slot_index = int((chip_center_x - slot_width * 0.1) // slot_width)
        if 0 <= slot_index < len(self.slots):
            label = self.slots[slot_index][1]
            result = f"{player_name} landed on: {label}"
        else:
            result = f"{player_name} missed the slots!"
        self.land_sound.play()
        if self.parent():
            self.parent().display_result(result) 