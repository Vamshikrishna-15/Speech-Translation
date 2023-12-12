import os
import speech_recognition as sr
from flask import Flask, render_template, request, jsonify
from googletrans import Translator
from googletrans.constants import LANGUAGES
from gtts import gTTS
import datetime

app = Flask(__name__)

# Function to capture voice
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        # Recognize the user's speech
        query = r.recognize_google(audio, language='en-IN')

        # Detect the language of the recognized query
        lang_detector = Translator()
        detected_lang = lang_detector.detect(query)
        detected_lang_code = detected_lang.lang

        # Translate the query back to the detected language for printing
        translator = Translator()
        detected_text_to_translate = translator.translate(query, src='en', dest=detected_lang_code)
        detected_text = detected_text_to_translate.text

        return query, detected_lang_code, detected_text
    except Exception as e:
        print("Say that again, please...")
        return "None", None, None

def destination_language():
    print("Enter the language in which you want to convert (e.g., Hindi, English, etc.):")
    print()
    # Input destination language in which the user wants to translate
    to_lang = takecommand()[0]
    while to_lang == "None":
        print("Sorry, could not understand the language selection. Please try again.")
        to_lang = takecommand()[0]

    # Check if the destination language name is valid and get the corresponding language code
    to_lang_code = None
    for code, name in LANGUAGES.items():
        if to_lang.lower() in name.lower():
            to_lang_code = code
            break

    if to_lang_code is None:
        print("Invalid language name. Please enter a valid language.")
        return destination_language()

    return to_lang_code.lower()

# Function to get the language name from the language code
def get_language_name(code):
    return LANGUAGES[code]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/record', methods=['POST'])
def record():
    # Input from user
    # Make input to lowercase
    query, detected_lang, detected_text = takecommand()
    while query == "None" or detected_lang is None or detected_text is None:
        query, detected_lang, detected_text = takecommand()

    to_lang = destination_language()

    # Translating from detected language to destination language
    translator = Translator()
    text_to_translate = translator.translate(query, src=detected_lang, dest=to_lang)

    translated_text = text_to_translate.text

    # Get the detected language name from the detected language code
    detected_lang_name = get_language_name(detected_lang)

    # Using Google-Text-to-Speech (gTTS) to speak the translated text
    speak = gTTS(text=translated_text, lang=to_lang, slow=False)


    # Save the translated speech with the name of current date and time
    now = datetime.datetime.now()
    filename = now.strftime('%Y-%m-%d_%H-%M-%S') + '.mp3'
    audio_file_path = os.path.join('static', filename)
    speak.save(audio_file_path)

    # Response data to send back to the frontend
    response = {
        'detected_lang': detected_lang_name,
        'detected_text': detected_text,
        'to_lang': to_lang,
        'translated_text': translated_text,
        'audio_file': filename
    }
    return jsonify(response)
# Error handling for server-side exceptions
@app.errorhandler(Exception)
def handle_error(e):
    response = {
        'status': 'error',
        'message': str(e)
    }
    return jsonify(response), 500

if __name__ == '__main__':
    app.run(debug=True)
