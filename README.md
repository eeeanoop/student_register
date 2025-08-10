# Student Register

A cross-platform attendance application that recognises students from webcam video using OpenCV's LBPH face recogniser. Place a clear photo of each student inside the `student_images` directory (the filename becomes the student's name).

## Running the app

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Add student photos to `student_images/`.
3. Start the program:
   ```bash
   python app.py
   ```
4. Click **Start roll call** to begin. Faces are announced once. Unknown visitors are reported as unauthorised. When finished, press **End roll call** to see present and absent students with thumbnails.

The application uses only pure-Python packages and runs on macOS and Windows without requiring `dlib`.
