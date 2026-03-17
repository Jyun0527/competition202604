from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "mistralai/Mistral-7B"

model = AutoModelForCausalLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

model.save_pretrained("./model/finetuned")
tokenizer.save_pretrained("./model/finetuned")