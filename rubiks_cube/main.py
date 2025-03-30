#!/usr/bin/env python3
"""
Rubik's Cube Simulator
A 3D interactive Rubik's Cube simulation with Nintendo 64 style graphics.
"""

import tkinter as tk
import sys
import os

def check_dependencies():
    """Check if all required dependencies are available."""
    try:
        # Try different OpenGL backends
        backends = ['', 'egl', 'glx', 'osmesa', 'windows']
        
        # Import required packages
        import numpy
        from PIL import Image
        
        # Try to import OpenGL
        opengl_imported = False
        
        for backend in backends:
            try:
                if backend:
                    os.environ['PYOPENGL_PLATFORM'] = backend
                    print(f"Trying OpenGL backend: {backend}")
                
                from OpenGL import GL
                opengl_imported = True
                print(f"OpenGL imported successfully with backend: {backend or 'default'}")
                break
            except ImportError:
                print(f"Failed to import OpenGL with backend: {backend or 'default'}")
                continue
        
        if not opengl_imported:
            print("Error: Failed to import OpenGL with any backend")
            return False
        
        # Check if tkinter has OpenGL support
        try:
            from pyopengltk import OpenGLFrame
            print("pyopengltk imported successfully")
        except ImportError:
            print("Error: pyopengltk is required but not installed.")
            print("Please install it using: pip install pyopengltk")
            return False
            
        print("All dependencies found.")
        return True
        
    except ImportError as e:
        print(f"Error: Missing dependency - {e}")
        print("Please install all required packages using: pip install -r requirements.txt")
        return False

def main():
    """Main entry point for the application."""
    # Check dependencies first
    opengl_available = check_dependencies()
    
    try:
        # Create the root window
        root = tk.Tk()
        root.title("Rubik's Cube Simulator")
        
        if opengl_available:
            try:
                # Try to use the OpenGL version
                print("Attempting to use OpenGL renderer...")
                from rubiks_cube.views.gui import RubiksCubeGUI
                app = RubiksCubeGUI(root)
                print("Successfully initialized OpenGL renderer")
            except Exception as e:
                print(f"Failed to initialize OpenGL renderer: {e}")
                print("Falling back to 2D renderer")
                
                # Show a message about fallback mode
                import tkinter.messagebox as messagebox
                messagebox.showinfo(
                    "Fallback Mode", 
                    "OpenGL initialization failed. Using 2D fallback renderer instead.\n\n"
                    "You will still be able to interact with the cube, but in a simplified 2D view."
                )
                
                # Use the fallback renderer
                from rubiks_cube.views.fallback_renderer import create_fallback_gui
                app = create_fallback_gui(root)
        else:
            # Use the fallback renderer directly
            print("OpenGL not available. Using 2D fallback renderer.")
            from rubiks_cube.views.fallback_renderer import create_fallback_gui
            app = create_fallback_gui(root)
        
        # Start the Tkinter event loop
        root.mainloop()
        
    except Exception as e:
        print(f"Error in application startup: {e}")
        sys.exit(1)
        
if __name__ == "__main__":
    main() 