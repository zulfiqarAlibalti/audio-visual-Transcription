import os
import whisper
from torch import cuda, Generator
import datetime

def transcribe_audio(file_path, model_name='base.en', language=None, verbose=False):
    # Check for GPU acceleration
    if cuda.is_available():
        Generator('cuda').manual_seed(42)
    else:
        Generator().manual_seed(42)

    # Load model
    model = whisper.load_model(model_name)

    # Start transcription
    try:
        result = model.transcribe(file_path, language=language, verbose=verbose)
        
        # Process the transcription result
        transcription_text = ""
        for segment in result['segments']:
            transcription_text += segment['text'] + " "

        return transcription_text.strip()

    except RuntimeError as e:
        return f"Error during transcription: {e}"

# Example usage:
# transcription = transcribe_audio("path_to_audio_file.wav")
# print(transcription)
