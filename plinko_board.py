import random
from PySide6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsRectItem, QGraphicsSimpleTextItem
)
from PySide6.QtCore import Qt, QTimer, QUrl, QRectF, QPointF
from PySide6.QtGui import QColor, QBrush, QPen, QFont, QLinearGradient, QMouseEvent
from PySide6.QtMultimedia import QSoundEffect
from utils.physics import PlinkoPhysics

class PlinkoBoard(QGraphicsView):
    def __init__(self, reward_labels, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        # Set 16:9 vertical aspect ratio (e.g., 720x1280)
        self.setMinimumSize(360, 640)
        self.setFixedSize(720, 1280)
        self.pegs = []
        self.peg_positions = []
        self.slots = []
        self.reward_labels = reward_labels
        self.bounce_sound = QSoundEffect()
        self.bounce_sound.setSource(QUrl.fromLocalFile("assets/bounce.wav"))
        self.land_sound = QSoundEffect()
        self.land_sound.setSource(QUrl.fromLocalFile("assets/land.wav"))
        self.init_board()
        self.dragging_chip = None
        self.drag_start_pos = None
        self.chip_ready = False
        self.chip_color = "#ff00de"
        self.setMouseTracking(True)

    def resizeEvent(self, event):
        # Maintain 16:9 vertical aspect ratio
        w = self.width()
        h = int(w * 16 / 9)
        if h != self.height():
            self.setFixedSize(w, h)
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
        self.peg_positions = []
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
        peg_d = min(spacing_x, spacing_y) / 8  # 1/4 the previous (was /2, then /4, now /8)
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
                self.peg_positions.append((x + peg_d/2, y + peg_d/2, peg_d/2))
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
        # Place draggable chip at the top center
        self.chip_ready = True
        self.chip_color = getattr(self, 'chip_color', "#ff00de")
        self.create_draggable_chip()

    def create_draggable_chip(self):
        w = self.viewport().width()
        chip_d = min(w / 20, 30)
        chip = QGraphicsEllipseItem(w / 2 - chip_d / 2, 0, chip_d, chip_d)
        chip.setPen(self.neon_pen("#ff00de", width=5))
        chip.setBrush(self.neon_brush(self.chip_color, glow=0.8))
        chip.setFlag(QGraphicsEllipseItem.ItemIsMovable, True)
        chip.setFlag(QGraphicsEllipseItem.ItemIsSelectable, True)
        chip.setZValue(10)
        self.scene.addItem(chip)
        self.dragging_chip = chip
        self.chip_start_y = 0

    def mousePressEvent(self, event: QMouseEvent):
        if not self.chip_ready:
            return
        pos = self.mapToScene(event.pos())
        if self.dragging_chip and self.dragging_chip.contains(self.dragging_chip.mapFromScene(pos)):
            self.drag_start_pos = pos
            self.chip_drag_offset = pos.x() - self.dragging_chip.x()
            self.chip_dragging = True
        else:
            self.chip_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        if getattr(self, 'chip_dragging', False) and self.dragging_chip:
            pos = self.mapToScene(event.pos())
            w = self.viewport().width()
            chip_d = self.dragging_chip.rect().width()
            # Restrict to top row
            y = self.chip_start_y
            x = min(max(pos.x() - self.chip_drag_offset, 0), w - chip_d)
            self.dragging_chip.setPos(x, y)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if getattr(self, 'chip_dragging', False) and self.dragging_chip:
            self.chip_dragging = False
            # Start drop from current x
            self.chip_ready = False
            chip = self.dragging_chip
            self.dragging_chip = None
            self.start_chip_drop(chip)
        super().mouseReleaseEvent(event)

    def start_chip_drop(self, chip):
        h = self.viewport().height()
        w = self.viewport().width()
        self.physics = PlinkoPhysics(self.pegs, self.peg_positions, h, w)
        self.physics.reset()
        self.anim_y = chip.y()
        self.anim_chip = chip
        self.anim_player = getattr(self, 'current_player', 'Player')
        self.anim_step = 0
        self.anim_max_steps = random.randint(180, 600)  # 3-10 seconds at 60 FPS
        self.anim_timer = QTimer()
        self.anim_timer.timeout.connect(self._chip_step_with_realistic_bounce)
        self.anim_timer.start(1000 // 60)  # 60 FPS

    def _chip_step_with_realistic_bounce(self):
        chip = self.anim_chip
        w = self.viewport().width()
        h = self.viewport().height()
        chip_d = chip.rect().width()
        self.anim_step += 1
        chip_x, chip_y, hit_peg, vy = self.physics.next_bounce(
            chip.x(), self.anim_y, chip_d, self.anim_step, self.anim_max_steps
        )
        chip.setX(chip_x)
        chip.setY(chip_y)
        self.anim_y = chip_y
        if hit_peg:
            self.bounce_sound.play()
        # Land
        if self.anim_y >= h - h / 13 * 1.2 or self.anim_step >= self.anim_max_steps:
            QTimer.singleShot(120, lambda: self.resolve_chip(chip, self.anim_player))
            self.anim_timer.stop()

    def drop_chip(self, player_name, chip_color):
        # For programmatic drops (e.g., from main window)
        self.chip_color = chip_color
        self.current_player = player_name
        self.chip_ready = True
        self.init_board()

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
        parent = self.parent()
        if parent and hasattr(parent, 'display_result'):
            parent.display_result(result) 