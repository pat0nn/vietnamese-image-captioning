import axios from 'axios';
import { API_URL } from '../constants';

// API base URL từ constants.js
// const API_URL = 'http://localhost:5000';

/**
 * Get image caption from API
 * @param {FormData} formData - Form data containing image
 * @param {AbortSignal} signal - Optional signal to abort the request
 * @returns {Promise} Promise with caption data
 */
export async function getImageCaption(formData, signal) {
  try {
    const response = await axios.post(`${API_URL}/api/caption`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      signal: signal // Add signal for cancellation support
    });
    return response.data;
  } catch (error) {
    // Không log ra console nếu request bị hủy có chủ đích
    if (error.name === 'CanceledError' || error.name === 'AbortError') {
      // Propagate the abort error without logging
      throw error;
    }
    
    console.error('Error calling image caption API:', error);
    throw error;
  }
}

/**
 * Text-to-speech API request
 * @param {string} text - Text to convert to speech
 * @returns {Promise} Promise with audio data
 */
export async function textToSpeech(text) {
  try {
    const response = await axios.post(`${API_URL}/api/text-to-speech`, { text }, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error calling text-to-speech API:', error);
    throw error;
  }
}

/**
 * Contribute image and caption to API
 * @param {FormData} formData - Form data containing image and caption
 * @returns {Promise} Promise with response data
 */
export async function contributeImage(formData) {
  try {
    const response = await axios.post(`${API_URL}/api/contribute`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error calling contribute API:', error);
    throw error;
  }
}

/**
 * Submit rating for image caption
 * @param {string} imageId - Image ID to rate
 * @param {number} rating - Rating value (1-5)
 * @returns {Promise} Promise with response data
 */
export async function submitRating(imageId, rating) {
  try {
    const response = await axios.post(`${API_URL}/api/rate/${imageId}`, 
      { rating },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error submitting rating:', error);
    throw error;
  }
}

/**
 * Get user contributions
 * @returns {Promise} Promise with user contributions data
 */
export async function getUserContributions() {
  try {
    const response = await axios.get(`${API_URL}/api/user/contributions`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error getting user contributions:', error);
    throw error;
  }
}

/**
 * Update a contribution caption
 * @param {string} contributionId - ID of the contribution to update
 * @param {string} caption - New caption text
 * @returns {Promise} Promise with response data
 */
export async function updateContribution(contributionId, caption) {
  console.log(`Calling updateContribution API with ID: ${contributionId} and caption: ${caption}`);
  try {
    // Sử dụng endpoint chuẩn
    const response = await axios.put(`${API_URL}/api/user/contribution/${contributionId}`, 
      { userCaption: caption },
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
      }
    );
    return response.data;
  } catch (error) {
    console.error('Error updating contribution:', error);
    throw error;
  }
}

/**
 * Delete a contribution
 * @param {string} contributionId - ID of the contribution to delete
 * @returns {Promise} Promise with response data
 */
export async function deleteContribution(contributionId) {
  try {
    console.log(`Deleting contribution with ID: ${contributionId} via API endpoint`);
    const response = await axios.delete(`${API_URL}/api/contribution/${contributionId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error deleting contribution:', error);
    throw error;
  }
} 