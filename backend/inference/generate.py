# -*- coding: utf-8 -*-
from .load_model import get_model

def generate_reply(user_text):
    model, tokenizer = get_model()

    messages = [
        {"role": "system", "content": "你是一個溫和、支持性的助理，會提供陪伴、簡單建議與正向回應。請務必使用繁體中文回覆。"},
        {"role": "user", "content": user_text}
    ]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    outputs = model.generate(
        **inputs,
        max_new_tokens=200,
        pad_token_id=tokenizer.eos_token_id
    )

    reply = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
    return reply