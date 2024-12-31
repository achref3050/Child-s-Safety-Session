import os
import time
import mss
import numpy as np
import cv2
from keras.models import load_model
from keras.applications.mobilenet_v2 import preprocess_input
from PIL import Image
import pytesseract
from transformers import pipeline
from nltk.tokenize import sent_tokenize
import re
from googletrans import Translator
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db


pytesseract.pytesseract.tesseract_cmd = r'path to tesseract.exe'  # Update this path to your installation

nsfw_model = load_model("nsfw_mobilenet2.224x224.h5") 

toxicity_model = pipeline("text-classification", model="unitary/toxic-bert")

translator = Translator()

cred = credentials.Certificate("path to your service account SDK.json")  # Update with your service account file path

# Firebase connection
firebase_connected = False
try:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'your Database Url'  # Replace with your actual Firebase Realtime Database URL and Not Firestore Database
    })
    firebase_connected = True
    print("Firebase connection successful!")
except Exception as e:
    print(f"Firebase connection failed: {e}")



from datetime import datetime

def log_detection_to_realtime_database(event_type, event_message):
    """Log detection event to Realtime Database."""
    if firebase_connected:
        try:
            ref = db.reference('detections')  
            ref.push({
                'event_type': event_type,
                'event_message': event_message,
                'timestamp': datetime.now().isoformat()  
            })
            print(f"Detection logged to Realtime Database: {event_type}")
        except Exception as e:
            print(f"Error logging to Realtime Database: {e}")
    else:
        print("Firebase not connected. Skipping logging.")




def is_nsfw(frame):
    """Check if the frame contains NSFW content using the pre-trained model."""
    frame_resized = cv2.resize(frame, (224, 224))
    frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    frame_rgb = preprocess_input(np.expand_dims(frame_rgb, axis=0))
    prediction = nsfw_model.predict(frame_rgb)[0][0]
    return prediction > 0.5  

def preprocess_frame_for_ocr(frame):
    """Preprocess frame for OCR to improve text extraction."""
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    threshold_frame = cv2.adaptiveThreshold(
        gray_frame, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    return threshold_frame

def extract_text(frame):
    """Extract text from a frame using Tesseract OCR."""
    processed_frame = preprocess_frame_for_ocr(frame)
    custom_config = r'--oem 3 --psm 6'  # Optimize OCR configuration
    text = pytesseract.image_to_string(processed_frame, config=custom_config)
    return text.strip()

def clean_text(text):
    """Clean extracted text to remove unwanted characters and symbols."""
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Remove non-ASCII characters
    return re.sub(r'[^a-zA-Z0-9\s]', '', text).strip()

def chunk_text(text, max_length=512):
    """Split long text into smaller chunks for analysis."""
    sentences = sent_tokenize(text)
    chunks, current_chunk = [], ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_length:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def detect_toxicity(text):
    """Detect toxicity in the provided text using the toxicity model."""
    if not text:
        return None  
    chunks = chunk_text(text)
    toxicity_scores = []
    for chunk in chunks:
        result = toxicity_model(chunk)
        toxicity_scores.append(result[0]['score'])
    return max(toxicity_scores)  

def translate_to_english(text):
    """
    Translate text to English using Google Translate API.
    """
    try:
        # Translate text to English
        translated = translator.translate(text, src='auto', dest='en')
        return translated.text
    except Exception as e:
        print(f"Translation error: {e}")
        return text  


def process_frames(interval=1):
    """Capture frames, analyze nudity, extract text, translate to English, and detect toxicity."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]  
        print("Starting combined nudity and toxicity detection...")

        try:
            while True:
                # Capture frame
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)  

                # Step 1: Nudity Detection
                if is_nsfw(frame):
                    print("Warning: NSFW Content Detected!")
                    log_detection_to_realtime_database("NSFW_DETECTED", "Nudity detected in the frame.")
                else:
                    print("Content is safe.")

                # Step 2: Text Extraction
                extracted_text = extract_text(frame)
                cleaned_text = clean_text(extracted_text)

                if cleaned_text:
                    # Step 3: Translate Text to English
                    translated_text = translate_to_english(cleaned_text)
                    print(f"Translated Text: {translated_text}")

                    # Step 4: Toxicity Detection
                    toxicity_score = detect_toxicity(translated_text)
                    print(f"Toxicity Score: {toxicity_score:.2f}")

                    if toxicity_score > 0.5:  
                        print("Warning: Toxic Content Detected!")
                        
                        log_detection_to_realtime_database("TOXIC_TEXT", "Toxicity detected in the text.")
                else:
                    print("No text extracted from screenshot.")

                
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nProcess interrupted by user. Exiting.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    
    if firebase_connected:
        process_frames(interval=10)
    else:
        print("Firebase connection failed. Exiting.")
