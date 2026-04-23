from PIL import Image
from transformers import CLIPProcessor, CLIPModel
import torch

# Load once (global)
# Using openai/clip-vit-base-patch32 — outputs 512-dim vectors via visual_projection
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def embed_images(image_paths):
    embeddings = []

    for path in image_paths:
        image = Image.open(path).convert("RGB")

        inputs = processor(images=image, return_tensors="pt")

        with torch.no_grad():
            # Step 1: Run the vision encoder to get pooled CLS token (1, 768)
            vision_outputs = model.vision_model(pixel_values=inputs["pixel_values"])
            pooled_output = vision_outputs.pooler_output  # shape: (1, 768)

            # Step 2: Apply the visual projection layer to get (1, 512)
            image_embeds = model.visual_projection(pooled_output)  # shape: (1, 512)

        # image_embeds[0] is shape (512,) → flat list of 512 floats
        vector = image_embeds[0].cpu().numpy().tolist()
        embeddings.append(vector)

    return embeddings