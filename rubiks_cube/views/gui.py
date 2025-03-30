import tkinter as tk
from tkinter import ttk
import sys
from OpenGL import GL
from PIL import Image, ImageTk
import numpy as np
from pyopengltk import OpenGLFrame
from ..models.cube_model import CubeModel
from .cube_renderer import CubeRenderer

# Dark theme colors
DARK_BG = "#1e1e1e"
DARKER_BG = "#121212"
ACCENT = "#3a8ee6"
TEXT_COLOR = "#ffffff"
BUTTON_BG = "#333333"
BUTTON_ACTIVE = "#444444"
BORDER_COLOR = "#555555"
FRAME_BG = "#222222"

class RubiksCubeGUI:
    """Main GUI class for the Rubik's Cube application."""
    def __init__(self, root):
        """Initialize the GUI with the root Tkinter window."""
        self.root = root
        self.root.title("Rubik's Cube Simulator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Apply dark theme
        self._apply_dark_theme()
        
        # Create model
        self.cube_model = CubeModel()
        
        # Create main frame
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the OpenGL frame for rendering
        self.gl_frame = CubeGLFrame(self.main_frame, self.cube_model, width=600, height=500)
        self.gl_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create control panel frame
        self.control_frame = ttk.Frame(self.main_frame, padding=10)
        self.control_frame.pack(fill=tk.X, expand=False, pady=(0, 10))
        
        # Create and arrange the control buttons
        self._create_control_buttons()
        
        # Handle window close event
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # Start the animation loop
        self._animation_loop()
        
    def _apply_dark_theme(self):
        """Apply dark theme to all GUI elements."""
        self.root.configure(bg=DARK_BG)
        
        # Create custom styles
        style = ttk.Style()
        style.theme_use('default')
        
        # Configure TFrame
        style.configure('TFrame', background=DARK_BG)
        
        # Configure TButton
        style.configure('TButton', 
                         background=BUTTON_BG, 
                         foreground=TEXT_COLOR, 
                         borderwidth=1, 
                         focusthickness=1, 
                         focuscolor=ACCENT,
                         padding=5)
        style.map('TButton', 
                   background=[('active', BUTTON_ACTIVE), ('pressed', ACCENT)])
        
        # Configure special buttons
        style.configure('Accent.TButton', background=ACCENT)
        style.map('Accent.TButton', 
                   background=[('active', '#4a9ef6'), ('pressed', '#2a7ed6')])
    
    def _create_control_buttons(self):
        """Create and arrange all control buttons."""
        # Left control panel (for face rotations)
        self.face_frame = ttk.LabelFrame(self.control_frame, text="Face Controls", padding=10)
        self.face_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Define face rotation buttons with labels and commands
        # Using standard cube notation: U (top), D (bottom), F (front), B (back), L (left), R (right)
        # CW = clockwise, CCW = counter-clockwise
        face_buttons = [
            ("Top CW", lambda: self._rotate_face(0, 1)),      # U - White face
            ("Top CCW", lambda: self._rotate_face(0, -1)),    # U' - White face
            ("Bottom CW", lambda: self._rotate_face(1, 1)),   # D - Yellow face 
            ("Bottom CCW", lambda: self._rotate_face(1, -1)), # D' - Yellow face
            ("Front CW", lambda: self._rotate_face(2, 1)),    # F - Red face
            ("Front CCW", lambda: self._rotate_face(2, -1)),  # F' - Red face
            ("Back CW", lambda: self._rotate_face(3, 1)),     # B - Orange face
            ("Back CCW", lambda: self._rotate_face(3, -1)),   # B' - Orange face
            ("Left CW", lambda: self._rotate_face(4, 1)),     # L - Blue face
            ("Left CCW", lambda: self._rotate_face(4, -1)),   # L' - Blue face
            ("Right CW", lambda: self._rotate_face(5, 1)),    # R - Green face
            ("Right CCW", lambda: self._rotate_face(5, -1)),  # R' - Green face
        ]
        
        # Create a grid of buttons (4 rows x 3 columns)
        for i, (text, command) in enumerate(face_buttons):
            row = i // 3
            col = i % 3
            ttk.Button(self.face_frame, text=text, command=command).grid(
                row=row, column=col, padx=5, pady=5, sticky="nsew"
            )
        
        # Configure grid weights
        for i in range(4):
            self.face_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):
            self.face_frame.grid_columnconfigure(i, weight=1)
        
        # Right control panel (for view and special operations)
        self.view_frame = ttk.LabelFrame(self.control_frame, text="View Controls", padding=10)
        self.view_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        # Camera rotation buttons
        camera_frame = ttk.Frame(self.view_frame)
        camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(camera_frame, text="↑", command=lambda: self._rotate_view(0, -10)).grid(row=0, column=1)
        ttk.Button(camera_frame, text="←", command=lambda: self._rotate_view(-10, 0)).grid(row=1, column=0)
        ttk.Button(camera_frame, text="→", command=lambda: self._rotate_view(10, 0)).grid(row=1, column=2)
        ttk.Button(camera_frame, text="↓", command=lambda: self._rotate_view(0, 10)).grid(row=2, column=1)
        
        # Configure grid for camera buttons
        for i in range(3):
            camera_frame.grid_rowconfigure(i, weight=1)
            camera_frame.grid_columnconfigure(i, weight=1)
        
        # Special operations buttons
        ttk.Button(self.view_frame, text="Reset View", command=self._reset_view).pack(fill=tk.X, pady=5)
        ttk.Button(self.view_frame, text="Reset Cube", command=self._reset_cube).pack(fill=tk.X, pady=5)
        ttk.Button(self.view_frame, style='Accent.TButton', text="Randomize", command=self._randomize_cube).pack(fill=tk.X, pady=5)
        ttk.Button(self.view_frame, style='Accent.TButton', text="Solve", command=self._solve_cube).pack(fill=tk.X, pady=5)
    
    def _rotate_face(self, face, direction):
        """Rotate a face of the cube."""
        if not self.cube_model.animating:
            # Start the animation - the actual cube update will happen when animation completes
            if self.gl_frame.renderer.start_animation(face, direction):
                # We don't need to record the move here because cube_model.rotate_face will do it
                # when the animation completes
                return True
        return False
    
    def _rotate_view(self, dx, dy):
        """Rotate the 3D view of the cube."""
        self.gl_frame.renderer.rotate_view(dx, dy)
    
    def _reset_view(self):
        """Reset the view to the default camera angle."""
        self.gl_frame.renderer.rotation_x = 30.0
        self.gl_frame.renderer.rotation_y = 45.0
        self.gl_frame.renderer.distance = 15.0
    
    def _reset_cube(self):
        """Reset the cube to its solved state."""
        if not self.cube_model.animating:
            self.cube_model = CubeModel()
            self.gl_frame.set_cube_model(self.cube_model)
    
    def _randomize_cube(self):
        """Randomize the cube with random moves."""
        if not self.cube_model.animating:
            self.cube_model.randomize(20)
    
    def _solve_cube(self):
        """Solve the cube with an algorithm."""
        if not self.cube_model.animating:
            # Get solution moves
            solution = self.cube_model.get_solution()
            
            # Start solving animation
            self._animate_solution(solution)
    
    def _animate_solution(self, moves, index=0):
        """Animate the solution moves one by one."""
        if index >= len(moves) or self.cube_model.animating:
            return
            
        # Get next move
        face, direction = moves[index]
        
        # Start animation
        self.gl_frame.renderer.start_animation(face, direction)
        
        # Schedule next move after current animation completes
        self.root.after(int(self.gl_frame.renderer.animation_duration * 1000) + 100, 
                       lambda: self._animate_solution(moves, index + 1))
    
    def _animation_loop(self):
        """Main animation loop to update the OpenGL display."""
        try:
            # Update animation state
            self.gl_frame.renderer.update_animation()
            
            # Only redraw if the frame is visible and initialized
            if hasattr(self.gl_frame, 'init_done') and self.gl_frame.init_done:
                self.gl_frame.redraw()
        except Exception as e:
            print(f"Animation loop error: {e}")
        
        # Schedule the next update
        self.root.after(16, self._animation_loop)  # ~60 FPS
    
    def _on_close(self):
        """Handle window close event."""
        self.root.quit()
        self.root.destroy()
        sys.exit()


