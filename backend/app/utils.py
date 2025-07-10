# app/utils.py (Enhanced cleanup)
import os
import base64
import io
import logging
import time # Import time for delays
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_directory(directory):
    """Creates a directory if it doesn't exist."""
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logger.error(f"Error creating directory {directory}: {str(e)}")
        raise

def image_to_base64(image):
    """Converts a PIL Image to a base64-encoded JPEG data URI."""
    # Note: This function isn't currently used in the main backend flow you provided.
    # Keep it if you plan to display frame thumbnails, otherwise it could be removed.
    try:
        buffered = io.BytesIO()
        # Ensure image is RGB before saving as JPEG
        if image.mode in ("RGBA", "P"):
             image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return f"data:image/jpeg;base64,{image_base64}"
    except Exception as e:
        logger.error(f"Error converting image to base64: {str(e)}")
        # Consider returning None instead of raising, depending on how it's used
        return None # Return None on error

def file_to_base64(file_path):
    """Converts a file's content to a raw base64-encoded string."""
    if not os.path.exists(file_path):
        logger.warning(f"File not found for base64 encoding: {file_path}")
        return None
    try:
        with open(file_path, "rb") as f:
            file_data = f.read()
            file_base64 = base64.b64encode(file_data).decode('utf-8')
            return file_base64
    except Exception as e:
        logger.error(f"Error converting file {file_path} to base64: {str(e)}")
         # Consider returning None instead of raising, to allow main flow to continue partially
        return None # Return None on error

def cleanup_files(file_paths: list[str]):
    """Attempts to remove a list of files, with retries for permission errors."""
    logger.info(f"Attempting to clean up files: {file_paths}")
    for file_path in file_paths:
        if file_path and isinstance(file_path, str) and os.path.exists(file_path):
            retries = 3
            delay = 0.5 # Initial delay in seconds
            for i in range(retries):
                try:
                    os.remove(file_path)
                    logger.info(f"Successfully removed temporary file: {file_path}")
                    break # Exit retry loop on success
                except PermissionError as pe:
                     # This often means the file is still locked by another process
                     if i < retries - 1:
                          logger.warning(f"PermissionError removing {file_path}. Retrying in {delay}s... ({i+1}/{retries})")
                          time.sleep(delay)
                          delay *= 2 # Exponential backoff for next retry
                     else:
                          # Log final failure after retries
                          logger.error(f"Failed to remove file {file_path} after {retries} attempts due to PermissionError: {pe}")
                except FileNotFoundError:
                    logger.warning(f"File {file_path} not found during cleanup attempt (already removed?).")
                    break # No need to retry if it's gone
                except Exception as e:
                    # Log other unexpected errors during removal
                    logger.error(f"Error removing file {file_path}: {str(e)}", exc_info=True)
                    break # Don't retry on other errors
        elif file_path and isinstance(file_path, str):
            # Log if the file path was provided but the file didn't exist initially
            # logger.debug(f"File not found for cleanup (already removed or never created?): {file_path}")
            pass # Avoid excessive logging for files that might intentionally not exist (e.g., silent audio)
        elif file_path:
             logger.warning(f"Invalid item in cleanup list (expected string path): {file_path}")