import mss  # Library for capturing screenshots
import cv2  # OpenCV for image processing
import numpy as np  # NumPy for handling arrays
from pynput import mouse  # Library for mouse event handling
import threading  # For running processes in parallel
import tkinter as tk  # GUI library for file dialogs
from tkinter import filedialog  # File dialog module

# Dictionary to store the coordinates of the selected area
coords = {"x1": 0, "y1": 0, "x2": 0, "y2": 0}
listener = None  # Mouse listener instance

# Initialize Tkinter and hide the main window
root = tk.Tk()
root.withdraw()  # Prevents an empty window from appearing


def onClick(x, y, button, pressed):
    """
    Handles mouse click events to capture the coordinates 
    of the selected region.
    
    - When the mouse is pressed: stores the starting coordinates.
    - When the mouse is released: stores the ending coordinates 
      and triggers the screenshot capture.
    """
    global coords, listener

    if pressed:
        # Store starting coordinates
        coords["x1"], coords["y1"] = x, y
    else:
        # Store ending coordinates
        coords["x2"], coords["y2"] = x, y

        # Stop the mouse listener after 1 second
        threading.Timer(1, stopListener).start()

        # Capture the screenshot
        captureScreenshot()


def captureScreenshot():
    """
    Captures a screenshot of the selected area using `mss` 
    and converts it into an OpenCV image.
    """
    x1, y1, x2, y2 = coords["x1"], coords["y1"], coords["x2"], coords["y2"]

    # Ensure coordinates are ordered correctly (top-left to bottom-right)
    x1, x2 = min(x1, x2), max(x1, x2)
    y1, y2 = min(y1, y2), max(y1, y2)

    # Calculate width and height of the selected region
    width, height = x2 - x1, y2 - y1

    with mss.mss() as sct:
        # Define the capture region
        capture = {"top": y1, "left": x1, "width": width, "height": height}
        screenshot = sct.grab(capture)  # Take a screenshot

        # Convert the screenshot to a NumPy array
        img = np.array(screenshot)

        # Convert from BGRA (used by `mss`) to BGR (used by OpenCV)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)

        # Call the save function on the main thread
        root.after(0, lambda: saveScreenshot(img))


def saveScreenshot(img):
    """
    Opens a file dialog to allow the user to save the screenshot.
    If a path is selected, the image is saved using OpenCV.
    """
    save_path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG files", "*.png"),
            ("JPG files", "*.jpg"),
            ("All files", "*.*"),
        ],
    )

    if save_path:
        cv2.imwrite(save_path, img)  # Save the image
        print(f"✅ Screenshot saved at: {save_path}")
    else:
        print("❌ Screenshot not saved")

    # Close the Tkinter application after saving
    root.destroy()


def stopListener():
    """Stops the mouse listener."""
    global listener
    if listener is not None:
        listener.stop()


# Start the mouse listener in a separate thread
def startMouseListener():
    """
    Initializes and starts the mouse listener 
    to detect click events in the background.
    """
    global listener
    listener = mouse.Listener(on_click=onClick)
    listener.start()
    listener.join()
    listener.stop()


# Run the mouse listener in a daemon thread
threading.Thread(target=startMouseListener, daemon=True).start()

print("🔲 Select the region by holding down the left mouse button...")

# Start the Tkinter event loop to keep the file dialog functional
root.mainloop()
