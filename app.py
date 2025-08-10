import tkinter as tk
from tkinter import messagebox
import os
import time
from typing import List, Dict

import cv2
import numpy as np
from PIL import Image, ImageTk
import pyttsx3


class StudentRegisterApp:
    """Simple student register using OpenCV's LBPH recognizer.

    Images of students should be placed in ``student_images``.  The filename
    (without extension) is used as the student's name.
    """

    def __init__(self, window: tk.Tk) -> None:
        self.window = window
        self.window.title("Automated Student Register")

        # --- Setup models ---
        self.detector = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()

        self.names: List[str] = []
        self.image_paths: Dict[str, str] = {}
        self._train_recognizer()

        # --- Video capture and UI ---
        self.cap = cv2.VideoCapture(0)
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 640)
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 480)

        self.canvas = tk.Canvas(window, width=width, height=height)
        self.canvas.pack()

        btn_frame = tk.Frame(window)
        btn_frame.pack(fill=tk.X)

        self.start_btn = tk.Button(btn_frame, text="Start roll call", command=self.start_roll_call)
        self.start_btn.pack(side=tk.LEFT, expand=True, padx=5, pady=5)

        self.end_btn = tk.Button(btn_frame, text="End roll call", command=self.end_roll_call, state=tk.DISABLED)
        self.end_btn.pack(side=tk.RIGHT, expand=True, padx=5, pady=5)

        self.tts = pyttsx3.init()
        self.capturing = False
        self.recognized: set[str] = set()
        self.last_unauthorized = 0.0

        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        self._update_frame()

    # ------------------------------------------------------------------
    def _train_recognizer(self) -> None:
        """Load images from disk and train the LBPH recognizer."""
        path = "student_images"
        if not os.path.exists(path):
            os.makedirs(path)
            messagebox.showinfo(
                "Setup", "Created 'student_images' folder. Add student photos and restart."
            )
            return

        faces: List[np.ndarray] = []
        labels: List[int] = []
        for idx, filename in enumerate(sorted(os.listdir(path))):
            if not filename.lower().endswith((".jpg", ".jpeg", ".png")):
                continue
            name = os.path.splitext(filename)[0]
            img_path = os.path.join(path, filename)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                print(f"Unable to read {filename}, skipping")
                continue
            detected = self.detector.detectMultiScale(img)
            if len(detected) == 0:
                print(f"No face found in {filename}, skipping")
                continue
            x, y, w, h = detected[0]
            faces.append(img[y : y + h, x : x + w])
            labels.append(idx)
            self.names.append(name)
            self.image_paths[name] = img_path

        if faces:
            self.recognizer.train(faces, np.array(labels))
        else:
            messagebox.showwarning("Warning", "No student images found for training")

    # ------------------------------------------------------------------
    def start_roll_call(self) -> None:
        self.recognized.clear()
        self.capturing = True
        self.start_btn.config(state=tk.DISABLED)
        self.end_btn.config(state=tk.NORMAL)

    # ------------------------------------------------------------------
    def end_roll_call(self) -> None:
        self.capturing = False
        self.start_btn.config(state=tk.NORMAL)
        self.end_btn.config(state=tk.DISABLED)

        present = sorted(self.recognized)
        absent = [name for name in self.names if name not in self.recognized]

        result = tk.Toplevel(self.window)
        result.title("Roll call results")

        tk.Label(result, text="Present", font=("Arial", 14, "bold")).pack()
        present_frame = tk.Frame(result)
        present_frame.pack()
        self._populate_results(present_frame, present)

        tk.Label(result, text="Absent", font=("Arial", 14, "bold")).pack()
        absent_frame = tk.Frame(result)
        absent_frame.pack()
        self._populate_results(absent_frame, absent)

    # ------------------------------------------------------------------
    def _populate_results(self, parent: tk.Frame, names: List[str]) -> None:
        images: List[ImageTk.PhotoImage] = []
        for name in names:
            path = self.image_paths.get(name)
            if not path:
                continue
            img = Image.open(path)
            img.thumbnail((80, 80))
            photo = ImageTk.PhotoImage(img)
            images.append(photo)
            row = tk.Frame(parent)
            row.pack(anchor=tk.W, padx=5, pady=2)
            tk.Label(row, image=photo).pack(side=tk.LEFT)
            tk.Label(row, text=name).pack(side=tk.LEFT, padx=5)
        parent.images = images  # prevent garbage collection

    # ------------------------------------------------------------------
    def _update_frame(self) -> None:
        ret, frame = self.cap.read()
        if ret:
            display = frame.copy()
            if self.capturing and self.names:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = self.detector.detectMultiScale(gray, 1.1, 4)
                for (x, y, w, h) in faces:
                    roi = gray[y : y + h, x : x + w]
                    label, confidence = self.recognizer.predict(roi)
                    if confidence < 80:
                        name = self.names[label]
                        if name not in self.recognized:
                            self.recognized.add(name)
                            self._speak(name)
                        color = (0, 255, 0)
                        cv2.putText(display, name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    else:
                        color = (0, 0, 255)
                        if time.time() - self.last_unauthorized > 5:
                            self._speak("unauthorized")
                            self.last_unauthorized = time.time()
                        cv2.putText(display, "Unknown", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
                    cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)

            image = cv2.cvtColor(display, cv2.COLOR_BGR2RGB)
            self.photo = ImageTk.PhotoImage(Image.fromarray(image))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

        self.window.after(30, self._update_frame)

    # ------------------------------------------------------------------
    def _speak(self, text: str) -> None:
        try:
            self.tts.say(text)
            self.tts.runAndWait()
        except Exception as exc:
            print(f"TTS error: {exc}")

    # ------------------------------------------------------------------
    def on_closing(self) -> None:
        self.capturing = False
        self.cap.release()
        self.window.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = StudentRegisterApp(root)
    root.mainloop()
