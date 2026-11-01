# Real-Time Finger Counting System

A Flask-hosted web application that uses MediaPipe in the visitor's browser to detect one hand and display the number of extended fingers.

## Features

- Live browser webcam preview
- Real-time hand landmark detection via MediaPipe Tasks in the browser
- Counts zero through five raised fingers
- On-screen hand skeleton and live detection status
- Automatically downloads the hand-landmarker model if it is missing

## Requirements

- Python 3.9 or newer
- A browser that supports camera access

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

> **Camera privacy:** The hosted site requests the visitor's camera in their browser. Hand detection runs there, so Render never receives the camera feed. Use HTTPS (provided automatically by Render) for browser camera access.

## Project files

- `finger_counter.py` — Flask server for the web application.
- `index.html` — browser dashboard for the live feed and count.
- `requirements.txt` — Python dependencies.
- `hand_landmarker.task` — MediaPipe hand-landmarker model.

## Notes

The application uses the first detected hand. Good lighting and keeping your hand clearly in frame improve detection accuracy.

## License

No license has been specified for this project.
