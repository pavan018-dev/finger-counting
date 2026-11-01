# Real-Time Finger Counting System

A small Flask application that reads your webcam feed, detects one hand with MediaPipe, and displays the number of extended fingers in a polished browser interface.

## Features

- Live webcam streaming in the browser
- Real-time hand landmark detection via MediaPipe Tasks
- Counts zero through five raised fingers
- On-screen hand skeleton and live detection status
- Automatically downloads the hand-landmarker model if it is missing

## Requirements

- Python 3.9 or newer
- A webcam available to OpenCV

## Setup

1. Clone this repository and enter its folder.
2. Create and activate a virtual environment (recommended).
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the application:

   ```bash
   python finger_counter.py
   ```

5. Visit [http://localhost:5000](http://localhost:5000) in your browser and allow camera access if prompted.

## Deploy on Render

This repository includes `render.yaml`, so you can deploy it as a Render Blueprint:

1. In Render, select **New +** → **Blueprint** and connect this GitHub repository.
2. Review the detected `finger-counting` web service and create it.
3. Render installs the packages in `requirements.txt` and runs the Gunicorn start command from `render.yaml`.

The deployment has a `/health` endpoint for Render's health check.

> **Important:** Render runs the Python code on a remote server, which cannot access a visitor's webcam. The application will deploy successfully, but live finger detection works only when the server runs on a computer with a camera (for example, locally with `python finger_counter.py`). The hosted page explains this instead of continually attempting to read an unavailable camera.

## Project files

- `finger_counter.py` — Flask server, webcam capture, landmark detection, and finger-counting logic.
- `index.html` — browser dashboard for the live feed and count.
- `requirements.txt` — Python dependencies.
- `hand_landmarker.task` — MediaPipe hand-landmarker model.

## Notes

The application uses the first detected hand and is designed for local use. Good lighting and keeping your hand clearly in frame improve detection accuracy.

## License

No license has been specified for this project.
