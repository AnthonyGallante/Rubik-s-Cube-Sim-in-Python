import tkinter as tk
from ..models.cube_model import COLOR_MAP, FACE_AXES, FACE_DIRECTIONS

class FallbackGUI:
    """
    A fallback GUI implementation using only Tkinter.
    This is used when OpenGL is not available.
    """
    def __init__(self, root):
        """Initialize the fallback GUI."""
        self.root = root
        self.root.title("Rubik's Cube Simulator (2D Fallback Mode)")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e1e")  # Dark theme background
        
        # Create the cube model
        from ..models.cube_model import CubeModel
        self.cube_model = CubeModel()
        
        # Create frames
        self.main_frame = tk.Frame(self.root, bg="#1e1e1e")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create the 2D canvas for rendering the cube
        self.canvas = tk.Canvas(self.main_frame, bg="#121212", highlightthickness=0)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create control panel
        self.controls_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        self.controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        # Create face rotation buttons
        self.create_rotation_buttons()
        
        # Special buttons
        self.create_special_buttons()
        
        # Bind window resize
        self.canvas.bind("<Configure>", self.on_resize)
        
        # Initial rendering
        self.render_cube()
        
    def create_rotation_buttons(self):
        """Create buttons for rotating the cube faces."""
        # Faces frame
        faces_frame = tk.LabelFrame(self.controls_frame, text="Face Controls", 
                                   bg="#1e1e1e", fg="white", padx=5, pady=5)
        faces_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Define the face rotation buttons
        faces = [
            ("Top CW", lambda: self.rotate_face(0, 1)),    # +Z
            ("Top CCW", lambda: self.rotate_face(0, -1)),  # +Z
            ("Bottom CW", lambda: self.rotate_face(1, 1)), # -Z
            ("Bottom CCW", lambda: self.rotate_face(1, -1)), # -Z
            ("Right CW", lambda: self.rotate_face(2, 1)),   # +X
            ("Right CCW", lambda: self.rotate_face(2, -1)), # +X
            ("Left CW", lambda: self.rotate_face(3, 1)),    # -X
            ("Left CCW", lambda: self.rotate_face(3, -1)),  # -X
            ("Front CW", lambda: self.rotate_face(4, 1)),   # +Y
            ("Front CCW", lambda: self.rotate_face(4, -1)), # +Y
            ("Back CW", lambda: self.rotate_face(5, 1)),    # -Y
            ("Back CCW", lambda: self.rotate_face(5, -1)),  # -Y
        ]
        
        # Create buttons in a grid
        row, col = 0, 0
        for text, command in faces:
            button = tk.Button(faces_frame, text=text, command=command,
                              bg="#333333", fg="white", activebackground="#444444",
                              activeforeground="white", relief=tk.FLAT)
            button.grid(row=row, column=col, padx=3, pady=3, sticky="nsew")
            
            col += 1
            if col > 2:  # 3 columns
                col = 0
                row += 1
                
        # Configure grid
        for i in range(4):  # 4 rows
            faces_frame.grid_rowconfigure(i, weight=1)
        for i in range(3):  # 3 columns
            faces_frame.grid_columnconfigure(i, weight=1)
    
    def create_special_buttons(self):
        """Create special action buttons."""
        special_frame = tk.LabelFrame(self.controls_frame, text="Actions", 
                                    bg="#1e1e1e", fg="white", padx=5, pady=5)
        special_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        # Reset button
        reset_button = tk.Button(special_frame, text="Reset Cube", 
                               command=self.reset_cube,
                               bg="#333333", fg="white", 
                               activebackground="#444444",
                               activeforeground="white", relief=tk.FLAT)
        reset_button.pack(fill=tk.X, pady=3)
        
        # Randomize button
        randomize_button = tk.Button(special_frame, text="Randomize", 
                                   command=self.randomize_cube,
                                   bg="#3a8ee6", fg="white", 
                                   activebackground="#4a9ef6",
                                   activeforeground="white", relief=tk.FLAT)
        randomize_button.pack(fill=tk.X, pady=3)
        
        # Solve button
        solve_button = tk.Button(special_frame, text="Solve", 
                               command=self.solve_cube,
                               bg="#3a8ee6", fg="white", 
                               activebackground="#4a9ef6",
                               activeforeground="white", relief=tk.FLAT)
        solve_button.pack(fill=tk.X, pady=3)
    
    def rotate_face(self, face, direction):
        """Rotate a face of the cube."""
        if not self.cube_model.animating:
            self.cube_model.rotate_face(face, direction)
            self.render_cube()
    
    def reset_cube(self):
        """Reset the cube to its solved state."""
        from ..models.cube_model import CubeModel
        self.cube_model = CubeModel()
        self.render_cube()
    
    def randomize_cube(self):
        """Randomize the cube with random moves."""
        self.cube_model.randomize(20)
        self.render_cube()
    
    def solve_cube(self):
        """Solve the cube automatically."""
        # Get solution moves
        solution = self.cube_model.get_solution()
        
        # Apply all moves instantly for simplicity
        for face, direction in solution:
            self.cube_model.rotate_face(face, direction)
        
        # Render the final state
        self.render_cube()
    
    def on_resize(self, event):
        """Handle window resize event."""
        self.render_cube()
    
    def render_cube(self):
        """Render the cube in 2D."""
        self.canvas.delete("all")
        
        # Get canvas dimensions
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # Calculate cell size for the grid
        size = min(width, height) / 12
        
        # Calculate the center of the canvas
        center_x = width / 2
        center_y = height / 2
        
        # Get colors for each face
        face_colors = {}
        for face in range(6):
            face_colors[face] = self.cube_model.get_face_colors(face)
        
        # Draw unfolded cube (like a cube net)
        # Arrangement:
        #     [0]
        # [3][4][2][5]
        #     [1]
        
        # Draw top face (index 0) - above center
        self._draw_face(face_colors[0], center_x - 1.5 * size, center_y - 4 * size, size)
        
        # Draw bottom face (index 1) - below center
        self._draw_face(face_colors[1], center_x - 1.5 * size, center_y + 1 * size, size)
        
        # Draw right face (index 2) - right of center
        self._draw_face(face_colors[2], center_x + 1.5 * size, center_y - 1.5 * size, size)
        
        # Draw left face (index 3) - left of center
        self._draw_face(face_colors[3], center_x - 4.5 * size, center_y - 1.5 * size, size)
        
        # Draw front face (index 4) - center
        self._draw_face(face_colors[4], center_x - 1.5 * size, center_y - 1.5 * size, size)
        
        # Draw back face (index 5) - right of right face
        self._draw_face(face_colors[5], center_x + 4.5 * size, center_y - 1.5 * size, size)
        
        # Add labels
        labels = ["Top", "Bottom", "Right", "Left", "Front", "Back"]
        positions = [
            (center_x, center_y - 5.5 * size),  # Top
            (center_x, center_y + 4 * size),    # Bottom
            (center_x + 3 * size, center_y),    # Right
            (center_x - 6 * size, center_y),    # Left
            (center_x, center_y),               # Front
            (center_x + 6 * size, center_y),    # Back
        ]
        
        for label, pos in zip(labels, positions):
            self.canvas.create_text(pos[0], pos[1], text=label, fill="white", font=("Arial", 10))
    
    def _draw_face(self, face_colors, x, y, size):
        """Draw a single face of the cube."""
        for row in range(3):
            for col in range(3):
                # Get the color index at this position
                color_idx = face_colors[row][col]
                
                # Convert color index to RGB hex code
                r, g, b = COLOR_MAP[color_idx]
                color = f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
                
                # Calculate position
                cell_x = x + col * size
                cell_y = y + row * size
                
                # Draw the cell
                self.canvas.create_rectangle(
                    cell_x, cell_y, 
                    cell_x + size, cell_y + size,
                    fill=color, outline="black", width=2
                )

def create_fallback_gui(root):
    """Create and return a fallback GUI instance."""
    return FallbackGUI(root) 