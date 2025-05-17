from flask import Blueprint, request, jsonify, send_file
import os
import io
import base64
from flask import Blueprint, request, jsonify, send_file
from app.utils.voice import caption_to_speech

tts_bp = Blueprint('tts', __name__)

@tts_bp.route('/text-to-speech', methods=['POST'])
@tts_bp.route('/api/text-to-speech', methods=['POST'])
def text_to_speech():
    print(f"Received text-to-speech request at {request.path}")
    
    try:
        data = request.json
        if not data:
            print("Error: No JSON data received in request")
            return jsonify({'error': 'No JSON data received'}), 400
            
        text = data.get('text')
        print(f"Received text for TTS: {text[:50]}..." if text else "No text received")
        
        if not text:
            return jsonify({'error': 'Text is required'}), 400
        
        # Generate audio from text
        print("Calling caption_to_speech function...")
        audio_data = caption_to_speech(text)
        
        if audio_data:
            print(f"Audio data received, size: {len(audio_data)} bytes")
            
            # Return audio data as base64 (matching the original implementation)
            audio_data_base64 = base64.b64encode(audio_data).decode('utf-8')
            print(f"Encoded audio data to base64, length: {len(audio_data_base64)}")
            
            return jsonify({
                'success': True,
                'audio': audio_data_base64
            })
        else:
            print("Error: caption_to_speech returned None")
            return jsonify({'error': 'Failed to generate speech. Check server logs for details.'}), 500
            
    except Exception as e:
        import traceback
        print(f"Error in text-to-speech route: {str(e)}")
        traceback.print_exc()
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@tts_bp.route('/text-to-speech', methods=['GET'])
def text_to_speech_redirect():
    print(f"Redirecting from GET /text-to-speech to POST /api/text-to-speech")
    return jsonify({'error': 'Use POST method with JSON body containing text field'}), 405
