from transformers import AutoProcessor, AutoModelForImageTextToText
import torch
import os

MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"
CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "/models")

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    cache_dir=CACHE_DIR
)

model = AutoModelForImageTextToText.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models",
    torch_dtype=torch.float32,
    device_map="auto"
)

def generate_answer(prompt, image_paths=None):

    content = []

    if image_paths:
        for img in image_paths:
            content.append({"type": "image", "image": img})

    content.append({"type": "text", "text": prompt})

    messages = [
        {
            "role": "user",
            "content": content
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        add_generation_prompt=True,
        return_tensors="pt"
    )

    outputs = model.generate(**inputs, max_new_tokens=300)

    return processor.decode(outputs[0], skip_special_tokens=True)