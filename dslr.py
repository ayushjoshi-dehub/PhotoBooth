import cv2
from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk, ImageOps
import os


class PhotoBoothApp:
    def __init__(self, root, camera_index=1):
        self.root = root
        self.root.title("Photobooth Application")
        self.root.geometry("900x700")
        self.root.configure(bg="#2C2F33")  # Dark background for better look

        # Variables
        self.video_capture = cv2.VideoCapture(camera_index)  # Use external camera
        self.captured_image = None
        self.photo_display = None

        # Paths to templates
        self.templates = {
            "None": None,
            "Birthday": "templates/birthday.png",
            "Wedding": "templates/wedding.png",
            "Party": "templates/party.png",
        }

        # Check if the camera opened successfully
        if not self.video_capture.isOpened():
            self.video_capture.release()
            raise RuntimeError("Could not access the camera. Please check your device.")

        # GUI Components
        self.setup_gui()

        # Start the video feed
        self.update_video_feed()

    def setup_gui(self):
        # Title Label
        title_label = Label(
            self.root,
            text="📸 Welcome to the Photobooth 📸",
            font=("Helvetica", 24, "bold"),
            fg="white",
            bg="#2C2F33",
        )
        title_label.pack(pady=20)

        # Video Frame
        self.video_frame = Label(self.root, bg="#23272A", relief=RIDGE)
        self.video_frame.pack(pady=10, padx=20, fill=BOTH, expand=True)

        # Button Frame
        button_frame = Frame(self.root, bg="#2C2F33")
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

        # Style Configuration
        style = ttk.Style()
        style.configure(
            "TButton",
            font=("Helvetica", 16, "bold"),
            padding=10,
            background="#7289DA",
            foreground="white",
            focuscolor="none",
        )
        style.map(
            "TButton",
            background=[("active", "#99AAB5")],
            foreground=[("active", "#2C2F33")],
        )

    def update_video_feed(self):
        # Capture frame-by-frame
        ret, frame = self.video_capture.read()
        if ret:
            # Convert to RGB and display in Tkinter
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.photo_display = ImageTk.PhotoImage(image=Image.fromarray(frame_rgb))
            self.video_frame.configure(image=self.photo_display)

        # Recursively update video feed
        self.root.after(10, self.update_video_feed)

    def capture_image(self):
        # Capture the current frame
        ret, frame = self.video_capture.read()
        if ret:
            self.captured_image = frame
            self.save_and_preview()

    def save_and_preview(self):
        # Save captured image
        save_path = "captured_photo.jpg"
        cv2.imwrite(save_path, self.captured_image)

        # Preview in a new window
        top = Toplevel(self.root)
        top.title("Captured Photo Preview")
        top.configure(bg="#2C2F33")

        img = Image.open(save_path)
        img_tk = ImageTk.PhotoImage(img)
        preview_label = Label(top, image=img_tk, bg="#2C2F33")
        preview_label.image = img_tk
        preview_label.pack(pady=10)

        # Enable print button
        self.print_button.config(state=NORMAL)

    def show_template_selection(self):
        # Create a new window for template selection
        top = Toplevel(self.root)
        top.title("Choose a Template")
        top.geometry("400x400")
        top.configure(bg="#2C2F33")

        # Title Label
        label = Label(
            top,
            text="Choose a Template:",
            font=("Helvetica", 18, "bold"),
            fg="white",
            bg="#2C2F33",
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

    # Pass the index of the external camera (1 or higher)
    root = Tk()
    app = PhotoBoothApp(root, camera_index=1)  # Change index to match your external camera
    root.mainloop()
