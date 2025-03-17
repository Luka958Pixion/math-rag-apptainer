import os
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Ensure the Hugging Face cache directory is set correctly
os.environ["HF_HOME"] = os.path.expanduser("~/.cache/huggingface")
os.environ["TRANSFORMERS_OFFLINE"] = "1"  # Force offline mode

def main():
    model_path = "/app/models/llama3b"  # Adjust to where the model is stored inside the container

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, torch_dtype=torch.float16, local_files_only=True).cuda()

    input_text = "Tell me a joke."
    inputs = tokenizer(input_text, return_tensors="pt").to("cuda")

    outputs = model.generate(inputs.input_ids, max_length=50)
    print("Generated Text:", tokenizer.decode(outputs[0], skip_special_tokens=True))

if __name__ == "__main__":
    main()