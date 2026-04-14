from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models"
)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models",
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    use_safetensors=True
).to("cpu")

def generate_answer(prompt: str):

    inputs = tokenizer(prompt, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_new_tokens=100
    )

    return tokenizer.decode(outputs[0], skip_special_tokens=True)