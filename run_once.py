from transformers import AutoProcessor, AutoModelForImageTextToText

model = AutoModelForImageTextToText.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    cache_dir="D:/models"
)

processor = AutoProcessor.from_pretrained(
    "Qwen/Qwen2.5-VL-3B-Instruct",
    cache_dir="D:/models"
)