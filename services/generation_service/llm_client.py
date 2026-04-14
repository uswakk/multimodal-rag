from transformers import AutoProcessor, AutoModelForImageTextToText
import torch

MODEL_NAME = "Qwen/Qwen2.5-VL-3B-Instruct"

processor = AutoProcessor.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models"
)

model = AutoModelForImageTextToText.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models",
    torch_dtype=torch.float32
).to("cpu")