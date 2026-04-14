from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"

# Optional: use HF token from environment (best practice)
#using from cli
#HF_TOKEN = os.getenv("HF_TOKEN")

print("Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models",

)

print("Loading model (this may take some time)...")
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    cache_dir="Z:/models",
    torch_dtype=torch.float32,
    low_cpu_mem_usage=True,
    use_safetensors=True,
  
).to("cpu")

print("Model loaded successfully!")


def generate_answer(prompt: str):

    # Tokenize input
    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=True,
        max_length=1024   # prevent huge prompts
    )

    # Generate output
    outputs = model.generate(
        **inputs,
        max_new_tokens=80,
        do_sample=False,        # deterministic (faster + stable)
        eos_token_id=tokenizer.eos_token_id
    )

    # Decode result
    answer = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return answer