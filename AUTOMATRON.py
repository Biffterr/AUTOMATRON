import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import pyautogui
import random
import tkinter.font as tkFont
import queue  # Import queue for thread communication
import tkinter as tk
import os
import sys


def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS  # This is set by PyInstaller
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))  # Use the directory of the script

    return os.path.join(base_path, relative_path)

class Overlay:
    def __init__(self, master, callback):
        self.master = master
        self.callback = callback

        # Create a full-screen window
        self.overlay = ctk.CTkToplevel(master)
        self.overlay.attributes('-fullscreen', True)  # Make it full screen
        self.overlay.attributes('-alpha', 0.3)  # Set transparency
        self.overlay.bind("<Button-1>", self.get_coordinates)  # Bind left mouse click

        # Optional: Add a label to instruct the user
        self.label = ctk.CTkLabel(self.overlay, text="Click anywhere to select a pixel.", font=("Helvetica", 24), fg_color="white")
        self.label.pack(expand=True)

        # Make the overlay window always on top
        self.overlay.attributes('-topmost', True)

    def get_coordinates(self, event):
        # Get the coordinates of the click
        x, y = event.x_root, event.y_root
        self.callback(x, y)  # Call the callback function with the coordinates
        self.overlay.destroy()  # Close the overlay

def print_available_fonts():
    # Create a temporary Tk instance to access font families
    temp_root = tk.Tk()  # Create a hidden root window
    temp_root.withdraw()  # Hide the root window

    # Get the list of available font families
    available_fonts = tkFont.families()

    # Print the available fonts to the console
    print("Available Fonts:")
    for font_name in available_fonts:
        print(font_name)

    temp_root.destroy()  # Destroy the temporary root window

# Call the function to print available fonts
print_available_fonts()

