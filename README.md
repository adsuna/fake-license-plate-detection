# Vehicle Recognition System

A comprehensive system for vehicle detection and verification that can identify license plates, vehicle make, model, and color, while also verifying the information against a registered vehicle database.

## Features

- License plate detection and OCR using YOLO and Tesseract
- Vehicle make, model, and color detection using Google's Gemini AI
- Indian state identification from license plate numbers
- Database verification for detecting fake/mismatched license plates
- User-friendly web interface using Streamlit

## Prerequisites

- Python 3.10
- MySQL Server
- Tesseract OCR
- CUDA-capable GPU (recommended for better performance)


## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fake-license-plate-detection.git
cd fake-license-plate-detection
```

2. Run the setup script:
```bash
./setup.sh
```

3. Configure the application:
   - Update `config.py` with your:
     - MySQL database credentials
     - Google API key
     - Model paths

4. Set up the database:
```sql
CREATE DATABASE reg_vehicles;
USE reg_vehicles;

CREATE TABLE vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    license_plate VARCHAR(20) NOT NULL,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    color VARCHAR(30) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

5. Download the model:
   - Place your trained `license-plate-detector.pt` model from [here](https://drive.google.com/file/d/1XHyNdpZI8eTiea3tn_sVIXhWV9Ys0GR0/view?usp=sharing) and place it in the project root directory

## Usage

1. Activate the virtual environment:
```bash
source venv/bin/activate  
```

2. Run the application:
```bash
streamlit run frontend.py
```

3. Access the web interface at `http://localhost:8501`


## Configuration

The `config.py` file contains sensitive information and should never be committed to git. Use it to store:
- Database credentials
- API keys
- Model paths

## License

This project is licensed under the GPL 3.0 License - see the LICENSE file for details.

