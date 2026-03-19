from transformers import AutoModelForCausalLM, AutoTokenizer
import os, torch

token = os.environ.get("HF_TOKEN")
model_name = "Qwen/Qwen2.5-3B-Instruct" #阿里巴巴出的，專門針對中文優化

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    token=token,
    torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(
    model_name,
    token=token)

model.save_pretrained("./model/finetuned")
tokenizer.save_pretrained("./model/finetuned")