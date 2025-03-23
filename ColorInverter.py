import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import mss

class ColorInverter:
    def __init__(self, root):
        """Initialize the color inverter window with T key toggle."""
        self.root = root
        self.root.attributes('-topmost', True)  # Always on top
        self.root.overrideredirect(True)       # No borders
        self.root.attributes('-alpha', 0.9)    # Slight transparency
        
        # Initial window size and position
        self.width = 400
        self.height = 300
        self.root.geometry(f'{self.width}x{self.height}+100+100')  # Start at (100,100)
        
        # Store previous size for toggling
        self.prev_width = self.width
        self.prev_height = self.height
        self.is_small = False
        
        # Frame to organize widgets
        self.frame = tk.Frame(self.root)
        self.frame.pack(expand=True, fill='both')
        
        # Canvas for displaying the image
        self.canvas = tk.Canvas(self.frame, width=self.width, height=self.height)
        self.canvas.pack(expand=True, fill='both')
        self.image_id = self.canvas.create_image(0, 0, anchor='nw')
        
        # Close button with hand cursor
        self.close_btn = tk.Button(self.frame, text='X', command=self.root.quit, bg='red', fg='white', cursor='hand2')
        self.close_btn.place(relx=1.0, rely=0.0, anchor='ne')
        
        # Refresh button with hand cursor
        self.refresh_btn = tk.Button(self.frame, text='Refresh', command=self.update_image, bg='blue', fg='white', cursor='hand2')
        self.refresh_btn.place(relx=0.0, rely=0.0, anchor='nw')
        
        # Bind events
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.drag)
        self.canvas.bind('<Motion>', self.update_cursor)
        self.canvas.bind('<ButtonRelease-1>', self.set_focus)
        
        # Keyboard shortcuts
        self.root.bind('<Key-r>', lambda event: self.update_image())  # R to refresh
        self.root.bind('<Key-c>', lambda event: self.root.quit())     # C to close
        self.root.bind('<Key-t>', lambda event: self.toggle_size())   # T to toggle size (changed from Ctrl+T)
        
        # Initialize screen capture tool
        self.sct = mss.mss()
        
        # Perform an initial update
        self.update_image()

    def start_drag(self, event):
        """Determine if dragging should move or resize based on click position."""
        self.start_x = event.x_root
        self.start_y = event.y_root
        self.initial_win_x = self.root.winfo_x()
        self.initial_win_y = self.root.winfo_y()
        border = 20
        
        self.is_resizing = False
        local_x = event.x
        local_y = event.y
        self.resize_from_left = local_x < border
        self.resize_from_right = local_x > self.width - border
        self.resize_from_top = local_y < border
        self.resize_from_bottom = local_y > self.height - border
        
        if self.resize_from_left or self.resize_from_right or self.resize_from_top or self.resize_from_bottom:
            self.is_resizing = True
        else:
            self.is_resizing = False

    def drag(self, event):
        """Handle dragging to move or resize the window."""
        if self.is_resizing:
            new_x = self.initial_win_x
            new_y = self.initial_win_y
            new_width = self.width
            new_height = self.height
            
            if self.resize_from_left:
                new_width = max(100, self.initial_win_x + self.width - event.x_root)
                new_x = event.x_root
            elif self.resize_from_right:
                new_width = max(100, event.x_root - self.initial_win_x)
            
            if self.resize_from_top:
                new_height = max(100, self.initial_win_y + self.height - event.y_root)
                new_y = event.y_root
            elif self.resize_from_bottom:
                new_height = max(100, event.y_root - self.initial_win_y)
            
            self.width = new_width
            self.height = new_height
            self.root.geometry(f'{new_width}x{new_height}+{new_x}+{new_y}')
            self.canvas.config(width=new_width, height=new_height)
        else:
            new_x = self.initial_win_x + (event.x_root - self.start_x)
            new_y = self.initial_win_y + (event.y_root - self.start_y)
            self.root.geometry(f'+{new_x}+{new_y}')

    def update_cursor(self, event):
        """Change cursor shape based on mouse position."""
        border = 20
        x = event.x
        y = event.y
        
        near_left = x < border
        near_right = x > self.width - border
        near_top = y < border
        near_bottom = y > self.height - border
        
        if near_left and near_top:
            self.canvas.config(cursor='size_nw_se')
        elif near_right and near_top:
            self.canvas.config(cursor='size_ne_sw')
        elif near_left and near_bottom:
            self.canvas.config(cursor='size_ne_sw')
        elif near_right and near_bottom:
            self.canvas.config(cursor='size_nw_se')
        elif near_left:
            self.canvas.config(cursor='size_we')
        elif near_right:
            self.canvas.config(cursor='size_we')
        elif near_top:
            self.canvas.config(cursor='size_ns')
        elif near_bottom:
            self.canvas.config(cursor='size_ns')
        else:
            self.canvas.config(cursor='fleur')

    def set_focus(self, event):
        """Set focus to the root window after clicking."""
        self.root.focus_set()
        print("Focus set")  # Debug

    def toggle_size(self):
        """Toggle window between small size and previous size."""
        small_width = 200
        small_height = 150
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        
        print(f"Toggling size: Current {self.width}x{self.height}, Small={self.is_small}")  # Debug
        
        if not self.is_small:
            # Store current size and shrink
            self.prev_width = self.width
            self.prev_height = self.height
            self.width = small_width
            self.height = small_height
            self.is_small = True
        else:
            # Restore previous size
            self.width = self.prev_width
            self.height = self.prev_height
            self.is_small = False
        
        # Apply new geometry and ensure visibility
        self.root.geometry(f'{self.width}x{self.height}+{x}+{y}')
        self.canvas.config(width=self.width, height=self.height)
        self.root.update()  # Force update to ensure visibility
        self.update_image()  # Refresh image for new size
        print(f"New size: {self.width}x{self.height}")  # Debug

    def update_image(self):
        """Capture, process, and display the inverted image."""
        self.root.attributes('-alpha', 0)
        self.root.update_idletasks()
        
        x = self.root.winfo_x()
        y = self.root.winfo_y()
        monitor = {"top": y, "left": x, "width": self.width, "height": self.height}
        screenshot = self.sct.grab(monitor)
        img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
        
        self.root.attributes('-alpha', 0.9)
        self.root.update_idletasks()
        
        img_array = np.array(img)
        inverted_array = 255 - img_array
        inverted_img = Image.fromarray(inverted_array)
        
        self.photo = ImageTk.PhotoImage(inverted_img)
        self.canvas.itemconfig(self.image_id, image=self.photo)
        self.canvas.image = self.photo

def main():
    root = tk.Tk()
    app = ColorInverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()