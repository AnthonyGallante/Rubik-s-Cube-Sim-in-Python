# Rubik's Cube Simulator

A 3D interactive Rubik's Cube simulation with Nintendo 64 style graphics built using Python, Tkinter, and OpenGL.

https://github.com/user-attachments/assets/dd83e17a-3a29-4a41-bb21-9c81d5045a19

## Features

- 3D rendered Rubik's Cube with Nintendo 64 style low-poly graphics
- Dark-themed, responsive GUI
- Interactive controls to rotate cube faces
- View manipulation (rotate and zoom)
- Cube scrambling and automatic solving
- Smooth animations for all operations
- Input locking during animations

## Requirements

- Python 3.6+
- Tkinter (included with most Python installations)
- NumPy
- PyOpenGL
- PyOpenGL-accelerate
- pyopengltk
- Pillow (PIL)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/AnthonyGallante/rubiks-cube-simulator.git
   cd rubiks-cube-simulator
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

Run the application with:

```
python -m rubiks_cube.main
```

### Controls

#### Face Rotation Buttons
- Click on the "Top CW/CCW", "Bottom CW/CCW", etc. buttons to rotate the respective face clockwise or counterclockwise.

#### View Controls
- Arrow buttons: Rotate the camera view
- Reset View: Return to the default camera angle
- Reset Cube: Reset the cube to its solved state
- Randomize: Scramble the cube with random moves
- Solve: Automatically solve the cube

#### Mouse Controls
- Click and drag: Rotate the cube view
- Scroll wheel: Zoom in/out

## Project Structure

```
rubiks_cube/
├── models/                # Data models
│   ├── __init__.py
│   └── cube_model.py      # Cube state and logic
├── views/                 # UI components
│   ├── __init__.py
│   ├── cube_renderer.py   # OpenGL renderer
│   └── gui.py             # Tkinter UI
├── controllers/           # Application logic
│   └── __init__.py
├── utils/                 # Helper functions
│   └── __init__.py
├── __init__.py
└── main.py                # Entry point
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Inspired by Nintendo 64 era graphics and the classic Rubik's Cube puzzle
- Built using Python, Tkinter, and OpenGL 
