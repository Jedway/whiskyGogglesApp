## `README.md` Content

# Whisky Goggles - Bottle Recognition App

A computer vision application that identifies whisky bottles from images using OpenCV feature detection.

## Features
- Upload images through web interface for bottle identification
- Real-time bottle recognition using webcam
- High-accuracy matching using ORB feature detection
- Detailed bottle information display

## Prerequisites
- Python 3.8+
- Webcam (for real-time recognition)
- macOS/Linux/Windows

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whiskyGogglesApp.git
cd whiskyGogglesApp
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the data:
```bash
python src/data_preparation.py
```

## Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your settings:
```plaintext
FLASK_ENV=development
FLASK_APP=app.py
```

## Running the Application

### Web Interface
1. Start the Flask server:
```bash
flask run
```
2. Open `http://localhost:5000` in your browser

### Webcam Recognition
Run the webcam recognition script:
```bash
python src/webcam_identify.py
```

## Project Structure
```
whiskyGogglesApp/
├── app.py                  # Flask application
├── src/
│   ├── identification.py   # Core identification logic
│   ├── data_preparation.py # Dataset management
│   ├── config.py          # Configuration settings
│   └── webcam_identify.py # Webcam interface
├── data/
│   ├── bottle_dataset.xlsx # Bottle information
│   └── bottle_images/     # Reference images
├── static/                # Static web assets
└── templates/            # HTML templates
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)## `README.md` Content

````markdown
# Whisky Goggles - Bottle Recognition App

A computer vision application that identifies whisky bottles from images using OpenCV feature detection.

## Features
- Upload images through web interface for bottle identification
- Real-time bottle recognition using webcam
- High-accuracy matching using ORB feature detection
- Detailed bottle information display

## Prerequisites
- Python 3.8+
- Webcam (for real-time recognition)
- macOS/Linux/Windows

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/whiskyGogglesApp.git
cd whiskyGogglesApp
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

4. Set up the data:
```bash
python src/data_preparation.py
```

## Configuration
1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Update `.env` with your settings:
```plaintext
FLASK_ENV=development
FLASK_APP=app.py
```

## Running the Application

### Web Interface
1. Start the Flask server:
```bash
flask run
```
2. Open `http://localhost:5000` in your browser

### Webcam Recognition
Run the webcam recognition script:
```bash
python src/webcam_identify.py
```

## Project Structure
```
whiskyGogglesApp/
├── app.py                  # Flask application
├── src/
│   ├── identification.py   # Core identification logic
│   ├── data_preparation.py # Dataset management
│   ├── config.py          # Configuration settings
│   └── webcam_identify.py # Webcam interface
├── data/
│   ├── bottle_dataset.xlsx # Bottle information
│   └── bottle_images/     # Reference images
├── static/                # Static web assets
└── templates/            # HTML templates
```

## Contributing
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)