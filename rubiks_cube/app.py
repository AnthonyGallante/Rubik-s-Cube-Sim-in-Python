import tkinter as tk
import sys
import os
import logging
from .controllers.app_controller import AppController

def main():
    """Main entry point for the Rubik's Cube application."""
    # Set up logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger('RubiksCube')
    
    # Parse command line arguments
    use_fallback = '--fallback' in sys.argv
    debug_mode = '--debug' in sys.argv
    
    if debug_mode:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug mode enabled")
    
    # Create the main Tkinter window
    root = tk.Tk()
    root.title("Rubik's Cube Simulator")
    root.geometry("800x600")
    root.configure(bg="#1e1e1e")  # Dark theme background
    
    # Add icon if available
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(script_dir, "assets", "icon.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            root.iconphoto(True, icon)
    except Exception as e:
        logger.warning(f"Could not load application icon: {e}")
    
    # Create the application controller
    controller = AppController(use_fallback=use_fallback)
    
    # Create the UI through the controller
    gui = controller.create_gui(root)
    
    # Run the main loop
    try:
        root.mainloop()
    except Exception as e:
        logger.error(f"Error in main loop: {e}")
    finally:
        # Clean up resources
        controller.shutdown()

if __name__ == "__main__":
    main() 