from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

model_path = r"C:\VSCODE\projects\competition2026\competition202604\backend\model\finetuned"

_model = None
_tokenizer = None

def get_model():
    global _model, _tokenizer
    if _model is None:
        _tokenizer = AutoTokenizer.from_pretrained(
            model_path,
            local_files_only=True
        )
        _model = AutoModelForCausalLM.from_pretrained(
            model_path,
            local_files_only=True,
            torch_dtype=torch.float16,
            device_map="auto"
        )
    return _model, _tokenizer