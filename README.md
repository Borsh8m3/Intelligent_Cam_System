# Intelligent Cam System

## Introduction
The Intelligent Cam System is a modular surveillance camera designed to operate in demanding weather conditions. It combines a rugged hardware platform—featuring 360° rotation, environmental sensors, and inductive control—with a Python-based video analytics pipeline powered by OpenCV and the `face_recognition` library. The system continuously monitors its surroundings, localises people, and reacts automatically to changes in temperature, humidity, and precipitation.

## Key Features
- **360° camera movement** – dual servos provide full panoramic motion along the horizontal and vertical axes.
- **Weather protection** – a sealed enclosure with anti-condensation heating and a rain-activated wiper keeps the optics clear.
- **Environmental monitoring** – temperature, humidity, dew point, and rain intensity are measured in real time.
- **Real-time video analytics** – faces are detected, recognised, and logged for later review; unknown faces can be labelled semi-automatically.
- **Communication module** – live video can be streamed to an external processing unit or monitoring dashboard.

## System Architecture
### Hardware Layer
- Weather-resistant housing with the camera mounted on a two-axis gimbal.
- Two servomotors to control pan and tilt.
- A DHT11 sensor that monitors enclosure temperature and humidity.
- An inductively powered rain sensor connected through an ADC input.
- A heater or fan that activates when the calculated dew point is exceeded.
- A servo-driven wiper that runs when rainfall is detected.

### Software Layer
- **Enclosure control (MicroPython)** – `Insidecode.py` ingests sensor data and orchestrates the servos, heater, and status LED.
- **Video analysis (Python)** – the `Video detection` module uses OpenCV to load known face encodings, perform detection, and annotate the live preview.
- **Face database management** – new frames tagged as `Unknown` are stored for later review, enabling incremental updates to the gallery of known users.

## Repository Structure
```
Intelligent_Cam_System/
├── code/
│   ├── Insidecode.py          # MicroPython control logic for the enclosure
│   └── Video detection/
│       ├── main_video.py      # Main loop for face detection and logging
│       └── simple_facerec.py  # Helper class for encoding and recognising faces
├── documents/                 # Project documentation and schematics
├── Photographic documentation # Prototype photos
├── Case/                      # CAD / 3D-print files for the enclosure
└── ...
```

## Requirements
### MicroPython Module
- A MicroPython-compatible microcontroller board (e.g. Raspberry Pi Pico).
- Libraries: `machine`, `servo`, `dht`, `utime`, `math`.
- Sensors wired to the pins defined in `Insidecode.py`.

### Video Analysis Module
- Python 3.9 or newer.
- Packages: `opencv-python`, `face_recognition`, `numpy`.
- UVC-compatible camera.
- An `images/` directory containing reference face photos (`.jpg`/`.png`).

Set up a virtual environment and install the Python dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt  # Create the file based on the list above
```

## Usage
### Enclosure Module (MicroPython)
1. Upload `Insidecode.py` to the microcontroller.
2. Verify the peripherals are connected:
   - Servo (GPIO 0)
   - DHT11 sensor (GPIO 26)
   - Push button (GPIO 12)
   - Heater or relay output (GPIO 13)
   - Status LED (GPIO 25)
   - Rain sensor connected to ADC 27
3. Run the script. The heater activates once the dew point threshold is crossed, and the wiper engages when rain intensity rises above roughly 25% of the sensor’s range.

### Video Analysis and Face Recognition
1. Populate the `images/` directory with files named `First_Last.jpg`. Files starting with `Unknown` will be treated as new profiles.
2. Update the `encoding_folder` path in `main_video.py` so it points to the image directory on your machine.
3. Launch the application:
   ```bash
   python "code/Video detection"/main_video.py
   ```
4. The program opens the live preview, highlights recognised faces, and saves frames for unknown persons. After stopping the script you can rename the captured images to add them to the known gallery.

## Future Improvements
- Integrate with external alarm or IoT systems.
- Synchronise the face database between the edge device and a central server.
- Extend object detection to non-human entities (vehicles, animals, etc.).
- Monitor power supply health and report hardware diagnostics.

## License
This project is provided for educational use. Ensure you have the right to process the images of individuals in your face recognition workflow.
