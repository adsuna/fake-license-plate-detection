import streamlit as st
import cv2
import pytesseract
import subprocess
import json
import numpy as np
import torch
from ultralytics import YOLO
import os
import re
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG, MODEL_PATH

torch.classes.__path__ = [os.path.join(torch.__path__[0], torch.classes.__file__)] 

def load_model(model_path):
    """Load the trained YOLOv8 model for license plate detection."""
    return YOLO(model_path)

def detect_license_plate(model, image):
    """Detect license plate using YOLOv8 model and extract text with OCR."""
    results = model(image)  # YOLOv8 inference
    
    for result in results:
        boxes = result.boxes.xyxy  # Bounding box coordinates
        for box in boxes:
            x1, y1, x2, y2 = map(int, box)
            plate_crop = image[y1:y2, x1:x2]
            gray = cv2.cvtColor(plate_crop, cv2.COLOR_BGR2GRAY)
            text = pytesseract.image_to_string(gray, config='--psm 8')
            cleaned_text = re.sub(r'[^A-Za-z0-9]', '', text).upper()  # Remove special characters and convert to uppercase
            return cleaned_text
    
    return "License plate not detected"

def detect_vehicle_model_and_color(image_path):
    """Call the existing script to detect vehicle model and color."""
    try:
        result = subprocess.run(["python", "predict_make_model.py", image_path], capture_output=True, text=True)
        output = result.stdout.strip()
        data = json.loads(output)
        return data.get("make", "Unknown Make"), data.get("model", "Unknown Model"), data.get("color", "Unknown Color")
    except Exception as e:
        st.error(f"Error running model detection: {e}")
        return "Unknown Make", "Unknown Model", "Unknown Color"

def create_db_connection():
    """Create a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        st.error(f"Error connecting to MySQL Database: {e}")
        return None

def verify_vehicle_details(plate_number, make, model, color):
    """Verify vehicle details against the database."""
    connection = create_db_connection()
    if not connection:
        return False, "Database connection failed"

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
        SELECT * FROM vehicles 
        WHERE license_plate = %s
        """
        cursor.execute(query, (plate_number,))
        result = cursor.fetchone()

        if not result:
            return False, "License plate not found in database"

        # Check for mismatches
        mismatches = []
        if result['make'].lower() != make.lower():
            mismatches.append("make")
        if result['model'].lower() != model.lower():
            mismatches.append("model")
        if result['color'].lower() != color.lower():
            mismatches.append("color")

        if mismatches:
            return False, f"Mismatch detected in: {', '.join(mismatches)}"

        return True, "Vehicle details verified"

    except Error as e:
        return False, f"Database error: {e}"
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

def get_state_from_plate(plate_number):
    """Get the Indian state name from license plate code."""
    state_codes = {
        'AP': 'Andhra Pradesh',
        'AR': 'Arunachal Pradesh',
        'AS': 'Assam',
        'BR': 'Bihar',
        'CG': 'Chhattisgarh',
        'DL': 'Delhi',
        'GA': 'Goa',
        'GJ': 'Gujarat',
        'HR': 'Haryana',
        'HP': 'Himachal Pradesh',
        'JK': 'Jammu and Kashmir',
        'JH': 'Jharkhand',
        'KA': 'Karnataka',
        'KL': 'Kerala',
        'MP': 'Madhya Pradesh',
        'MH': 'Maharashtra',
        'MN': 'Manipur',
        'ML': 'Meghalaya',
        'MZ': 'Mizoram',
        'NL': 'Nagaland',
        'OD': 'Odisha',
        'PB': 'Punjab',
        'RJ': 'Rajasthan',
        'SK': 'Sikkim',
        'TN': 'Tamil Nadu',
        'TS': 'Telangana',
        'TR': 'Tripura',
        'UP': 'Uttar Pradesh',
        'UK': 'Uttarakhand',
        'WB': 'West Bengal',
        '22': 'Bharat',
    }
    
    if len(plate_number) >= 2:
        state_code = plate_number[:2]
        return state_codes.get(state_code, "Unknown State")
    return "State Code Invalid"

def main():
    st.title("Vehicle Recognition System")
    st.write("Upload an image to detect the license plate, car make, model, and color.")
    
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
        
        model = load_model(MODEL_PATH)
        
        with torch.no_grad():  # Prevent potential torch-related errors
            plate_number = detect_license_plate(model, image)
        
        # Get and display state information
        state_name = get_state_from_plate(plate_number)
        st.write(f"**License Plate:** {plate_number}")
        st.write(f"**Registered State:** {state_name}")
        
        image_path = "temp.jpg"
        cv2.imwrite(image_path, image)  # Save temp file for script compatibility
        vehicle_make, vehicle_model, vehicle_color = detect_vehicle_model_and_color(image_path)
        
        st.write(f"**Vehicle Make:** {vehicle_make}")
        st.write(f"**Vehicle Model:** {vehicle_model}")
        st.write(f"**Vehicle Color:** {vehicle_color}")
        
        # Verify against database
        is_verified, message = verify_vehicle_details(plate_number, vehicle_make, vehicle_model, vehicle_color)
        
        if not is_verified:
            st.markdown(
                f"""
                <div style='background-color: #ff4444; padding: 20px; border-radius: 10px;'>
                    <h2 style='color: white; text-align: center;'>⚠️ FAKE LICENSE PLATE DETECTED ⚠️</h2>
                    <p style='color: white; text-align: center;'>{message}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.success("Vehicle details verified successfully!")

if __name__ == "__main__":
    main()