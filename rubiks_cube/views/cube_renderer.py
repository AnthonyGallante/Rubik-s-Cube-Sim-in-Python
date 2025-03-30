import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import math
import time
from ..models.cube_model import COLOR_MAP, FACE_AXES

class CubeRenderer:
    """
    Handles the 3D rendering of the Rubik's Cube using OpenGL.
    Provides Nintendo 64 style low-poly rendering.
    """
    def __init__(self, cube_model):
        """Initialize the renderer with a reference to the cube model."""
        self.cube_model = cube_model
        
        # Camera/view parameters
        self.rotation_x = 30.0  # Initial camera angles
        self.rotation_y = 45.0
        self.distance = 15.0    # Camera distance
        
        # Animation parameters
        self.animation_start_time = 0
        self.animation_duration = 0.5  # seconds per move
        self.current_animation = None
        
        # Cube piece size
        self.cube_size = 1.0
        
        # Nintendo 64 style parameters
        self.shading_intensity = 0.7  # Reduced shading for a flatter look
        self.edge_width = 2.0         # Width of the black outlines
        self.low_poly = True          # Enable low-poly style
    
    def init_gl(self, width, height):
        """Initialize OpenGL settings."""
        try:
            # Clear color to dark gray background
            glClearColor(0.12, 0.12, 0.12, 1.0)
            
            # Enable depth testing
            glEnable(GL_DEPTH_TEST)
            glDepthFunc(GL_LESS)
            
            # Enable basic lighting
            glEnable(GL_LIGHTING)
            glEnable(GL_LIGHT0)
            glEnable(GL_COLOR_MATERIAL)
            
            # Light position and properties
            glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])
            glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
            glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.8, 0.8, 0.8, 1.0])
            
            # Set up viewport
            self.resize_gl(width, height)
            return True
        except Exception as e:
            print(f"OpenGL initialization error in renderer: {e}")
            return False
    
    def resize_gl(self, width, height):
        """Handle window resize events."""
        if height == 0:
            height = 1
            
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(45.0, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
    
    def start_animation(self, face, direction):
        """Start an animation for rotating a face."""
        if not self.cube_model.animating:
            self.cube_model.animating = True
            self.animation_start_time = time.time()
            self.current_animation = (face, direction)
            return True
        return False
    
    def update_animation(self):
        """Update the current animation state."""
        if not self.cube_model.animating or self.current_animation is None:
            return False
            
        elapsed = time.time() - self.animation_start_time
        progress = min(elapsed / self.animation_duration, 1.0)
        
        # If animation is complete
        if progress >= 1.0:
            face, direction = self.current_animation
            
            print(f"Animation complete for face {face}, direction {direction}")
            
            # Reset animation state first
            self.cube_model.animating = False
            self.current_animation = None
            
            # Now directly apply the rotation to the model
            self.cube_model.rotate_face(face, direction)
            
            return True
            
        return False
    
    def draw(self):
        """Render the 3D cube."""
        try:
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            
            glLoadIdentity()
            
            # Position camera
            gluLookAt(
                0, 0, self.distance,  # Eye position
                0, 0, 0,              # Target
                0, 1, 0               # Up vector
            )
            
            # Apply user rotation
            glRotatef(self.rotation_x, 1.0, 0.0, 0.0)
            glRotatef(self.rotation_y, 0.0, 1.0, 0.0)
            
            # If there's an active animation, calculate intermediate state
            if self.cube_model.animating and self.current_animation is not None:
                face, direction = self.current_animation
                elapsed = time.time() - self.animation_start_time
                progress = min(elapsed / self.animation_duration, 1.0)
                
                # Draw animated rotation
                self._draw_animated_cube(face, direction, progress)
            else:
                # Draw normal cube
                self._draw_cube()
        except Exception as e:
            print(f"Error during OpenGL rendering: {e}")
    
    def _draw_cube(self):
        """Draw the complete cube in its current state."""
        # Get cubies state
        cubies = self.cube_model.get_state()
        
        # Draw each cubie
        for pos, cubie in cubies.items():
            self._draw_cubie(cubie)
    
    def _draw_animated_cube(self, face, direction, progress):
        """Draw the cube during animation."""
        # Get cubies state
        cubies = self.cube_model.get_state()
        
        # Get the axis and sign for this face
        axis, sign = FACE_AXES[face]
        
        # Get the angle of rotation based on progress
        # Reverse direction for Right and Left faces (indices 2 and 3)
        if face in [4, 5]:  # Right or Left face
            angle = 90.0 * progress * -direction  # Reverse the direction
        else:
            angle = 90.0 * progress * direction
        
        # Determine rotation axis vector
        rotation_axis = [0, 0, 0]
        rotation_axis[axis] = sign
        
        # Draw cubies with appropriate transforms
        for pos, cubie in cubies.items():
            glPushMatrix()
            
            # If this cubie is on the rotating face, apply rotation
            if pos[axis] == sign:
                # Set up rotation around the appropriate axis
                x_axis, y_axis, z_axis = rotation_axis
                glRotatef(angle, x_axis, y_axis, z_axis)
            
            # Draw the cubie
            self._draw_cubie(cubie)
            
            glPopMatrix()
    
    def _draw_cubie(self, cubie):
        """Draw a single cubie."""
        glPushMatrix()
        
        # Position this cubie
        glTranslatef(cubie.x * self.cube_size, cubie.y * self.cube_size, cubie.z * self.cube_size)
        
        # Scale slightly smaller to create separation between cubies
        scale = 0.95
        glScalef(scale, scale, scale)
        
        # Draw each colored face
        face_normals = {
            "x+": (1, 0, 0),   # Right
            "x-": (-1, 0, 0),  # Left
            "y+": (0, 1, 0),   # Front
            "y-": (0, -1, 0),  # Back
            "z+": (0, 0, 1),   # Top
            "z-": (0, 0, -1)   # Bottom
        }
        
        # Draw each face if it has a color
        for face_key, color in cubie.colors.items():
            if color is not None:
                nx, ny, nz = face_normals[face_key]
                self._draw_face(nx, ny, nz, color)
        
        # Draw black frame around the cubie
        if self.low_poly:
            glDisable(GL_LIGHTING)
            glColor3f(0.0, 0.0, 0.0)
            glLineWidth(self.edge_width)
            
            # Draw wireframe
            glBegin(GL_LINES)
            # Front face
            glVertex3f(-0.5, -0.5, -0.5)
            glVertex3f(0.5, -0.5, -0.5)
            glVertex3f(0.5, -0.5, -0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(-0.5, -0.5, -0.5)
            
            # Back face
            glVertex3f(-0.5, -0.5, 0.5)
            glVertex3f(0.5, -0.5, 0.5)
            glVertex3f(0.5, -0.5, 0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glVertex3f(-0.5, -0.5, 0.5)
            
            # Connecting lines
            glVertex3f(-0.5, -0.5, -0.5)
            glVertex3f(-0.5, -0.5, 0.5)
            glVertex3f(0.5, -0.5, -0.5)
            glVertex3f(0.5, -0.5, 0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glEnd()
            
            glEnable(GL_LIGHTING)
            
        glPopMatrix()
    
    def _draw_face(self, nx, ny, nz, color):
        """Draw a single face with the specified normal and color."""
        # Get RGB color from color index
        r, g, b = COLOR_MAP[color]
        
        # Adjust for N64 style flat shading
        shade = 1.0
        if self.low_poly:
            # Simplified Lambert shading for N64 style
            light_dir = np.array([0.5, 0.5, 0.5])
            light_dir = light_dir / np.linalg.norm(light_dir)
            normal = np.array([nx, ny, nz])
            if np.linalg.norm(normal) > 0:
                normal = normal / np.linalg.norm(normal)
            dot = abs(np.dot(normal, light_dir))
            shade = self.shading_intensity + (1.0 - self.shading_intensity) * dot
        
        glColor3f(r * shade, g * shade, b * shade)
        
        # Draw the face as a quad
        glBegin(GL_QUADS)
        glNormal3f(nx, ny, nz)
        
        # Determine which plane to draw on based on the normal
        if nx == 1:    # Right face (+X)
            glVertex3f(0.5, -0.5, -0.5)
            glVertex3f(0.5, -0.5, 0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(0.5, 0.5, -0.5)
        elif nx == -1:  # Left face (-X)
            glVertex3f(-0.5, -0.5, -0.5)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glVertex3f(-0.5, -0.5, 0.5)
        elif ny == 1:   # Front face (+Y)
            glVertex3f(-0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(-0.5, 0.5, 0.5)
        elif ny == -1:  # Back face (-Y)
            glVertex3f(-0.5, -0.5, -0.5)
            glVertex3f(-0.5, -0.5, 0.5)
            glVertex3f(0.5, -0.5, 0.5)
            glVertex3f(0.5, -0.5, -0.5)
        elif nz == 1:   # Top face (+Z)
            glVertex3f(-0.5, -0.5, 0.5)
            glVertex3f(-0.5, 0.5, 0.5)
            glVertex3f(0.5, 0.5, 0.5)
            glVertex3f(0.5, -0.5, 0.5)
        elif nz == -1:  # Bottom face (-Z)
            glVertex3f(-0.5, -0.5, -0.5)
            glVertex3f(0.5, -0.5, -0.5)
            glVertex3f(0.5, 0.5, -0.5)
            glVertex3f(-0.5, 0.5, -0.5)
        
        glEnd()
    
    def rotate_view(self, dx, dy):
        """Rotate the view based on mouse movement."""
        self.rotation_y += dx * 0.5
        self.rotation_x += dy * 0.5
        
        # Limit vertical rotation to avoid the cube flipping
        self.rotation_x = max(-90, min(90, self.rotation_x))
        
    def zoom(self, amount):
        """Adjust the camera distance based on scroll wheel."""
        self.distance = max(5.0, min(25.0, self.distance - amount)) 