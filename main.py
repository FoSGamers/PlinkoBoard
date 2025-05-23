import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox, QColorDialog, QSizePolicy, QSpacerItem
)
from PySide6.QtCore import Qt, QSize
from plinko_board import PlinkoBoard

class AspectRatioWidget(QWidget):
    def __init__(self, widget, aspect_ratio=9/16, parent=None):
        super().__init__(parent)
        self.widget = widget
        self.aspect_ratio = aspect_ratio
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        self.setLayout(layout)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def resizeEvent(self, event):
        w = self.width()
        h = int(w / self.aspect_ratio)
        if h > self.height():
            h = self.height()
            w = int(h * self.aspect_ratio)
        self.widget.setFixedSize(w, h)
        super().resizeEvent(event)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FoSGamers PlinkoBoard")
        self.resize(720, 1280)
        self.setMinimumSize(360, 640)

        self.reward_labels = [
            "+5 POGs", "+10 POGs", "Vault Key", "Whiskey", "Loot Crate",
            "+20 HP", "Mystery Box", "+1 INT Buff", "+3 Ammo", "Safe Haven Map"
        ]

        self.board = PlinkoBoard(self.reward_labels, parent=self)
        self.aspect_board = AspectRatioWidget(self.board, aspect_ratio=9/16)
        self.aspect_board.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.result_label = QLabel("Drop a chip to play!")
        self.result_label.setAlignment(Qt.AlignCenter)
        self.result_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.player_input = QLineEdit()
        self.player_input.setPlaceholderText("Enter player name")
        self.player_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.color_button = QPushButton("Pick Chip Color")
        self.color_button.clicked.connect(self.pick_color)
        self.color_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.chip_color = "red"

        self.drop_button = QPushButton("Drop Chip")
        self.drop_button.clicked.connect(self.handle_drop)
        self.drop_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.save_button = QPushButton("Save Rewards Template")
        self.save_button.clicked.connect(self.save_template)
        self.save_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.load_button = QPushButton("Load Rewards Template")
        self.load_button.clicked.connect(self.load_template)
        self.load_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.drop_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)

        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.result_label)
        controls_layout.addWidget(self.player_input)
        controls_layout.addWidget(self.color_button)
        controls_layout.addLayout(button_layout)
        controls_layout.setSpacing(10)
        controls_layout.setContentsMargins(0, 0, 0, 0)

        main_layout = QVBoxLayout()
        main_layout.addWidget(self.aspect_board, stretch=2)
        main_layout.addSpacing(10)
        main_layout.addLayout(controls_layout, stretch=0)
        main_layout.addStretch(1)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def handle_drop(self):
        name = self.player_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Missing Name", "Please enter a player name.")
            return
        self.board.drop_chip(name, self.chip_color)

    def pick_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.chip_color = color.name()

    def display_result(self, result):
        self.result_label.setText(result)

    def save_template(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Template", "", "JSON Files (*.json)")
        if path:
            with open(path, "w") as f:
                json.dump(self.reward_labels, f)
            QMessageBox.information(self, "Saved", "Reward template saved successfully.")

    def load_template(self):
        path, _ = QFileDialog.getOpenFileName(self, "Load Template", "", "JSON Files (*.json)")
        if path:
            try:
                with open(path, "r") as f:
                    self.reward_labels = json.load(f)
                self.board.reward_labels = self.reward_labels
                self.board.init_board()
                QMessageBox.information(self, "Loaded", "Reward template loaded.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load template: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 