# PlinkoBoard (FoSGamers Edition)

A customizable, animated Plinko board app for giveaways, OBS overlays, and gaming streams.

## Features
- Animated Plinko board with pegs, chips, and reward slots
- Customizable reward slots (load/save templates)
- Player name and chip color selection
- Sound effects for bounces and landings
- Designed for OBS overlay compatibility

## Setup
1. Install requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the app:
   ```bash
   python main.py
   ```

## Project Structure
```
Plinko/
├── main.py
├── plinko_board.py
├── assets/
│   ├── bounce.wav
│   ├── land.wav
├── config/
│   └── rewards_template.json
├── tests/
│   └── test_main.py
├── requirements.txt
└── README.md
```

## Development & Contribution
- Follow best practices: commit after every change, add/maintain tests, never break existing features.
- See `tests/` for test examples.

---

Place your sound files in the `assets/` folder. Customize rewards in `config/rewards_template.json` or via the app UI. 