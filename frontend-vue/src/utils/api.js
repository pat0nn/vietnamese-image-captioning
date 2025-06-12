import axios from 'axios';
import { API_URL } from '../constants';

// API base URL từ constants.js
// const API_URL = 'http://localhost:5000';

/**
 * Text-to-speech API request
 * @param {string} text - Text to convert to speech
 * @returns {Promise} Promise with audio data
 */
export async function textToSpeech(text) {
  try {
    const response = await axios.post(`${API_URL}/api/tts`, { text }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    throw error;
  }
} 