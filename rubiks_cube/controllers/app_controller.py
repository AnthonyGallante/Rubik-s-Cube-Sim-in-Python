import time
import random
import logging
from ..models.cube_model import CubeModel, FACE_AXES

class AppController:
    """
    Controller that manages the interaction between the model and view.
    """
    def __init__(self, use_fallback=False):
        """Initialize the controller."""
        self.use_fallback = use_fallback
        self.cube_model = CubeModel()
        self.view = None  # Will be set when create_gui is called
        self.animation_speed = 0.5  # seconds per rotation
        
        # Set up logging
        logging.basicConfig(level=logging.INFO, 
                           format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger('RubiksCube')
    
    def create_gui(self, root):
        """Create the appropriate GUI based on availability."""
        if self.use_fallback:
            from ..views.fallback_renderer import create_fallback_gui
            self.view = create_fallback_gui(root)
            self.logger.info("Using fallback GUI (2D Tkinter)")
        else:
            try:
                from ..views.cube_renderer import CubeRenderer
                self.view = CubeRenderer(root, self.cube_model)
                self.logger.info("Using 3D OpenGL renderer")
            except ImportError as e:
                self.logger.warning(f"OpenGL renderer unavailable: {e}")
                from ..views.fallback_renderer import create_fallback_gui
                self.view = create_fallback_gui(root)
                self.logger.info("Falling back to 2D Tkinter GUI")
        
        return self.view
    
    def rotate_face(self, face_idx, direction):
        """
        Rotate a face of the cube.
        
        Args:
            face_idx: Index of the face to rotate (0-5)
            direction: 1 for clockwise, -1 for counterclockwise
        """
        if self.is_animating():
            return
        
        # Convert face index to axis and sign
        axis, sign = FACE_AXES[face_idx]
        
        self.logger.info(f"Rotating face {face_idx}: axis={axis}, sign={sign}, direction={direction}")
        self.cube_model.rotate_face(face_idx, direction)
        
        # Update the view
        if hasattr(self.view, 'update'):
            self.view.update()
    
    def reset_cube(self):
        """Reset the cube to solved state."""
        self.logger.info("Resetting cube to solved state")
        self.cube_model = CubeModel()
        
        # Update the view
        if hasattr(self.view, 'set_cube_model'):
            self.view.set_cube_model(self.cube_model)
        elif hasattr(self.view, 'cube_model'):
            self.view.cube_model = self.cube_model
            
        if hasattr(self.view, 'update'):
            self.view.update()
    
    def randomize_cube(self, num_moves=20):
        """
        Randomize the cube with random moves.
        
        Args:
            num_moves: Number of random moves to apply
        """
        self.logger.info(f"Randomizing cube with {num_moves} moves")
        
        # Store history of moves for potential revert
        original_model = self.cube_model
        
        try:
            self.cube_model.randomize(num_moves)
            
            # Update the view
            if hasattr(self.view, 'update'):
                self.view.update()
        except Exception as e:
            self.logger.error(f"Error during randomization: {e}")
            self.cube_model = original_model
            
            if hasattr(self.view, 'set_cube_model'):
                self.view.set_cube_model(self.cube_model)
            elif hasattr(self.view, 'cube_model'):
                self.view.cube_model = self.cube_model
                
            if hasattr(self.view, 'update'):
                self.view.update()
    
    def solve_cube(self):
        """
        Solve the cube automatically.
        This is a placeholder for now, it will just reset the cube.
        """
        self.logger.info("Solving cube (currently just resets to solved state)")
        self.reset_cube()
    
    def is_animating(self):
        """Check if any animation is currently in progress."""
        return self.cube_model.animating
    
    def set_animation_speed(self, speed):
        """
        Set the animation speed.
        
        Args:
            speed: Animation speed in seconds per rotation (0.1 to 2.0)
        """
        self.animation_speed = max(0.1, min(2.0, speed))
        self.logger.info(f"Animation speed set to {self.animation_speed}")
        
        # Update renderer if available
        if hasattr(self.view, 'set_animation_speed'):
            self.view.set_animation_speed(self.animation_speed)
    
    def shutdown(self):
        """Clean up resources before shutting down."""
        self.logger.info("Shutting down application")
        if hasattr(self.view, 'cleanup'):
            self.view.cleanup() 