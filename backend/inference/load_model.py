from transformers import AutoModelForCausalLM, AutoTokenizer

model_path = "./model/finetuned"

tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)