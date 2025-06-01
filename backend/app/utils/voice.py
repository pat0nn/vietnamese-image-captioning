# !git clone --branch add-vietnamese-xtts -q https://github.com/thinhlpg/TTS.git
# !pip install --use-deprecated=legacy-resolver -q -e TTS
#❗❗❗ IMPORTANT: Please restart runtime after install TTS

import os
import io
from google.cloud import texttospeech
import logging

# Initialize the Google Cloud TTS client
try:
    # Try to use default credentials first (recommended for Cloud Run)
    try:
        client = texttospeech.TextToSpeechClient()
        logging.info("Google Cloud TTS client initialized with default credentials")
    except Exception as default_cred_error:
        logging.warning(f"Could not initialize with default credentials: {str(default_cred_error)}")
        
        # Fallback to service account key file if available
        GCP_KEY_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
        
        if not GCP_KEY_PATH or not os.path.exists(GCP_KEY_PATH):
            # Fallback paths
            alt_paths = [
                "/app/vietnamese-image-captioning-dd16a6c19d7f.json",
                os.path.join(os.path.dirname(__file__), '..', '..', 'vietnamese-image-captioning-dd16a6c19d7f.json'),
                os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'vietnamese-image-captioning-dd16a6c19d7f.json'))
            ]
            for path in alt_paths:
                if os.path.exists(path):
                    GCP_KEY_PATH = path
                    break
        
        if GCP_KEY_PATH and os.path.exists(GCP_KEY_PATH):
            client = texttospeech.TextToSpeechClient.from_service_account_json(GCP_KEY_PATH)
            logging.info(f"Google Cloud TTS client initialized with key: {GCP_KEY_PATH}")
        else:
            raise Exception("No valid credentials found")
            
except Exception as e:
    logging.error(f"Error initializing Google Cloud TTS client: {str(e)}")
    logging.error("Please ensure the Google Cloud credentials are correctly set up")
    client = None

def caption_to_speech(text, output_wav_path=None):
    """
    Convert text to speech using Google Cloud TTS.
    
    Args:
        text (str): The text to convert to speech
        output_wav_path (str, optional): Path to save the output audio file. 
            If None, the audio data is returned without saving to file.
            
    Returns:
        bytes or None: If output_wav_path is None, returns the audio data as bytes.
                      If output_wav_path is provided, saves to file and returns None.
    """
    try:
        
        # Check if the client is initialized
        if client is None:
            logging.error("Error: Google Cloud TTS client not initialized")
            return None
            
        # Create the input text
        input_text = texttospeech.SynthesisInput(text=text)
        
        # Configure voice parameters
        voice = texttospeech.VoiceSelectionParams(
            language_code="vi-VN",
            name="vi-VN-Chirp3-HD-Despina",  # Using high-quality Vietnamese female voice
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )
        
        # Configure audio parameters
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            pitch=0.0,
            speaking_rate=0.9
        )
        
        # Generate speech
        response = client.synthesize_speech(
            input=input_text,
            voice=voice,
            audio_config=audio_config
        )
        
        audio_data = response.audio_content
        logging.info(f"Speech generation successful, audio size: {len(audio_data)} bytes")
        
        # If output path is provided, save the audio file
        if output_wav_path:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(output_wav_path) if os.path.dirname(output_wav_path) else '.', exist_ok=True)
            
            # Save the audio file
            with open(output_wav_path, "wb") as out:
                out.write(audio_data)
                logging.info(f"Audio saved to {output_wav_path}")
                return None
        
        # Otherwise, return the audio data as bytes
        return audio_data
            
    except Exception as e:
        logging.error(f"Error generating speech with Google Cloud TTS: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

# Example usage (will only run if this file is executed directly)
if __name__ == "__main__":
    # Test with default example
    test_text = "Xin chào, tôi là một công cụ có khả năng chuyển đổi văn bản thành giọng nói tự nhiên, được phát triển bởi nhóm Nón lá"
    
    # Example 1: Save to file
    output_path = "test_output.mp3"
    caption_to_speech(test_text, output_path)
    print(f"Audio saved to {output_path}")
    
    # Example 2: Get audio bytes
    audio_bytes = caption_to_speech(test_text)
    print(f"Generated audio data of size: {len(audio_bytes) if audio_bytes else 0} bytes")