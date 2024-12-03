# Real-time Threat Detection

## Table of Contents
- [Foreword](#foreword)
- [Quick Overview](#quick-overview)
- [System Features](#system-features)
  - [Real-time Nudity Detection](#1-real-time-nudity-detection)
  - [Text Extraction and Analysis](#2-text-extraction-and-analysis)
  - [Firebase Integration](#3-firebase-integration)
- [Setup](#setup)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
    - [Python Backend](#python-backend)
    - [iOS Notifier App](#ios-notifier-app)
- [Further Improvements](#further-improvements)
- [Contributors](#contributors)
- [License](#license)

---

## Foreword
This project is a real-time threat detection application focused on detecting NSFW content and toxic text from screen captures. It leverages a combination of deep learning models, text analysis pipelines, and Firebase for logging detections. The project serves as a prototype for advanced monitoring and real-time alert systems.

---

## Quick Overview
The project uses the following tools and technologies:
1. **NSFW Content Detection**: Utilizes a MobileNet-based deep learning model for identifying inappropriate content in screenshots.
2. **Text Extraction and Analysis**:
   - Extracts text using Tesseract OCR.
   - Translates text to English for uniform processing.
   - Detects toxicity using `transformers` with a pre-trained `unitary/toxic-bert` model.
3. **Firebase Integration**: Logs all detected events in a Firebase Realtime Database for centralized monitoring.
4. **iOS Notifier App**: Provides real-time notifications to parents when inappropriate content or text is detected.

---

## System Features

### 1. Real-time Nudity Detection
Detects inappropriate content in screenshots using a MobileNet-based pre-trained model. Frames are processed in real-time to evaluate their NSFW content.

### 2. Text Extraction and Analysis
- **Text Extraction**: Uses Tesseract OCR for extracting textual content from screenshots.
- **Translation**: Integrates Google Translate for language detection and translation to English.
- **Toxicity Detection**: Identifies toxic content using a pre-trained BERT model for text classification.

### 3. Firebase Integration
Logs the following events in the Firebase Realtime Database:
- NSFW content detections.
- Toxic text detections.

### 4. iOS Notifier App
The iOS app is designed for parents to receive real-time notifications about detections. It integrates directly with Firebase to fetch logs and display alerts.

---

## Setup

### Prerequisites
Ensure you have the following tools installed:
- Python 3.7 or higher.
- Required Python libraries listed in the `requirements.txt` file.
- Tesseract OCR installed and configured (update the path in the script if necessary).
- Firebase project with a Realtime Database and a Service Account JSON file.
- Xcode installed on a macOS system for building the iOS app.
- An Apple Developer account for deploying the iOS app.

---

### Installation

#### Python Backend
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/real-time-threat-detection.git
   cd real-time-threat-detection

   
2. Install required dependencies:

   ```bash
   pip install -r requirements.txt

3.  Set up Firebase:
   
   Replace parentmonitoringapp-67794-firebase-adminsdk-auet4-5ce60d0f75.json with your Firebase service account JSON file.

4. Update the databaseURL in the script to match your Firebase project URL.
   

5. Update the Tesseract OCR path in the script:

   ```bash
   pytesseract.pytesseract.tesseract_cmd = r'C:\Path\To\Tesseract-OCR\tesseract.exe'


6. Download the NSFW detection model and place it in the project directory:

   **At this point, you are able to test the detections and track them through the terminal**. When the script runs, it will process the input images and log any detected NSFW content or toxic text.

8. Run the script:
   ```bash
   python projet.py
