document.addEventListener('DOMContentLoaded', function () {
  document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch(this.action, {
      method: this.method,
      body: formData
    }).then(response => response.json())
      .then(data => {
        if (data.video_path) {
          const videoSource = document.getElementById('video-source');
          videoSource.src = data.video_path;
          const video = document.getElementById('uploaded-video');
          video.load();
          video.play();
          document.getElementById('transcribe-button').dataset.filePath = data.file_path;
          document.getElementById('video-section').style.display = 'block';
        }
      }).catch(error => console.error('Error:', error));
  });

  document.getElementById('transcribe-button').addEventListener('click', function() {
    const video = document.getElementById('uploaded-video');
    video.onended = function() {
      const filePath = document.getElementById('transcribe-button').dataset.filePath;
      const model = document.getElementById('model').value;
      const language = document.getElementById('language').value;
      const verbose = document.getElementById('verbose').checked;

      startTranscription(filePath, model, language, verbose);
    };
    video.play();
  });

  // Recording functionality
  let mediaRecorder;
  let audioChunks = [];
  let recordingTimer;
  let recordingStartTime;

  const recordButton = document.getElementById('record-button');
  const stopButton = document.getElementById('stop-button');
  const recordingTimerDisplay = document.getElementById('recording-timer');

  recordButton.addEventListener('click', async () => {
    audioChunks = [];
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
      const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
      const formData = new FormData();
      formData.append('audio', audioBlob);
      formData.append('language', 'en');
      formData.append('model', 'base.en');
      formData.append('verbose', false);

      fetch('/transcribe_audio', {
        method: 'POST',
        body: formData
      }).then(response => response.json())
        .then(data => {
          if (data.transcription_status) {
            document.getElementById('transcription-status').textContent = data.transcription_status;
          }
          if (data.transcribed_text) {
            document.getElementById('transcription-text').textContent = data.transcribed_text;
            document.getElementById('transcription-status').textContent = 'Transcription Completed';
          }
        }).catch(error => console.error('Error:', error));
    };

    mediaRecorder.start();
    recordingStartTime = Date.now();
    updateRecordingTimer();
    recordingTimer = setInterval(updateRecordingTimer, 1000);
    recordButton.style.display = 'none';
    stopButton.style.display = 'inline-block';
  });

  stopButton.addEventListener('click', () => {
    mediaRecorder.stop();
    clearInterval(recordingTimer);
    recordingTimerDisplay.textContent = '00:00';
    recordButton.style.display = 'inline-block';
    stopButton.style.display = 'none';
  });

  function updateRecordingTimer() {
    const elapsedTime = Date.now() - recordingStartTime;
    const seconds = Math.floor((elapsedTime / 1000) % 60);
    const minutes = Math.floor((elapsedTime / 1000 / 60) % 60);
    recordingTimerDisplay.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
  }
});

function startTranscription(filePath, model, language, verbose) {
  const formData = new FormData();
  formData.append('file_path', filePath);
  formData.append('model', model);
  formData.append('language', language);
  formData.append('verbose', verbose);
  
  fetch('/transcribe', {
    method: 'POST',
    body: formData
  }).then(response => response.json())
    .then(data => {
      if (data.transcription_status) {
        document.getElementById('transcription-status').textContent = data.transcription_status;
      }
      if (data.transcribed_text) {
        document.getElementById('transcription-text').textContent = data.transcribed_text;
        document.getElementById('transcription-status').textContent = 'Transcription Completed';
      }
    }).catch(error => console.error('Error:', error));
}