class Dashboard:
    def __init__(self, master):
        self.master = master
        self.master.title("AUTOMATRON")

        # Set the icon using the resource_path function
        icon_path = resource_path("AUTOMATRON.ico")  # Use the resource path
        if os.path.exists(icon_path):
            self.master.iconbitmap(icon_path)
        else:
            print(f"Icon file not found: {icon_path}")


        self.master.configure(bg='#464646')  # Set the background color of the main window
        self.frame = ctk.CTkFrame(master)   
        self.frame.pack(fill=ctk.Y, expand=True)  # Extend the frame downwards

        self.label = ctk.CTkLabel(self.frame, text="AUTOMATRON", font=("Fixedsys", 30))
        self.label.grid(row=0, column=0, sticky='w', pady=15, padx=(75, 0))

        # Create a frame for the log text
        self.log_frame = ctk.CTkFrame(self.frame, fg_color="#dbdbdb", border_width=0)  # Create a new frame
        self.log_frame.grid(row=0, column=1, sticky='W', padx=(0, 25), pady=(0, 5))  # Place the frame in the grid

        # Create a Text widget for displaying click logs inside the log_frame
        self.log_text = ctk.CTkTextbox(self.log_frame, height=50, width=125, state='normal', fg_color='lightgrey')  # Increased height and width
        self.log_text.pack(expand=True, fill='both')  # Use pack to fill the frame
        self.log_text.configure(state='disabled')  # Initially disable editing

        self.log_entry_count = 0  # Initialize a counter for log entries

        # Entry fields for coordinates
        self.x_label = ctk.CTkLabel(self.frame, text="X Coordinate:")
        self.x_label.grid(row=1, column=0, sticky='w', padx=9, pady=5)
        self.x_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.x_entry.grid(row=1, column=1, sticky='w', padx=(0, 75))

        self.y_label = ctk.CTkLabel(self.frame, text="Y Coordinate:")
        self.y_label.grid(row=2, column=0, sticky='w', padx=9, pady=5)
        self.y_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.y_entry.grid(row=2, column=1, sticky='w', padx=(0, 75))

        # Entry fields for region coordinates
        self.x1_label = ctk.CTkLabel(self.frame, text="X1 Coordinate:")
        self.x1_label.grid(row=3, column=0, sticky='w', padx=4, pady=5)
        self.x1_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.x1_entry.grid(row=3, column=1, sticky='w', padx=(0, 75))

        self.y1_label = ctk.CTkLabel(self.frame, text="Y1 Coordinate:")
        self.y1_label.grid(row=4, column=0, sticky='w', padx=4, pady=5)
        self.y1_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.y1_entry.grid(row=4, column=1, sticky='w', padx=(0, 75))

        self.x2_label = ctk.CTkLabel(self.frame, text="X2 Coordinate:")
        self.x2_label.grid(row=5, column=0, sticky='w', padx=4, pady=5)
        self.x2_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.x2_entry.grid(row=5, column=1, sticky='w', padx=(0, 75))

        self.y2_label = ctk.CTkLabel(self.frame, text="Y2 Coordinate:")
        self.y2_label.grid(row=6, column=0, sticky='w', padx=4, pady=5)
        self.y2_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.y2_entry.grid(row=6, column=1, sticky='w', padx=(0, 75))

        # Button to select pixel
        self.select_pixel_button = ctk.CTkButton(self.frame, text="Select Pixel", command=self.open_overlay)
        self.select_pixel_button.grid(row=7, column=0, columnspan=2, sticky='w', padx=(40, 75))  # Increase the left padding

        # Toggle for Select Region
        self.select_region_var = ctk.BooleanVar(value=False)
        self.select_region_toggle = ctk.CTkCheckBox(self.frame, text="Enable Select Region", variable=self.select_region_var)
        self.select_region_toggle.grid(row=8, column=0, sticky='w', columnspan=2, pady=5, padx=(5, 0))  # Increase the left padding

        # Button to select region
        self.select_region_button = ctk.CTkButton(self.frame, text="Select Region", command=self.select_region)
        self.select_region_button.grid(row=7, column=0, columnspan=2, sticky='e', padx=(0, 125))  # Decrease the right padding

        # Entry field for fixed interval
        self.interval_label = ctk.CTkLabel(self.frame, text="Click Interval (seconds):")
        self.interval_label.grid(row=10, column=0, sticky='w', padx=(5, 75))
        self.interval_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.interval_entry.grid(row=10, column=1, sticky='w', padx=(0, 75))
        self.interval_entry.insert(0, "3")  # Default value

        # Entry fields for random interval
        self.min_interval_label = ctk.CTkLabel(self.frame, text="Min Click Interval (seconds):")
        self.min_interval_label.grid(row=11, column=0, sticky='e', padx=5, pady=5)
        self.min_interval_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.min_interval_entry.grid(row=11, column=1, pady=5)
        self.min_interval_entry.insert(0, "0.5")  # Default value

        self.max_interval_label = ctk.CTkLabel(self.frame, text="Max Click Interval (seconds):")
        self.max_interval_label.grid(row=12, column=0, sticky='e', padx=5, pady=5)
        self.max_interval_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.max_interval_entry.grid(row=12, column=1, pady=5)
        self.max_interval_entry.insert(0, "2.5")  # Default value

        # Status label for interval mode
        self.interval_mode_label = ctk.CTkLabel(self.frame, text="Current Mode: Fixed Interval")
        self.interval_mode_label.grid(row=13, column=0, columnspan=2, pady=5, padx=(0, 115))  # Decrease the right padding

        # Toggle button for random intervals
        self.use_random_interval_var = ctk.BooleanVar(value=False)
        self.toggle_button = ctk.CTkCheckBox(self.frame, text="Use Random Intervals", variable=self.use_random_interval_var, command=self.toggle_interval_fields)
        self.toggle_button.grid(row=14, column=0, columnspan=2, pady=5, padx=(0, 115))  # Decrease the right padding

        # Click type selection
        self.click_type_var = ctk.StringVar(value="left")
        self.click_type_label = ctk.CTkLabel(self.frame, text="Click Type:")
        self.click_type_label.grid(row=15, column=0, sticky='w', padx=5, pady=5)

        self.left_radio = ctk.CTkRadioButton(self.frame, text="Left Click", variable=self.click_type_var, value="left")
        self.left_radio.grid(row=15, column=0, pady=5, sticky='w', padx=(75, 0))

        self.right_radio = ctk.CTkRadioButton(self.frame, text="Right Click", variable=self.click_type_var, value="right")
        self.right_radio.grid(row=15, column=0, pady=5, sticky='e', padx=(175, 0))

        # Create a frame for buttons
        button_frame = ctk.CTkFrame(self.frame, fg_color="#dbdbdb", border_width=0)  # Set frame color to white or any other color that matches your background
        button_frame.grid(row=16, column=0, columnspan=2, pady=(10, 0), padx=(0, 82))  # Add left padding to the frame

        # Start and Stop buttons for autoclicker
        self.start_button = ctk.CTkButton(button_frame, text="Start Autoclicker", command=self.start_autoclicker)
        self.start_button.grid(row=0, column=0, padx=(10, 25), sticky='w')  # Align to the west (left)

        self.stop_button = ctk.CTkButton(button_frame, text="Stop Autoclicker", command=self.stop_autoclicker)
        self.stop_button.grid(row=0, column=1, padx=(50, 0), sticky='e')  # Adjust padding as needed

        # Create a new frame for the logout button
        self.logout_frame = ctk.CTkFrame(self.frame, fg_color="#dbdbdb", border_width=0)  # Set frame color to white or any other color that matches your background
        self.logout_frame.grid(row=17, column=0, columnspan=2, pady=(10, 0), padx=(0, 82))  # Position below the button frame

        # Logout button
        self.logout_button = ctk.CTkButton(self.logout_frame, text="EXIT", command=self.logout)
        self.logout_button.pack(pady=5)  # Center the button in the frame

        # Status bar
        self.status_bar_frame = ctk.CTkFrame(master, corner_radius=0)  # Create a frame for the status bar
        self.status_bar_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

        self.status_bar = ctk.CTkLabel(self.status_bar_frame, text="Status: Ready", anchor='w')
        self.status_bar.pack(side=ctk.LEFT, padx=10)  # Add padding for aesthetics

        # Timer label
        self.timer_label = ctk.CTkLabel(self.status_bar_frame, text="Timer: 0s", font=("Helvetica", 12))
        self.timer_label.pack(side=ctk.RIGHT, padx=10)  # Add padding for aesthetics

        self.autoclicking = False
        self.elapsed_time = 0  # Timer variable

        # Create a queue for communication
        self.queue = queue.Queue()

        # Call to toggle fields initially
        self.toggle_interval_fields()

        # Initialize region coordinates
        self.region_coords = None

        # 1. Add Mouse Smoothing Toggle
        self.mouse_smoothing_var = ctk.BooleanVar(value=False)
        self.mouse_smoothing_toggle = ctk.CTkCheckBox(self.frame, text="Enable Mouse Smoothing", variable=self.mouse_smoothing_var)
        self.mouse_smoothing_toggle.grid(row=9, column=0, sticky='w', columnspan=2, pady=5, padx=(5, 0))  # Increase the left padding

        # 2. Add entry field for Smoothing Value
        self.smoothing_entry = ctk.CTkEntry(self.frame, width=125)  # Set width to 10 characters
        self.smoothing_entry.grid(row=9, column=1, sticky='w', padx=(0, 75))
        self.smoothing_entry.insert(0, "5")  # Default value

        # Start the UI update loop
        self.master.after(100, self.update_ui)

    def toggle_interval_fields(self):
        if self.use_random_interval_var.get():
            self.min_interval_label.grid(row=11, column=0, sticky='w', pady=5)
            self.min_interval_entry.grid(row=11, column=1, sticky='w', padx=(0, 75))
            self.max_interval_label.grid(row=12, column=0, sticky='w', pady=5)
            self.max_interval_entry.grid(row=12, column=1, sticky='w', padx=(0, 75))
            self.interval_label.grid_remove()
            self.interval_entry.grid_remove()
            self.interval_mode_label.configure(text="Current Mode: Random Intervals")
        else:
            self.min_interval_label.grid_remove()
            self.min_interval_entry.grid_remove()
            self.max_interval_label.grid_remove()
            self.max_interval_entry.grid_remove()
            self.interval_label.grid(row=10, column=0, sticky='w', pady=5)
            self.interval_entry.grid(row=10, column=1, sticky='w', padx=(0, 75))
            self.interval_mode_label.configure(text="Current Mode: Fixed Interval")

    def open_overlay(self):
        Overlay(self.master, self.set_coordinates)

    def set_coordinates(self, x, y):
        self.x_entry.delete(0, ctk.END)
        self.x_entry.insert(0, str(x))
        self.y_entry.delete(0, ctk.END)
        self.y_entry.insert(0, str(y))

    def select_region(self):
        if not self.select_region_var.get():
            messagebox.showwarning("Warning", "Select Region is disabled. Please enable it to select a region.")
            return

        # Get the screen width and height
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()

        # Create the overlay window
        self.overlay = ctk.CTkToplevel(self.master)
        self.overlay.overrideredirect(True)  # Remove window decorations
        self.overlay.wm_attributes("-alpha", 0.5)  # Make the overlay semi-transparent
        self.overlay.wm_attributes("-topmost", True)

        # Set overlay to full screen
        self.overlay.geometry(f"{screen_width}x{screen_height}+0+0")
        self.overlay.bind("<ButtonPress-1>", self.on_start)
        self.overlay.bind("<B1-Motion>", self.on_drag)
        self.overlay.bind("<ButtonRelease-1>", self.on_release)

        # Create a canvas on the overlay to mark the region
        self.canvas = ctk.CTkCanvas(self.overlay, bg='white', highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Initialize rectangle variables
        self.rect = None
        self.start_x = None
        self.start_y = None

    def on_start(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red", width=2)

    def on_drag(self, event):
        # Update the rectangle coordinates as the mouse drags
        self.canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

    def on_release(self, event):
        x1 = min(self.start_x, event.x)
        y1 = min(self.start_y, event.y)
        x2 = max(self.start_x, event.x)
        y2 = max(self.start_y, event.y)

        # Update the entry fields with the new coordinates
        self.x1_entry.delete(0, ctk.END)
        self.x1_entry.insert(0, str(x1))
        self.y1_entry.delete(0, ctk.END)
        self.y1_entry.insert(0, str(y1))
        self.x2_entry.delete(0, ctk.END)
        self.x2_entry.insert(0, str(x2))
        self.y2_entry.delete(0, ctk.END)
        self.y2_entry.insert(0, str(y2))

        self.region_coords = (x1, y1, x2, y2)  # Store the selected region coordinates
        self.overlay.destroy()  # Close the overlay

        # Show the selected region coordinates
        print(f"Selected Region: {self.region_coords}")

    def start_autoclicker(self):
        self.autoclicking = True
        self.elapsed_time = 0  # Reset timer
        self.update_timer()  # Start the timer update
        self.status_bar.configure(text="Status: Autoclicker Running")
        threading.Thread(target=self.autoclick).start()

    def stop_autoclicker(self):
        self.autoclicking = False
        self.status_bar.configure(text="Status: Autoclicker Stopped")

    def smooth_move(self, target_x, target_y):
        if self.mouse_smoothing_var.get():
            try:
                steps = int(self.smoothing_entry.get())  # Get the number of steps from the entry field
                if steps <= 0:
                    raise ValueError("Number of steps must be greater than 0.")
                current_x, current_y = pyautogui.position()
                for step in range(1, steps + 1):
                    # Calculate intermediate position
                    x = current_x + (target_x - current_x) * (step / steps)
                    y = current_y + (target_y - current_y) * (step / steps)
                    pyautogui.moveTo(x, y)
                    time.sleep(0.01)  # Small delay for smoothness
            except ValueError as e:
                messagebox.showerror("Input Error", str(e))  # Show error if input is invalid
        else:
            pyautogui.moveTo(target_x, target_y)

    def update_log(self, x, y, interval):
        """Update the log display with click details, showing the latest click at the top."""
        # Calculate seconds and milliseconds
        seconds = int(interval)  # Get the whole seconds
        milliseconds = int((interval - seconds) * 1000)  # Get the remaining milliseconds

        self.log_text.configure(state='normal')  # Enable editing
        self.log_text.insert('1.0', f"({x}, {y}) {seconds}.{milliseconds:03d} s\n")  # Insert at the top
        self.log_text.configure(state='disabled')  # Disable editing

        self.log_entry_count += 1  # Increment the log entry counter

        # Clear the log if there are more than 10 entries
        if self.log_entry_count > 10:
            self.log_text.configure(state='normal')  # Enable editing to clear
            self.log_text.delete('1.0', ctk.END)  # Clear all entries
            self.log_entry_count = 0  # Reset the counter
            self.log_text.configure(state='disabled')  # Disable editing again

    def autoclick(self):
        while self.autoclicking:
            try:
                click_type = self.click_type_var.get()
                print(f"Click Type: {click_type}")  # Debugging statement

                if self.select_region_var.get() and self.region_coords:
                    x1, y1, x2, y2 = self.region_coords
                    x = random.randint(x1, x2)
                    y = random.randint(y1, y2)
                else:
                    x = int(self.x_entry.get())
                    y = int(self.y_entry.get())

                print(f"Clicking at: ({x}, {y})")  # Debugging statement

                # Smoothly move to the target position
                self.smooth_move(x, y)

                if self.use_random_interval_var.get():
                    min_interval = float(self.min_interval_entry.get())
                    max_interval = float(self.max_interval_entry.get())
                    interval = random.uniform(min_interval, max_interval)
                else:
                    interval = float(self.interval_entry.get())

                print(f"Interval: {interval}")  # Debugging statement

                pyautogui.click(x, y, button=click_type)

                # Update the visual log with click details
                self.queue.put((x, y, interval))  # Put click details in the queue

                time.sleep(interval)  # Wait for the specified interval
            except ValueError as e:
                print(f"ValueError: {e}")  # Log the error
                messagebox.showerror("Input Error", "Please enter valid coordinates and interval.")
                self.stop_autoclicker()  # Stop the autoclicker
                return  # Exit the method if input is invalid

    def update_ui(self):
        while not self.queue.empty():
            x, y, interval = self.queue.get()
            self.update_log(x, y, interval)  # Update the log with the click details
        self.master.after(100, self.update_ui)  # Schedule the next UI update

    def update_timer(self):
        if self.autoclicking:
            self.elapsed_time += 1
            self.timer_label.configure(text=f"Timer: {self.elapsed_time}s")
            self.master.after(1000, self.update_timer)  # Update every second

    def logout(self):
        self.master.destroy()  # Close the dashboard window

if __name__ == "__main__":
    ctk.set_appearance_mode("System")  # Set the appearance mode
    ctk.set_default_color_theme("blue")  # Set the default color theme

    root = ctk.CTk()  # Create the main window
    root.geometry("405x700")  # Set the size of the main window
    root.resizable(False, False)  # Lock the application size
    root.minsize(405, 665)  # Set minimum size to match the intended size
    root.configure(bg='#464646')  # Match the frame's background color

    app = Dashboard(root)
    root.mainloop()