class CubeGLFrame(OpenGLFrame):
    """Custom OpenGL frame for rendering the Rubik's Cube."""
    def __init__(self, parent, cube_model, **kwargs):
        """Initialize the OpenGL frame with the cube model."""
        super().__init__(parent, **kwargs)
        
        # Store reference to the cube model
        self.cube_model = cube_model
        
        # Create renderer
        self.renderer = CubeRenderer(self.cube_model)
        
        # Track initialization state
        self.init_done = False
        
        # Mouse tracking for rotation
        self.bind("<ButtonPress-1>", self._on_mouse_press)
        self.bind("<B1-Motion>", self._on_mouse_drag)
        self.bind("<MouseWheel>", self._on_mouse_wheel)  # Windows
        self.bind("<Button-4>", lambda e: self._on_mouse_wheel(e, 1))  # Linux scroll up
        self.bind("<Button-5>", lambda e: self._on_mouse_wheel(e, -1))  # Linux scroll down
        
        self.last_x = 0
        self.last_y = 0
    
    def initgl(self):
        """Initialize OpenGL context."""
        try:
            self.renderer.init_gl(self.width, self.height)
            self.init_done = True
            print("OpenGL initialized successfully")
        except Exception as e:
            print(f"OpenGL initialization error: {e}")
            self.init_done = False
    
    def redraw(self):
        """Redraw the OpenGL scene."""
        if not self.init_done:
            return
            
        try:
            self.tkMakeCurrent()
            self.renderer.draw()
            self.tkSwapBuffers()
        except Exception as e:
            print(f"Redraw error: {e}")
    
    def set_cube_model(self, cube_model):
        """Update the cube model reference."""
        self.cube_model = cube_model
        self.renderer.cube_model = cube_model
    
    def _on_mouse_press(self, event):
        """Handle mouse press for rotation."""
        self.last_x = event.x
        self.last_y = event.y
    
    def _on_mouse_drag(self, event):
        """Handle mouse drag for rotation."""
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        self.renderer.rotate_view(dx, dy)
        
        self.last_x = event.x
        self.last_y = event.y
    
    def _on_mouse_wheel(self, event, direction=None):
        """Handle mouse wheel for zoom."""
        if direction is None:
            # Windows
            direction = 1 if event.delta > 0 else -1
        
        self.renderer.zoom(direction)


def main():
    """Main function to start the application."""
    root = tk.Tk()
    app = RubiksCubeGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 