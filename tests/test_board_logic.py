import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from plinko_board import PlinkoBoard
from PySide6.QtWidgets import QApplication

app = QApplication.instance() or QApplication([])

def test_board_initialization():
    rewards = [str(i) for i in range(10)]
    board = PlinkoBoard(rewards)
    assert len(board.pegs) == 8 * 10
    assert len(board.slots) == 10
    assert all(label == str(i) for i, (slot, label) in enumerate(board.slots)) 