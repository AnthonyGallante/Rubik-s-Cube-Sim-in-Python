import numpy as np
from copy import deepcopy

# Define colors using 3D coordinate system
# Colors are defined by their position relative to the cube center
WHITE = 0   # +Z (top)
YELLOW = 1  # -Z (bottom)
RED = 2     # +X (right)
ORANGE = 3  # -X (left)
BLUE = 4    # +Y (front)
GREEN = 5   # -Y (back)

# Color to RGB mapping
COLOR_MAP = {
    WHITE: (1.0, 1.0, 1.0),   # White
    YELLOW: (1.0, 1.0, 0.0),  # Yellow
    RED: (1.0, 0.0, 0.0),     # Red
    ORANGE: (1.0, 0.5, 0.0),  # Orange
    BLUE: (0.0, 0.0, 1.0),    # Blue
    GREEN: (0.0, 1.0, 0.0)    # Green
}

# Face to axis mapping
# Each face is defined by an axis and a direction (positive or negative)
FACE_AXES = {
    0: (2, 1),    # +Z (top/white)
    1: (2, -1),   # -Z (bottom/yellow)
    2: (0, 1),    # +X (right/red)
    3: (0, -1),   # -X (left/orange)
    4: (1, 1),    # +Y (front/blue)
    5: (1, -1),   # -Y (back/green)
}

# Define which face is in which direction for easier lookup
FACE_DIRECTIONS = {
    "top": 0,     # +Z
    "bottom": 1,  # -Z
    "right": 2,   # +X
    "left": 3,    # -X
    "front": 4,   # +Y
    "back": 5,    # -Y
}

class Cubie:
    """
    Represents a single cubie (small cube) in the Rubik's Cube.
    Each cubie has a position (x, y, z) and colors on visible faces.
    """
    def __init__(self, x, y, z):
        """Initialize a cubie at the given position."""
        self.x = x  # -1, 0, or 1
        self.y = y  # -1, 0, or 1
        self.z = z  # -1, 0, or 1
        
        # Initialize colors (None means not visible)
        self.colors = {
            "x+": RED if x == 1 else None,      # Right face
            "x-": ORANGE if x == -1 else None,  # Left face
            "y+": BLUE if y == 1 else None,     # Front face
            "y-": GREEN if y == -1 else None,   # Back face
            "z+": WHITE if z == 1 else None,    # Top face
            "z-": YELLOW if z == -1 else None   # Bottom face
        }
    
    def __repr__(self):
        """String representation of the cubie."""
        return f"Cubie({self.x}, {self.y}, {self.z})"

