# Flappy Bird with Hand Gesture Control

A modern take on the classic Flappy Bird game featuring hand gesture control using MediaPipe for intuitive gameplay.

## Features

- **Hand Gesture Control**: Control the bird using hand gestures via webcam
- **Dual Hand Support**: Works with one or both hands simultaneously
- **Keyboard Fallback**: Traditional keyboard controls (Space/Up arrow)
- **Automatic Detection**: Auto-detects available camera and falls back gracefully
- **God Mode**: Immortality mode for testing
- **Audio Toggle**: Mute/unmute game sounds
- **Real-time Feedback**: Live display of hand angles on camera feed

## Installation

### Prerequisites
- Python 3.7+
- Webcam (optional, keyboard-only mode available)

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/MinhToan4/flappy-bird.git
   cd flappy-bird
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Running the Game
```bash
python main.py
```

### Controls

#### Keyboard
- **Space** or **↑**: Make bird flap
- **ESC**: Exit game

#### Hand Gestures
- Place hand(s) in front of camera
- Open hand wide (angle > 55°) to flap
- Close hand (angle < 55°) for natural fall
- Works with one or both hands

### Configuration
Edit `main.py` to customize:
- `GESTURE_THRESHOLD`: Hand angle threshold (default: 55°)
- `GOD_MODE`: Enable immortality (default: False)
- `IS_MUTED`: Mute audio (default: False)
- `FPS`: Game speed (default: 32)

## Project Structure

```
flappy-bird/
├── main.py                    # Main game file
├── utils_mediapipe.py         # MediaPipe hand tracking implementation
├── utils_mediapipe_mock.py    # Mock implementation for fallback
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── gallery/                   # Game assets
    ├── audio/                 # Sound effects
    └── sprites/               # Game sprites
```

## Troubleshooting

### MediaPipe Installation Issues
```bash
pip install mediapipe==0.10.14
```

### Camera Not Found
The game automatically switches to keyboard-only mode if no camera is detected.

### Import Errors
Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

## Technical Details

- **Hand Tracking**: MediaPipe with 21-point landmark detection
- **Game Engine**: Pygame with physics-based movement
- **Gesture Recognition**: Angle-based detection from finger joints
- **Fallback System**: Automatic mock implementation when MediaPipe unavailable

## License

This project is for educational and entertainment purposes.

## Contributing

Feel free to submit issues and enhancement requests!