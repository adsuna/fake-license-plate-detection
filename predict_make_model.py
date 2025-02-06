import google.generativeai as genai
from PIL import Image
import os
import sys
import json
from config import GOOGLE_API_KEY

genai.configure(api_key=GOOGLE_API_KEY)

def get_car_color(image_path):
    try:
        # Load the image
        image = Image.open(image_path)

        model = genai.GenerativeModel('gemini-1.5-flash-8b')

        prompt = "What is the color make and model of the car in this image? tell me 1 word for color, 1 for make, 1 for model in that order, 3 simple words in one line, dont separate with commas or anything."

        response = model.generate_content([prompt, image])

        # Split the response into color, make, and model
        color, make, model = response.text.strip().split()

        # Return the result as a JSON object
        return json.dumps({"color": color, "make": make, "model": model})

    except Exception as e:
        return json.dumps({"error": str(e)})

def main():
    # Check if image path is provided as command line argument
    if len(sys.argv) != 2:
        print("Usage: python predict_make_model.py <path_to_image>")
        print("Example: python predict_make_model.py car.jpg")
        sys.exit(1)

    # Get image path from command line argument
    image_path = sys.argv[1]

    # Verify if file exists
    if not os.path.exists(image_path):
        print("Error: Image file not found!")
        sys.exit(1)

    # Get and display the result
    result = get_car_color(image_path)
    print(result)

if __name__ == "__main__":
    main()
