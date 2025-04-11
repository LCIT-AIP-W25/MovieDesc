// Log to confirm the script is loaded
console.log("script.js loaded successfully");

// Fallback in case DOMContentLoaded doesn't fire
setTimeout(() => {
  if (!window.domLoaded) {
    console.warn("DOMContentLoaded did not fire, running initialization manually");
    initializeApp();
  }
}, 5000);

document.addEventListener('DOMContentLoaded', () => {
  console.log("DOM fully loaded");
  window.domLoaded = true;
  initializeApp();
});
function initializeApp() {
  console.log("Initializing app");

  // DOM Elements
  const introSection = document.getElementById('introSection');
  const mainSection = document.getElementById('mainSection');
  const videoSection = document.getElementById('videoSection');
  const videoInput = document.getElementById('videoInput');
  const fileNameDisplay = document.getElementById('fileNameDisplay');
  const triggerFileInput = document.getElementById('triggerFileInput');
  const addAudioDescCheckbox = document.getElementById('addAudioDescCheckbox');
  let processButton = document.getElementById('processButton');
  const loadingSpinner = document.getElementById('loadingSpinner');
  const progressText = document.getElementById('progressText');
  const outputVideo = document.getElementById('outputVideo');
  const downloadLink = document.getElementById('downloadLink');
  const theaterAmbiance = document.getElementById('theaterAmbiance');
  const transitionSound = document.getElementById('transitionSound');
  const homeButton = document.getElementById('homeButton');

  // Debug: Verify elements exist
  console.log("Checking for processButton...");
  if (!processButton) {
    console.error("processButton element not found with getElementById! Trying querySelector...");
    processButton = document.querySelector('#processButton');
    if (!processButton) {
      console.error("processButton still not found with querySelector! Check the ID in index.html.");
    } else {
      console.log("processButton found with querySelector:", processButton);
    }
  } else {
    console.log("processButton element found with getElementById:", processButton);
  }

  // Attach event listener immediately after finding the button
  if (processButton) {
    console.log("Attaching event listener to processButton");
    processButton.addEventListener('click', async (e) => {
      e.preventDefault();
      console.log("Process Video button clicked");

      // Step 1: Validate the file
      const file = videoInput.files[0];
      if (!file) {
        speak("No file selected. Please select an MP4 video file to upload.", "NoFileSelected");
        console.log("No file selected");
        return;
      }
      if (!file.type.startsWith('video/mp4')) {
        speak("Invalid file format. Please upload an MP4 video file.", "InvalidFileFormat");
        console.log("Invalid file format:", file.type);
        return;
      }
      console.log("File validated:", file.name, file.type);

      // Step 2: Update UI (show spinner, disable button, transition)
      try {
        speak("Your video has been uploaded. Our AI is now creating a cinematic experience for you. Please wait.", "VideoUploaded");
        console.log("Announced video upload");

        if (!loadingSpinner || !mainSection || !videoSection || !progressText) {
          console.error("One or more UI elements not found!");
          speak("An error occurred with the page layout. Please refresh the page.", "LayoutError");
          return;
        }

        loadingSpinner.classList.remove('d-none');
        processButton.disabled = true;
        progressText.textContent = "Processing video...";
        console.log("Spinner shown, button disabled");

        mainSection.classList.add('d-none');
        videoSection.classList.remove('d-none');
        videoSection.style.opacity = '0';
        setTimeout(() => {
          videoSection.style.transition = 'opacity 0.5s ease';
          videoSection.style.opacity = '1';
          console.log("Transitioned to video section");
        }, 100);
      } catch (error) {
        console.error("Error updating UI:", error);
        speak("An error occurred while preparing the UI. Please try again.", "UIError");
        loadingSpinner.classList.add('d-none');
        processButton.disabled = false;
        return;
      }

      // Step 3: Simulate progress (for debugging, we’ll keep this short)
      try {
        let progress = 0;
        const progressInterval = setInterval(() => {
          progress += 20;
          if (progress <= 80) {
            progressText.textContent = `Processing video... ${progress}% complete`;
            speak(`${progress}% complete.`, "ProgressUpdate");
            console.log(`Progress: ${progress}%`);
          }
        }, 2000);

        // Step 4: Make API call to backend
        const backendUrl = 'http://localhost:8000/process-video/';
        console.log("Attempting to process video at:", backendUrl);

        // Prepare form data
        const formData = new FormData();
        formData.append('file', file);
        formData.append('add_audio_desc', addAudioDescCheckbox.checked);
        console.log("Form data prepared");

        // Make API call
        let response;
        try {
          response = await fetch(backendUrl, {
            method: 'POST',
            body: formData,
          });
        } catch (error) {
          clearInterval(progressInterval);
          progressText.textContent = "Error: Failed to connect to the backend.";
          speak("Failed to connect to the backend. Please ensure the backend is running on http://localhost:8000.", "BackendError");
          console.error("Backend connectivity error:", error.message);
          loadingSpinner.classList.add('d-none');
          processButton.disabled = false;
          return;
        }

        clearInterval(progressInterval);
        if (!response.ok) {
          throw new Error('Failed to process video: ' + response.statusText);
        }

        const data = await response.json();
        console.log("API response received:", data);

        // Step 5: Update UI with processed video
        progressText.textContent = "Processing video... 100% complete";
        speak("Processing complete. Your cinematic experience is ready.", "ProcessingComplete");

        fadeOutAudio(theaterAmbiance, 3000);
        console.log("Fading out ambient sound");

        outputVideo.src = data.output_video;
        outputVideo.load();
        outputVideo.onloadeddata = () => {
          console.log("Video loaded successfully for streaming.");
        };
        outputVideo.onerror = (e) => {
          console.error("Error loading video:", e);
          speak("Error loading the video for playback. Please try downloading it instead.", "VideoLoadError");
        };

        downloadLink.href = data.output_video;
        downloadLink.setAttribute('download', 'processed_video.mp4');
        console.log("Download link set up");

        outputVideo.focus();
        speak("Your cinematic experience is ready. Press Enter to play the video, or Tab to the download button to save it.", "VideoReady");
      } catch (error) {
        console.error("Error during processing:", error.message);
        progressText.textContent = "Error processing video: " + error.message;
        speak(`Error processing video: ${error.message}. Please try again.`, "ProcessingError");
      } finally {
        loadingSpinner.classList.add('d-none');
        processButton.disabled = false;
        console.log("Re-enabled Process Video button");
      }
    });
  } else {
    console.error("Cannot attach event listener: processButton is null");
  }

  if (!triggerFileInput) {
    console.error("triggerFileInput element not found!");
  }
  if (!videoInput) {
    console.error("videoInput element not found!");
  }

  // Speech Synthesis Setup
  const synth = window.speechSynthesis;
  let voices = [];
  let cinematicVoice = null;

  function loadVoices() {
    voices = synth.getVoices();
    cinematicVoice = voices.find(voice => voice.name.includes('Microsoft David') || voice.name.includes('Google US English Male')) || voices[0];
  }

  loadVoices();
  if (synth.onvoiceschanged !== undefined) {
    synth.onvoiceschanged = loadVoices;
  }

  function speak(text, id, pitch = 0.8, rate = 0.8) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.voice = cinematicVoice;
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.volume = 1.0;
    utterance.id = id;
    synth.speak(utterance);
  }

  // Function to fade out the ambient sound
  function fadeOutAudio(audio, duration = 3000) {
    const initialVolume = audio.volume;
    const step = initialVolume / (duration / 100); // Decrease volume every 100ms
    const fadeInterval = setInterval(() => {
      if (audio.volume > step) {
        audio.volume = Math.max(0, audio.volume - step);
      } else {
        audio.volume = 0;
        audio.pause();
        clearInterval(fadeInterval);
      }
    }, 100);
  }

  // Play Transition Sound and Delay Ambient Sound
  window.addEventListener('load', () => {
    transitionSound.volume = 0.5;
    transitionSound.play().catch(e => console.error("Error playing transition sound:", e));

    setTimeout(() => {
      speak("SenseTheScene", "SenseTheScene", 1.2, 0.7);
    }, 2500);

    setTimeout(() => {
      theaterAmbiance.volume = 0.1;
      theaterAmbiance.play().catch(e => console.error("Error playing ambiance:", e));
    }, 4000);

    setTimeout(() => {
      if (!introSection || !mainSection) {
        console.error("introSection or mainSection not found!");
        return;
      }
      introSection.classList.add('d-none');
      mainSection.classList.remove('d-none');
      mainSection.style.opacity = '0';
      setTimeout(() => {
        mainSection.style.transition = 'opacity 0.5s ease';
        mainSection.style.opacity = '1';
        speak("Welcome to Movie Descriptor, an AI-powered cinematic experience for the visually impaired. Use the Tab key to navigate to the upload field and select a video to begin.", "WelcomeMessage");
        if (fileNameDisplay) {
          fileNameDisplay.focus();
        } else {
          console.error("fileNameDisplay not found!");
        }
      }, 100);
    }, 4000);
  });

  // Trigger File Input on Arrow Button Click
  if (triggerFileInput && videoInput) {
    triggerFileInput.addEventListener('click', () => {
      console.log("Upload button clicked");
      videoInput.click();
    });

    triggerFileInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        console.log("Enter key pressed on upload button");
        videoInput.click();
      }
    });
  }

  // Update File Name Display When a File is Selected
  if (videoInput) {
    videoInput.addEventListener('change', () => {
      console.log("File input changed");
      const file = videoInput.files[0];
      if (file) {
        fileNameDisplay.value = file.name;
        speak(`File selected: ${file.name}. Press the Process Video button to continue.`, "FileSelected");
        if (processButton) {
          processButton.focus();
        } else {
          console.error("processButton not found for focusing!");
        }
      } else {
        fileNameDisplay.value = '';
        fileNameDisplay.placeholder = 'Upload an MP4 video...';
      }
    });
  }

  // Home Button Functionality
  if (homeButton) {
    homeButton.addEventListener('click', () => {
      videoSection.classList.add('d-none');
      mainSection.classList.remove('d-none');
      mainSection.style.opacity = '0';
      setTimeout(() => {
        mainSection.style.transition = 'opacity 0.5s ease';
        mainSection.style.opacity = '1';
        speak("Returned to the home page. Use the Tab key to navigate to the upload field.", "HomeNavigation");
        if (fileNameDisplay) {
          fileNameDisplay.focus();
        } else {
          console.error("fileNameDisplay not found!");
        }
        videoInput.value = '';
        fileNameDisplay.value = '';
        fileNameDisplay.placeholder = 'Upload an MP4 video...';
        outputVideo.src = '';
        if (theaterAmbiance.paused) {
          theaterAmbiance.volume = 0.1;
          theaterAmbiance.play().catch(e => console.error("Error playing ambiance:", e));
        }
      }, 100);
    });
  }

  console.log("Script initialization complete");
}