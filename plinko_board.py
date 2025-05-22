import random
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsSimpleTextItem
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRectF
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient
from PySide6.QtMultimedia import QSoundEffect

class PlinkoBoard(QGraphicsView):
    def __init__(self, reward_labels, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
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

    def neon_pen(self, color, width=3):
        pen = QPen(QColor(color))
        pen.setWidth(width)
        pen.setColor(QColor(color))
        return pen

    def neon_brush(self, color, glow=0.5):
        c = QColor(color)
        c.setAlphaF(glow)
        return QBrush(c)

    def init_board(self):
        self.scene.clear()
        self.pegs = []
        self.slots = []
        w = self.viewport().width()
        h = self.viewport().height()
        self.scene.setSceneRect(0, 0, w, h)

        # Retro neon gradient background
        grad = QLinearGradient(0, 0, 0, h)
        grad.setColorAt(0, QColor(10, 10, 30))
        grad.setColorAt(1, QColor(30, 0, 40))
        self.scene.setBackgroundBrush(QBrush(grad))

        spacing_x = w / 10
        spacing_y = h / 12
        peg_d = min(spacing_x, spacing_y) / 2
        neon_colors = ["#00fff7", "#ff00de", "#39ff14", "#ffe600"]
        for row in range(8):
            for col in range(10):
                offset_x = spacing_x / 2 if row % 2 == 0 else 0
                x = col * spacing_x + offset_x + spacing_x * 0.1
                y = row * spacing_y + spacing_y * 0.8
                peg = QGraphicsEllipseItem(x, y, peg_d, peg_d)
                color = neon_colors[(row + col) % len(neon_colors)]
                peg.setPen(self.neon_pen(color, width=4))
                peg.setBrush(self.neon_brush(color, glow=0.7))
                self.scene.addItem(peg)
                self.pegs.append(peg)
        slot_width = w / 10
        slot_height = h / 13
        for i, label in enumerate(self.reward_labels):
            slot = QGraphicsRectItem(i * slot_width + spacing_x * 0.1, h - slot_height * 1.2, slot_width - spacing_x * 0.2, slot_height)
            slot.setPen(self.neon_pen("#00fff7", width=5))
            slot.setBrush(QBrush(Qt.transparent))
            self.scene.addItem(slot)
            # Neon label
            text = QGraphicsSimpleTextItem(label)
            font = QFont("Courier New", int(slot_height/3))
            font.setBold(True)
            text.setFont(font)
            text.setBrush(self.neon_brush("#ffe600", glow=1.0))
            text.setPen(self.neon_pen("#ffe600", width=2))
            text.setPos(i * slot_width + spacing_x * 0.15, h - slot_height * 1.1)
            self.scene.addItem(text)
            self.slots.append((slot, label))

    def drop_chip(self, player_name, chip_color):
        w = self.viewport().width()
        chip_d = min(w / 20, 30)
        chip = QGraphicsEllipseItem(w / 2 - chip_d / 2, 0, chip_d, chip_d)
        chip.setPen(self.neon_pen("#ff00de", width=5))
        chip.setBrush(self.neon_brush(chip_color, glow=0.8))
        self.scene.addItem(chip)
        self.animate_chip(chip, player_name)

    def animate_chip(self, chip, player_name):
        self.anim_y = chip.y()
        self.anim_vy = 0
        self.anim_bounces = 0
        self.anim_max_bounces = 8
        self.anim_chip = chip
        self.anim_player = player_name
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._chip_step)
        self.anim_timer.start(18)

    def _chip_step(self):
        chip = self.anim_chip
        w = self.viewport().width()
        h = self.viewport().height()
        chip_d = chip.rect().width()
        gravity = h / 400
        self.anim_vy += gravity
        self.anim_y += self.anim_vy
        # Neon jitter
        jitter = random.uniform(-0.7, 0.7) * (w / 200)
        chip.setPos(chip.x() + jitter, self.anim_y)
        self.bounce_sound.play()
        # Simulate bounce
        if self.anim_bounces < self.anim_max_bounces and random.random() < 0.13:
            self.anim_vy = -abs(self.anim_vy) * random.uniform(0.2, 0.5)
            self.anim_bounces += 1
        # Land
        if self.anim_y >= h - h / 13 * 1.2:
            QTimer.singleShot(120, lambda: self.resolve_chip(chip, self.anim_player))
            self.anim_timer.stop()

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