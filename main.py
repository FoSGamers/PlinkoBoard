import sys
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel,
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QFileDialog, QMessageBox, QColorDialog
)
from PySide6.QtCore import Qt
from plinko_board import PlinkoBoard

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FoSGamers PlinkoBoard")
        self.setFixedSize(620, 1000)

        self.reward_labels = [
            "+5 POGs", "+10 POGs", "Vault Key", "Whiskey", "Loot Crate",
            "+20 HP", "Mystery Box", "+1 INT Buff", "+3 Ammo", "Safe Haven Map"
        ]

        self.board = PlinkoBoard(self.reward_labels, parent=self)

        self.result_label = QLabel("Drop a chip to play!")
        self.result_label.setAlignment(Qt.AlignCenter)

        self.player_input = QLineEdit()
        self.player_input.setPlaceholderText("Enter player name")

        self.color_button = QPushButton("Pick Chip Color")
        self.color_button.clicked.connect(self.pick_color)
        self.chip_color = "red"

        self.drop_button = QPushButton("Drop Chip")
        self.drop_button.clicked.connect(self.handle_drop)

        self.save_button = QPushButton("Save Rewards Template")
        self.save_button.clicked.connect(self.save_template)

        self.load_button = QPushButton("Load Rewards Template")
        self.load_button.clicked.connect(self.load_template)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.drop_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.load_button)

        layout = QVBoxLayout()
        layout.addWidget(self.board)
        layout.addWidget(self.result_label)
        layout.addWidget(self.player_input)
        layout.addWidget(self.color_button)
        layout.addLayout(button_layout)

        container = QWidget()
        container.setLayout(layout)
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