import torch
import numpy as np
from PIL import Image
from transformers import BlipProcessor, BlipForConditionalGeneration

def load_blip_model(model_dir="H:/MovieDesc/Modeling/blip_model"):
    """Load the pre-trained BLIP model for detailed visual descriptions of video frames."""
    processor = BlipProcessor.from_pretrained(model_dir)
    model = BlipForConditionalGeneration.from_pretrained(model_dir)
    model.eval()
    return {"processor": processor, "model": model}

def generate_caption(model, image, max_length=50, num_beams=5):
    """Generate a detailed caption for an image (e.g., video frame) using BLIP."""
    # Ensure image is in the correct format (PIL Image or NumPy array)
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    inputs = model["processor"](image, return_tensors="pt")
    with torch.no_grad():
        outputs = model["model"].generate(**inputs, max_length=max_length, num_beams=num_beams)
    return model["processor"].decode(outputs[0], skip_special_tokens=True)