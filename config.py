import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AI Service Configuration
    HUGGINGFACE_API_KEY = os.getenv('HUGGINGFACE_API_KEY')
    
    # Use only Hugging Face with WORKING models
    AI_PRIORITY = ['huggingface']
    
    # WORKING Hugging Face models (tested and available)
    HUGGINGFACE_MODELS = [
        "black-forest-labs/FLUX.1-schnell",
        "dataautogpt3/OpenDalleV1.1",
        "warp-ai/dalle-3"
    ]
    
    # Aspect Ratios
    ASPECT_RATIOS = {
        '1_1': (1024, 1024),
        '9_16': (720, 1280),
        '16_9': (1280, 720)
    }
    
    # Paths
    INPUT_ASSETS_DIR = "input_assets"
    OUTPUT_DIR = "output"