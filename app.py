import tkinter as tk
from tkinter import messagebox
import cv2
import face_recognition
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PIL import Image, ImageTk
import pyttsx3
import datetime

import threading

# --- Configuration ---
# IMPORTANT: For Gmail, you may need to create an "App Password"
# Go to your Google Account -> Security -> 2-Step Verification -> App Passwords
SENDER_EMAIL = "classroom_sentry_system@gmail.com"  # Your email address
SENDER_PASSWORD = "arky ugvf tmep gpkw"  # Your email app password
RECIPIENT_EMAIL = "ee.anoop@gmail.com"  # Where to send the report

class StudentRegisterApp:
    def __init__(self, window, window_title):
        self.window = window
        self.window.title(window_title)

        # --- State Variables ---
        self.known_face_encodings = []
        self.known_face_names = []
        self.sentry_mode = False
        self.sentry_thread = None
        self.sentry_stop_event = threading.Event()
        self.frame_lock = threading.Lock()
        self.latest_frame = None
        
        # --- Load Student Data ---
        self.load_student_images()

        # --- Setup Video Capture ---
        self.video_capture = cv2.VideoCapture(0) # 0 is usually the default webcam

        # --- Setup Text-to-Speech ---
        self.tts_engine = pyttsx3.init()

        # --- Create UI Elements ---
        self.canvas = tk.Canvas(window, width=self.video_capture.get(cv2.CAP_PROP_FRAME_WIDTH), height=self.video_capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.canvas.pack()

        # --- Buttons ---
        btn_frame = tk.Frame(window, bg="white")
        btn_frame.pack(fill=tk.X, expand=True)

        self.btn_register = tk.Button(btn_frame, text="Take Register", width=20, command=self.run_register_call)
        self.btn_register.pack(side=tk.LEFT, expand=True, padx=5, pady=5)
        
        self.btn_sentry = tk.Button(btn_frame, text="Toggle Sentry Mode", width=20, command=self.toggle_sentry_mode)
        self.btn_sentry.pack(side=tk.RIGHT, expand=True, padx=5, pady=5)
        
        # Start the video feed loop
        self.update()
        self.window.mainloop()

    def load_student_images(self):
        """Loads face encodings from images in the 'student_images' folder."""
        path = "student_images"
        if not os.path.exists(path):
            os.makedirs(path)
            messagebox.showinfo("Setup", "Created 'student_images' folder. Please add student photos to it.")
            return

        print("Loading known faces...")
        for filename in os.listdir(path):
            if filename.endswith((".jpg", ".png", ".jpeg")):
                image_path = os.path.join(path, filename)
                try:
                    student_image = face_recognition.load_image_file(image_path)
                    # Use the first face found in the image
                    face_encodings = face_recognition.face_encodings(student_image)
                    if face_encodings:
                        encoding = face_encodings[0]
                        self.known_face_encodings.append(encoding)
                        # Get student name from filename (e.g., "Elon_Musk.jpg" -> "Elon Musk")
                        self.known_face_names.append(os.path.splitext(filename)[0].replace("_", " "))
                    else:
                        print(f"Warning: No face found in {filename}. Skipping.")
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        print(f"Loaded {len(self.known_face_names)} known faces.")

    def run_register_call(self):
        """Identifies students present, calls out their names, and emails a report."""
        self.btn_register.config(state=tk.DISABLED, text="Registering...")
        # Run face recognition in a separate thread to avoid freezing the UI
        threading.Thread(target=self.process_register_call).start()

    def process_register_call(self):
        # Grab a single frame of video
        ret, frame = self.video_capture.read()
        if not ret:
            messagebox.showerror("Error", "Failed to capture image from webcam.")
            self.btn_register.config(state=tk.NORMAL, text="Take Register")
            return

        # Find all faces in the current frame
        face_locations = face_recognition.face_locations(frame)
        face_encodings = face_recognition.face_encodings(frame, face_locations)

        present_students = set()
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            if True in matches:
                first_match_index = matches.index(True)
                name = self.known_face_names[first_match_index]
            
            if name != "Unknown":
                present_students.add(name)

        # Call out names of present students
        if present_students:
            self.speak(f"Register call. The following {len(present_students)} students are present:")
            for student in sorted(list(present_students)):
                self.speak(student)
        else:
            self.speak("No students were recognized.")
            
        # Send email report
        absent_students = set(self.known_face_names) - present_students
        self.send_email(list(present_students), list(absent_students))

        # Re-enable the button
        self.window.after(0, self.enable_register_button)

    def enable_register_button(self):
        self.btn_register.config(state=tk.NORMAL, text="Take Register")

    def toggle_sentry_mode(self):
        """Activates or deactivates sentry mode."""
        self.sentry_mode = not self.sentry_mode
        if self.sentry_mode:
            self.btn_sentry.config(relief=tk.SUNKEN, text="Sentry Mode: ON")
            print("Sentry Mode Activated.")
            self.sentry_stop_event.clear()
            self.sentry_thread = threading.Thread(target=self.sentry_worker, daemon=True)
            self.sentry_thread.start()
            self.speak("Sentry mode activated.")
        else:
            self.sentry_stop_event.set()
            self.btn_sentry.config(relief=tk.RAISED, text="Toggle Sentry Mode")
            print("Sentry Mode Deactivated.")
            self.speak("Sentry mode deactivated.")

    def sentry_worker(self):
        """Processes frames for faces in a background thread."""
        last_seen_unknown = 0
        while not self.sentry_stop_event.is_set():
            frame_to_process = None
            with self.frame_lock:
                if self.latest_frame is not None:
                    # Work on a copy
                    frame_to_process = self.latest_frame.copy()

            if frame_to_process is None:
                time.sleep(0.05) # Wait for a frame
                continue

            # Find all faces in the current frame
            face_locations = face_recognition.face_locations(frame_to_process)
            face_encodings = face_recognition.face_encodings(frame_to_process, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                name = "Unknown"
                color = (0, 0, 255) # Red for unknown

                if True in matches:
                    first_match_index = matches.index(True)
                    name = self.known_face_names[first_match_index]
                    color = (0, 255, 0) # Green for known
                elif time.time() - last_seen_unknown > 5: # Avoid spamming
                    self.speak("Unauthorized person detected")
                    last_seen_unknown = time.time()

                # Draw a box around the face
                cv2.rectangle(self.latest_frame, (left, top), (right, bottom), color, 2)
                # Draw a label with a name below the face
                cv2.rectangle(self.latest_frame, (left, bottom - 25), (right, bottom), color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(self.latest_frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

    def update(self):
        """Main loop to update the video feed and run detection."""
        ret, frame = self.video_capture.read()
        if ret:
            with self.frame_lock:
                # Convert the image from BGR (OpenCV default) to RGB for face_recognition
                self.latest_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert the frame to a PhotoImage for Tkinter
            self.photo = ImageTk.PhotoImage(image=Image.fromarray(self.latest_frame))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        # Call update again after 15ms
        self.window.after(15, self.update)

    def send_email(self, present_list, absent_list):
        """Formats and sends an email with the attendance report."""
        now = datetime.datetime.now()
        subject = f"Attendance Report - {now.strftime('%Y-%m-%d %H:%M')}"
        
        body = f"""
        <html>
        <body>
            <h2>Attendance Report</h2>
            <p>Report generated on {now.strftime('%A, %B %d, %Y at %I:%M %p')}.</p>
            
            <h3>✅ Present Students ({len(present_list)})</h3>
            <ul>
                {''.join(f'<li>{name}</li>' for name in sorted(present_list))}
            </ul>

            <h3>❌ Absent Students ({len(absent_list)})</h3>
            <ul>
                {''.join(f'<li>{name}</li>' for name in sorted(absent_list))}
            </ul>
        </body>
        </html>
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = RECIPIENT_EMAIL
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))
            
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            text = msg.as_string()
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, text)
            server.quit()
            
            print(f"Email report sent successfully to {RECIPIENT_EMAIL}")
            messagebox.showinfo("Success", "Attendance report sent successfully!")

        except Exception as e:
            print(f"Failed to send email: {e}")
            messagebox.showerror("Email Error", f"Failed to send email. Check credentials and connection.\nError: {e}")

    def speak(self, text):
        """Uses the TTS engine to speak the given text."""
        try:
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
            
    def on_closing(self):
        """Release the webcam and destroy the window when closing."""
        print("Releasing resources...")
        self.video_capture.release()
        self.window.destroy()

if __name__ == "__main__":
    app = StudentRegisterApp(tk.Tk(), "Automated Student Register 📸")