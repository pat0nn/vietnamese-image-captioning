/**
 * Play audio from base64 encoded data
 * @param {string} base64Audio - Base64 encoded audio data
 * @param {Function} onStart - Callback when audio starts playing
 * @param {Function} onEnd - Callback when audio ends
 * @param {Function} onError - Callback when audio errors
 * @returns {HTMLAudioElement} Audio element
 */
export function playAudioFromBase64(base64Audio, onStart, onEnd, onError) {
  try {
    // Create audio element
    const audio = new Audio();
    
    // Set audio source from base64
    audio.src = `data:audio/mp3;base64,${base64Audio}`;
    
    // Set up event listeners
    if (onStart) {
      audio.addEventListener('playing', onStart);
    }
    
    if (onEnd) {
      audio.addEventListener('ended', onEnd);
    }
    
    if (onError) {
      audio.addEventListener('error', (error) => {
        console.error('Audio error:', error);
        onError(error);
      });
    }
    
    // Start playing
    const playPromise = audio.play();
    
    if (playPromise) {
      playPromise.catch((error) => {
        console.error('Play error:', error);
        if (onError) {
          onError(error);
        }
      });
    }
    
    return audio;
  } catch (error) {
    console.error('Audio creation error:', error);
    if (onError) {
      onError(error);
    }
    return null;
  }
}

/**
 * Stop an audio element
 * @param {HTMLAudioElement} audio - Audio element to stop
 */
export function stopAudio(audio) {
  if (!audio) return;
  
  try {
    audio.pause();
    audio.currentTime = 0;
  } catch (error) {
    console.error('Error stopping audio:', error);
  }
} 