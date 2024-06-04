import os
import datetime
from glob import glob
import whisper
from torch import cuda, Generator
import colorama
from colorama import Back, Fore
from src.initialize_whisper import load_whisper_model

colorama.init(autoreset=True)

# Get the path
def get_path(path):
    glob_file = glob(path + '/*')
    return glob_file

# Main function
def transcribe(path, glob_file, model=None, language=None, verbose=False):
    """
    Transcribes audio files in a specified folder using OpenAI's Whisper model.

    Args:
        path (str): Path to the folder containing the audio files.
        glob_file (list): List of audio file paths to transcribe.
        model (str, optional): Name of the Whisper model to use for transcription.
            Defaults to None, which uses the default model.
        language (str, optional): Language code for transcription. Defaults to None,
            which enables automatic language detection.
        verbose (bool, optional): If True, enables verbose mode with detailed information
            during the transcription process. Defaults to False.

    Returns:
        str: The transcribed text without timestamps.

    Raises:
        RuntimeError: If an invalid file is encountered, it will be skipped.

    Notes:
        - The function downloads the specified model if not available locally.
        - The transcribed text files will be saved in a "transcriptions" folder
          within the specified path.
    """    
    # Check for GPU acceleration
    if cuda.is_available():
        Generator('cuda').manual_seed(42)
    else:
        Generator().manual_seed(42)
    
    # Load model using custom initializer
    model = load_whisper_model(model)
    
    # Start main loop
    files_transcribed = []
    full_transcription_text = []
    for file in glob_file:
        title = os.path.basename(file).split('.')[0]
        print(Back.CYAN + '\nTrying to transcribe file named: {}\U0001f550'.format(title))
        try:
            result = model.transcribe(
                file, 
                language=language, 
                verbose=verbose
            )
            files_transcribed.append(result)
            
            # Collect text segments without timestamps
            for segment in result['segments']:
                full_transcription_text.append(segment['text'])

            # Make the transcriptions folder if missing
            transcriptions_folder = os.path.join(os.path.dirname(path), 'transcriptions')
            os.makedirs(transcriptions_folder, exist_ok=True)
            
            # Save the transcription with timestamps to a file (optional)
            with open(os.path.join(transcriptions_folder, "{}.txt".format(title)), 'w', encoding='utf-8') as file:
                file.write(title)
                for segment in result['segments']:
                    file.write('\n[{} --> {}]:{}'.format(str(datetime.timedelta(seconds=segment['start'])), str(datetime.timedelta(seconds=segment['end'])), segment['text']))

        # Skip invalid files
        except RuntimeError:
            print(Fore.RED + 'Not a valid file, skipping.')
            pass
    
    # Check if any files were processed
    if len(files_transcribed) > 0:
        output_text = ' '.join(full_transcription_text)
        status_message = 'Finished transcription, {} files can be found in {}'.format(len(files_transcribed), transcriptions_folder)
    else:
        output_text = ''
        status_message = 'No files eligible for transcription, try adding audio or video files to this folder or choose another folder!'

    return output_text, status_message
