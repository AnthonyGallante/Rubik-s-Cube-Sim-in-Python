#!/usr/bin/env python3
"""
Runner script for the Rubik's Cube Simulator.
This is a convenience wrapper to run the application from the root directory.
"""

import sys
import os
import importlib
import pkgutil

def check_installation():
    """Check if required packages are installed."""
    required_packages = [
        "numpy", 
        "OpenGL", 
        "PIL", 
        "pyopengltk"
    ]
    
    missing = []
    for package in required_packages:
        if not pkgutil.find_loader(package):
            missing.append(package)
    
    if missing:
        print("Missing required packages:", ", ".join(missing))
        print("Please install them with: pip install -r requirements.txt")
        return False
    
    return True

def show_fallback_message():
    """Display a fallback message if OpenGL doesn't work."""
    import tkinter as tk
    from tkinter import messagebox
    
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    messagebox.showerror(
        "OpenGL Error",
        "Failed to initialize OpenGL context.\n\n"
        "This may be due to:\n"
        "1. Missing or incompatible graphics drivers\n"
        "2. Insufficient GPU capabilities\n"
        "3. Incompatible rendering backend\n\n"
        "Please ensure you have the latest graphics drivers and compatible hardware."
    )
    
    root.destroy()

def main():
    """Main entry point with error handling."""
    # Check if required packages are installed
    if not check_installation():
        return 1
    
    try:
        # Try to import and run the main module
        from rubiks_cube.main import main
        main()
    except Exception as e:
        print(f"Error starting application: {e}")
        try:
            show_fallback_message()
        except Exception:
            print("Failed to display graphical error message.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 