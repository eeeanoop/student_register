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

## Optional face verification

For stronger security, the app can verify faces using embeddings. This
requires the `face_recognition` package (and its dependency `dlib`) or an
equivalent OpenCV DNN face recognition model. When installed, embeddings
for all student photos are computed at start-up and a detected face is
accepted only if its embedding is within a small distance of the stored
embedding (cutoff ≈ 0.6).

To enable this mode install the extra dependency:

```bash
pip install face_recognition
```

Place the required model files if using an alternative DNN approach.
The application will automatically use embeddings when the dependency is
available; otherwise it falls back to the LBPH recogniser alone.