class CubeModel:
    """
    Represents a Rubik's Cube using a 3D coordinate system.
    The cube is centered at the origin (0, 0, 0) with cubies at
    positions (x, y, z) where x, y, z ∈ {-1, 0, 1}.
    """
    def __init__(self):
        """Initialize a solved 3x3x3 Rubik's Cube."""
        # Create a 3x3x3 array to store the cubies
        self.cubies = {}
        
        # Initialize all cubies
        for x in range(-1, 2):
            for y in range(-1, 2):
                for z in range(-1, 2):
                    # Skip the center cubie (not visible)
                    if x == 0 and y == 0 and z == 0:
                        continue
                    
                    # Create a cubie at this position
                    self.cubies[(x, y, z)] = Cubie(x, y, z)
        
        # Animation properties
        self.animating = False
        self.animation_progress = 0
        
        # Keep track of move history
        self.history = []
    
    def get_state(self):
        """Return the current state of the cube."""
        return deepcopy(self.cubies)
    
    def is_solved(self):
        """Check if the cube is solved."""
        # Check each face for uniform color
        for face_idx, (axis, sign) in FACE_AXES.items():
            # Get the color of the center cubie of this face
            center_pos = [0, 0, 0]
            center_pos[axis] = sign
            center_color = None
            
            # Find which face of the center cubie is on this face
            face_key = f"{['x', 'y', 'z'][axis]}{'+' if sign > 0 else '-'}"
            
            # Get all cubies on this face
            cubies_on_face = []
            for pos, cubie in self.cubies.items():
                if pos[axis] == sign:
                    cubies_on_face.append(cubie)
                    
                    # Get the center color if this is the center cubie
                    is_center = True
                    for i in range(3):
                        if i != axis and pos[i] != 0:
                            is_center = False
                            break
                    
                    if is_center:
                        center_color = cubie.colors[face_key]
            
            # Check if all cubies on this face have the same color on this face
            for cubie in cubies_on_face:
                if cubie.colors[face_key] != center_color:
                    return False
        
        return True
    
    def rotate_face(self, face, direction=1):
        """
        Rotate a face of the cube.
        face: 0=top(+Z), 1=bottom(-Z), 2=right(+X), 3=left(-X), 4=front(+Y), 5=back(-Y)
        direction: 1=clockwise, -1=counterclockwise (as viewed from outside the cube)
        """
        if self.animating:
            return False
        
        print(f"Rotating face {face} in direction {direction}")
        
        # Record the move
        self.history.append((face, direction))
        
        # Get the axis and sign for this face
        axis, sign = FACE_AXES[face]
        
        # Get all cubies on this face
        face_cubies = {}
        for pos, cubie in self.cubies.items():
            if pos[axis] == sign:
                face_cubies[pos] = cubie
        
        # Make a copy of the cubies to update
        new_cubies = {}
        
        # Calculate new positions for cubies on this face
        for pos, cubie in face_cubies.items():
            # Determine the other two axes
            other_axes = [i for i in range(3) if i != axis]
            a1, a2 = other_axes
            
            # Calculate new position based on rotation
            # For clockwise rotation around the positive axis:
            # (x, y) -> (-y, x) for (a1, a2)
            # For counterclockwise rotation or negative axis:
            # Adjust rotation direction
            effective_dir = direction * sign
            
            new_pos = list(pos)
            if effective_dir == 1:  # Clockwise around the axis
                new_pos[a1] = -pos[a2]
                new_pos[a2] = pos[a1]
            else:  # Counterclockwise around the axis
                new_pos[a1] = pos[a2]
                new_pos[a2] = -pos[a1]
            
            new_pos = tuple(new_pos)
            
            # Create a new cubie at the new position
            new_cubie = Cubie(new_pos[0], new_pos[1], new_pos[2])
            
            # Update colors by rotating them
            self._rotate_cubie_colors(cubie, new_cubie, axis, effective_dir)
            
            # Add to the new cubies dictionary
            new_cubies[new_pos] = new_cubie
        
        # Update the cubies that weren't on the face
        for pos, cubie in self.cubies.items():
            if pos[axis] != sign:
                new_cubies[pos] = cubie
        
        # Update the cubies dictionary
        self.cubies = new_cubies
        
        return True
    
    def _rotate_cubie_colors(self, old_cubie, new_cubie, rotation_axis, direction):
        """
        Update the colors of a cubie after rotation.
        rotation_axis: 0=x, 1=y, 2=z
        direction: 1=clockwise, -1=counterclockwise
        """
        # Map face keys to axis indices
        face_to_axis = {
            "x+": (0, 1),  # +X face -> +X axis
            "x-": (0, -1), # -X face -> -X axis
            "y+": (1, 1),  # +Y face -> +Y axis
            "y-": (1, -1), # -Y face -> -Y axis
            "z+": (2, 1),  # +Z face -> +Z axis
            "z-": (2, -1)  # -Z face -> -Z axis
        }
        
        # Reverse mapping for easier lookup
        axis_to_face = {v: k for k, v in face_to_axis.items()}
        
        # Find which axes are affected by the rotation
        affected_axes = [i for i in range(3) if i != rotation_axis]
        
        # Create a mapping of old faces to new faces
        face_mapping = {}
        
        # Faces aligned with the rotation axis don't change
        for face_key, (axis, sign) in face_to_axis.items():
            if axis == rotation_axis:
                face_mapping[face_key] = face_key
        
        # Determine the new orientation of the other faces
        # This depends on the direction of rotation
        affected_faces = [face for face, (axis, _) in face_to_axis.items() if axis in affected_axes]
        
        # Get the two affected axes
        a1, a2 = affected_axes
        
        # For each affected face
        for face_key in affected_faces:
            face_axis, face_sign = face_to_axis[face_key]
            
            # Calculate the new axis and sign after rotation
            if face_axis == a1:
                if direction == 1:  # Clockwise
                    new_axis = a2
                    new_sign = face_sign
                else:  # Counterclockwise
                    new_axis = a2
                    new_sign = -face_sign
            else:  # face_axis == a2
                if direction == 1:  # Clockwise
                    new_axis = a1
                    new_sign = -face_sign
                else:  # Counterclockwise
                    new_axis = a1
                    new_sign = face_sign
            
            # Map to the new face key
            new_face_key = axis_to_face[(new_axis, new_sign)]
            face_mapping[face_key] = new_face_key
        
        # Apply the face mapping to update colors
        for old_face, new_face in face_mapping.items():
            if old_cubie.colors[old_face] is not None:
                new_cubie.colors[new_face] = old_cubie.colors[old_face]
    
    def randomize(self, num_moves=20):
        """Randomize the cube with a series of random moves."""
        if self.animating:
            return False
            
        import random
        faces = list(range(6))  # 0-5 for the six faces
        directions = [1, -1]    # 1 for clockwise, -1 for counterclockwise
        
        for _ in range(num_moves):
            face = random.choice(faces)
            direction = random.choice(directions)
            self.rotate_face(face, direction)
        
        return True
    
    def get_solution(self):
        """
        Find a solution to the current cube state.
        This is a placeholder for a real solver algorithm.
        """
        # In a real implementation, this would use an algorithm like Kociemba's
        # For now, just return the inverse of the move history
        solution = []
        for face, direction in reversed(self.history):
            solution.append((face, -direction))
        return solution
    
    def get_face_colors(self, face):
        """
        Get the colors of all cubies on a specific face.
        Returns a 3x3 grid of colors.
        """
        axis, sign = FACE_AXES[face]
        
        # Create a 3x3 grid to store the colors
        colors = np.zeros((3, 3), dtype=int)
        
        # Get the face key for this face
        face_key = f"{['x', 'y', 'z'][axis]}{'+' if sign > 0 else '-'}"
        
        # Map from 3D coordinates to 2D grid coordinates
        # The mapping depends on which face we're looking at
        coord_map = self._get_coordinate_mapping(axis, sign)
        
        # Fill the grid with colors from the cubies
        for pos, cubie in self.cubies.items():
            if pos[axis] == sign:
                # Normalize the coordinates (shift from -1,0,1 to 0,1,2)
                normalized_pos = [p + 1 for p in pos]
                
                # Map 3D position to 2D grid using the appropriate mapping
                row, col = coord_map(normalized_pos)
                
                # Set the color
                colors[row, col] = cubie.colors[face_key]
        
        return colors
    
    def _get_coordinate_mapping(self, axis, sign):
        """
        Return a function that maps 3D coordinates to 2D grid coordinates.
        The mapping depends on which face we're looking at.
        """
        # Get the other two axes
        other_axes = [i for i in range(3) if i != axis]
        a1, a2 = other_axes
        
        # Define the mapping function
        def map_func(pos):
            # Extract coordinates for the other two axes
            c1, c2 = pos[a1], pos[a2]
            
            # The mapping depends on the face and sign
            if axis == 0:  # X axis (left/right faces)
                if sign > 0:  # Right face
                    return 2 - c2, c1  # Map (y, z) to (2-z, y)
                else:  # Left face
                    return 2 - c2, 2 - c1  # Map (y, z) to (2-z, 2-y)
            elif axis == 1:  # Y axis (front/back faces)
                if sign > 0:  # Front face
                    return 2 - c2, 2 - c1  # Map (x, z) to (2-z, 2-x)
                else:  # Back face
                    return 2 - c2, c1  # Map (x, z) to (2-z, x)
            else:  # Z axis (top/bottom faces)
                if sign > 0:  # Top face
                    return c2, c1  # Map (x, y) to (y, x)
                else:  # Bottom face
                    return 2 - c2, c1  # Map (x, y) to (2-y, x)
        
        return map_func 