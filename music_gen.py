from models.color_analysis import extract_dominant_colors
from models.Object_detection import detect_objects
from models.scene_recog_pretrained import predict_image_category

from transformers import MusicgenForConditionalGeneration, AutoProcessor
import torchaudio
import torch
import os

print(torch.cuda.is_available())

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"🚀 Using device: {device}")

# Load model and processor ONCE
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained(
    "facebook/musicgen-small",
    torch_dtype=torch.float16,    # Use float16 for faster generation
).to(device)

def color_mood_descriptor(color):
    mapping = {
        "red": ("intense", "fast tempo and powerful beats"),
        "orange": ("vibrant", "energetic rhythm and lively bass"),
        "yellow": ("bright", "upbeat tempo and catchy melodies"),
        "green": ("fresh", "dynamic rhythms with organic vibes"),
        "blue": ("cool", "pulsating beats with smooth synths"),
        "purple": ("bold", "rhythmic bass and atmospheric energy"),
        "black": ("edgy", "heavy beats and dark basslines"),
        "white": ("crisp", "sharp beats with clean melodies"),
        "gray": ("gritty", "raw beats and moody bass"),
    }
    return mapping.get(color.lower(), ("balanced", "moderate-fast tempo"))

def build_dynamic_music_prompt(scene, colors, objects):
    primary_color = colors[0] if colors else "neutral"
    mood_adj, tempo_desc = color_mood_descriptor(primary_color)

    object_descriptions = {
        "waves": "energetic synth waves",
        "birds": "rapid melodic trills",
        "trees": "percussive rhythmic elements",
        "clouds": "bright soaring synths",
        "cars": "mechanical beats and bass",
        "people": "vocal chops and crowd energy",
    }

    musical_elements = [object_descriptions.get(obj.lower(), f"dynamic patterns inspired by {obj}") for obj in objects]
    element_line = ", ".join(musical_elements)

    prompt = (
        f"Create an {mood_adj}, {tempo_desc} electronic music track inspired by a {scene.lower()}, "
        f"highlighting {primary_color} energy with {element_line}. "
        f"The track should feature low basslines, dynamic beats, and a driving rhythm perfect for a medium-energy atmosphere."
    )
    return prompt


def generate_music_from_image(image_path, output_path="static/music/music_from_image.wav", max_new_tokens=768):
    # Step 1: Extract image features
    scene = predict_image_category(image_path)
    colors = extract_dominant_colors(image_path)
    objects = detect_objects(image_path)

    # Step 2: Build prompt
    prompt = build_dynamic_music_prompt(scene, colors, objects)
    print("🎵 Music Prompt:", prompt)

    # Step 3: Generate music
    inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(device)
    with torch.no_grad():
        audio_values = model.generate(**inputs, max_new_tokens=max_new_tokens)

    # Step 4: Move audio back to CPU and save
    audio_tensor = audio_values.cpu()

# Fix shape: (batch, channels, time) -> (channels, time)
    if audio_tensor.dim() == 3:
        audio_tensor = audio_tensor.squeeze(0)
    if audio_tensor.dim() == 1:
        audio_tensor = audio_tensor.unsqueeze(0)

# 🔥 Important: Convert to float32
    audio_tensor = audio_tensor.to(torch.float32)

# Save WAV
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    torchaudio.save(output_path, audio_tensor, 16000)
    print(f"✅ Music saved to: {output_path}")

    return output_path
