import ctypes
import ctypes.util
import os
import whisper

# Function to find and load the appropriate C library
def load_c_library():
    libc_name = None
    if os.name == 'nt':  # Windows
        libc_name = ctypes.util.find_library('msvcrt')
    else:  # Unix-like systems
        libc_name = ctypes.util.find_library('c')
    
    if libc_name is None:
        raise FileNotFoundError("Could not find the C library. Ensure the correct path is specified.")
    
    return ctypes.CDLL(libc_name)

# Load the C library
libc = load_c_library()

# Function to initialize and return the Whisper model
def load_whisper_model(model_name):
    return whisper.load_model(model_name)
