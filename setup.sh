#!/bin/bash

# Create and activate virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt

# Create config.py from template if it doesn't exist
if [ ! -f config.py ]; then
    mv config.template.py config.py
    echo "Created config.py from template. Please update with your credentials."
fi

echo "Setup complete! Don't forget to:"
echo "1. Update config.py with your credentials"
echo "2. Install system dependencies (tesseract-ocr, mysql-server)"
echo "3. Place your YOLOv8 model file (license-plate-detector.pt) in the project root"
