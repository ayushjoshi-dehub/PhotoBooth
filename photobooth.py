import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import os
import numpy as np


class PhotoBoothApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photobooth Application")
        self.root.geometry("900x700")
        self.root.configure(bg="#CDB4FF")  # Dark background for better look

        # Variables
        self.video_capture = cv2.VideoCapture(0)
        self.captured_image = None
        self.photo_display = None
        self.beauty_mode = False
        self.filter_type = StringVar(value="None")  # Default filter type
        self.filter_intensity = IntVar(value=30)  # Default intensity for filters

        # Paths to templates
        self.templates = {
            "None": None,
            "Birthday": "templates/birthday.png",
            "Wedding": "templates/wedding.png",
            "Party": "templates/party.png",
        }

        # GUI Components
        self.setup_gui()

        # Start the video feed
        self.update_video_feed()

    def setup_gui(self):
        # Top Frame to hold title and image
        top_frame = Frame(self.root, bg="#CDB4FF")
        top_frame.pack(pady=20)

        # Load and display the image
        try:
            logo = Image.open("C:\\Users\\joshi\\OneDrive\\Desktop\\photobooth\\2.jpg").convert("RGBA")
  # Replace with your image file
            logo = logo.resize((100, 100), Image.LANCZOS)

            logo_img = ImageTk.PhotoImage(logo)
            logo_label = Label(top_frame, image=logo_img, bg="#CDB4FF")
            logo_label.image = logo_img  # Store reference to prevent garbage collection
            logo_label.pack(side=LEFT, padx=10)
        except FileNotFoundError:
            print("Logo image not found! Please add 'photobooth_logo.png' to the directory.")

        # Title Label
        title_label = Label(
            top_frame,
            text=" Welcome to the Photobooth ",
            font=("Brush Script MT", 30, "bold"),
            fg="white",
            bg="#CDB4FF",
        )
        title_label.pack(side=LEFT, padx=10)

        # Video Frame
        self.video_frame = Label(self.root, bg="#23272A", relief=RIDGE)
        self.video_frame.pack(pady=10, padx=50, fill=X, expand=True)

        # Button Frame
        button_frame = Frame(self.root, bg="#CDB4FF")
        button_frame.pack(pady=20)

        # Capture Button
        self.capture_button = ttk.Button(
            button_frame, text="📷 Capture", command=self.capture_image, style="TButton"
        )
        self.capture_button.grid(row=0, column=0, padx=20)

        # Print Button
        self.print_button = ttk.Button(
            button_frame, text="🖨️ Print", command=self.show_template_selection, style="TButton"
        )
        self.print_button.grid(row=0, column=1, padx=20)
        self.print_button.config(state=DISABLED)

        # Quit Button
        self.quit_button = ttk.Button(
            button_frame, text="❌ Quit", command=self.quit_app, style="TButton"
        )
        self.quit_button.grid(row=0, column=2, padx=20)

        # Beauty Filter Controls
        beauty_frame = Frame(self.root, bg="#CDB4FF")
        beauty_frame.pack(side=LEFT, padx=10, pady=10)

        beauty_label = Label(
            beauty_frame,
            text="🎉 Beauty Filter Options:",
            font=("Helvetica", 12, "bold"),
            fg="white",
            bg="#CDB4FF",
        )
        beauty_label.pack(anchor=W, pady=5)

        # Dropdown for Filter Type
        self.filter_dropdown = ttk.Combobox(
            beauty_frame,
            textvariable=self.filter_type,
            values=["None", "Gaussian Blur", "Median Blur", "Bilateral", "Sharpen", "Noise Reduction"],
            state="readonly",
            font=("Helvetica", 10),
        )
        self.filter_dropdown.pack(fill=X, padx=10, pady=5)

        # Seekbar for Intensity
        self.filter_slider = ttk.Scale(
            beauty_frame,
            from_=0,
            to=20,
            orient=HORIZONTAL,
            variable=self.filter_intensity,
            command=self.update_filter_intensity,
        )
        self.filter_slider.pack(fill=X, padx=10, pady=5)

        # Toggle Button
        self.beauty_toggle_button = ttk.Button(
            beauty_frame,
            text="🎉 Toggle Beauty Filter",
            command=self.toggle_beauty_mode,
            style="TButton",
        )
        self.beauty_toggle_button.pack(pady=20)

        # Style Configuration
        style = ttk.Style()
        style.configure(
            "TButton",
            font=("Helvetica", 12, "bold"),
            padding=10,
            background="#BA60F2",
            foreground="black",
            focuscolor="#820263",
        )
        style.map(
            "TButton",
            background=[("active", "#820263")],
            foreground=[("active", "#820263")],
        )

    def update_video_feed(self):
        # Capture frame-by-frame
        ret, frame = self.video_capture.read()
        if ret:
            # Apply beauty filter if enabled
            if self.beauty_mode:
                frame = self.apply_selected_filter(frame)

            # Convert to RGB and display in Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo_display = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.video_frame.configure(image=self.photo_display)

        # Recursively update video feed
        self.root.after(10, self.update_video_feed)

    def apply_selected_filter(self, frame):
        # Apply the selected filter
        filter_type = self.filter_type.get()
        intensity = self.filter_intensity.get()

        if filter_type == "Gaussian Blur":
            return cv2.GaussianBlur(frame, (int(intensity) * 2 + 1, int(intensity) * 2 + 1), 0)
        elif filter_type == "Median Blur":
            return cv2.medianBlur(frame, int(intensity) * 2 + 1)
        elif filter_type == "Bilateral":
            return cv2.bilateralFilter(frame, int(intensity) * 2 + 1, intensity * 10, intensity * 10)
        elif filter_type == "Sharpen":
            kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Sharpening kernel
            return cv2.filter2D(frame, -1, kernel)
        elif filter_type == "Noise Reduction":
            return cv2.fastNlMeansDenoisingColored(frame, None, intensity, intensity, 7, 21)
        else:
            return frame

    def update_filter_intensity(self, event=None):
        # Update the filter intensity dynamically
        print(f"Filter intensity: {self.filter_intensity.get()}")

    def toggle_beauty_mode(self):
        # Toggle beauty filter mode
        self.beauty_mode = not self.beauty_mode
        mode = "enabled" if self.beauty_mode else "disabled"
        print(f"Beauty filter {mode}.")

    def capture_image(self):
        # Capture the current frame
        ret, frame = self.video_capture.read()
        if ret:
            if self.beauty_mode:
                frame = self.apply_selected_filter(frame)
            self.captured_image = frame
            self.save_and_preview()

    def save_and_preview(self):
        # Save captured image
        save_path = "captured_photo.jpg"
        cv2.imwrite(save_path, self.captured_image)

        # Preview in a new window
        top = Toplevel(self.root)
        top.title("Captured Photo Preview")
        top.configure(bg="#CDB4FF")

        img = Image.open(save_path)
        img_tk = ImageTk.PhotoImage(img)
        preview_label = Label(top, image=img_tk, bg="#CDB4FF")
        preview_label.image = img_tk
        preview_label.pack(pady=10)

        # Enable print button
        self.print_button.config(state=NORMAL)

    def show_template_selection(self):
        # Create a new window for template selection
        top = Toplevel(self.root)
        top.title("Choose a Template")
        top.geometry("400x400")
        top.configure(bg="#CDB4FF")

        # Title Label
        label = Label(
            top,
            text="Choose a Template:",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#CDB4FF",
        )
        label.pack(pady=20)

        # Template Buttons
        for template_name, template_path in self.templates.items():
            button = ttk.Button(
                top,
                text=template_name,
                command=lambda t=template_path: self.apply_template_and_print(t),
                style="TButton",
            )
            button.pack(pady=10, fill=X, padx=50)

    def apply_template_and_print(self, template_path):
        # Overlay photo with the selected template
        if template_path:
            # Open photo and template
            photo = Image.open("captured_photo.jpg").convert("RGBA")
            template = Image.open(template_path).convert("RGBA")

            # Resize photo to fit the template
            photo = ImageOps.fit(photo, template.size, method=Image.ANTIALIAS)

            # Composite the photo onto the template
            combined = Image.alpha_composite(template, photo)

            # Save the combined image
            combined_path = "combined_photo.png"
            combined.save(combined_path)
        else:
            combined_path = "captured_photo.jpg"  # No template

        # Print the final image
        self.print_image(combined_path)

    def print_image(self, image_path):
        # Print the selected or combined image
        print("Printing image...")
        os.startfile(image_path, "print")

    def quit_app(self):
        # Release the video feed and quit
        self.video_capture.release()
        self.root.destroy()


# Run the application
if __name__ == "__main__":
    # Ensure template folder exists
    if not os.path.exists("templates"):
        os.makedirs("templates")
        print("Add your templates in the 'templates' folder (e.g., birthday.png).")

    root = Tk()
    app = PhotoBoothApp(root)
    root.mainloop()
