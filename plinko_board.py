import random
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem
)
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect

class PlinkoBoard(QGraphicsView):
    def __init__(self, reward_labels, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setRenderHint(self.renderHints())
        self.setFixedSize(600, 800)
        self.scene.setSceneRect(0, 0, 580, 780)
        self.pegs = []
        self.slots = []
        self.reward_labels = reward_labels
        self.bounce_sound = QSoundEffect()
        self.bounce_sound.setSource(QUrl.fromLocalFile("assets/bounce.wav"))
        self.land_sound = QSoundEffect()
        self.land_sound.setSource(QUrl.fromLocalFile("assets/land.wav"))
        self.init_board()

    def init_board(self):
        self.scene.clear()
        self.pegs = []
        self.slots = []
        spacing_x = 60
        spacing_y = 70
        for row in range(8):
            for col in range(10):
                offset_x = spacing_x // 2 if row % 2 == 0 else 0
                x = col * spacing_x + offset_x + 40
                y = row * spacing_y + 60
                peg = QGraphicsEllipseItem(x, y, 10, 10)
                peg.setBrush(Qt.black)
                self.scene.addItem(peg)
                self.pegs.append(peg)

        slot_width = 58
        for i, label in enumerate(self.reward_labels):
            slot = QGraphicsRectItem(i * slot_width + 40, 700, slot_width - 4, 60)
            slot.setBrush(QColor("lightblue"))
            self.scene.addItem(slot)
            self.slots.append((slot, label))

    def drop_chip(self, player_name, chip_color):
        chip = QGraphicsEllipseItem(285, 0, 20, 20)
        chip.setBrush(QColor(chip_color))
        self.scene.addItem(chip)
        self.animate_chip(chip, player_name)

    def animate_chip(self, chip, player_name):
        def step():
            y = chip.y() + 10
            jitter = random.randint(-10, 10)
            x = chip.x() + jitter
            chip.setPos(x, y)
            self.bounce_sound.play()
            if y >= 700:
                QTimer.singleShot(100, lambda: self.resolve_chip(chip, player_name))
                timer.stop()

        timer = QTimer()
        timer.timeout.connect(step)
        timer.start(50)

    def resolve_chip(self, chip, player_name):
        chip_center_x = chip.x() + 10
        slot_width = 58
        slot_index = int((chip_center_x - 40) // slot_width)
        if 0 <= slot_index < len(self.slots):
            label = self.slots[slot_index][1]
            result = f"{player_name} landed on: {label}"
        else:
            result = f"{player_name} missed the slots!"
        self.land_sound.play()
        if self.parent():
            self.parent().display_result(result) 