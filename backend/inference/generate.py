from .load_model import model, tokenizer

def generate_reply(user_text):

    prompt = f"""
    你是一個溫和、支持性的助理，會提供陪伴、簡單建議與正向回應。
    
    使用者:{user_text}
    助理:
    """
    
    inputs = tokenizer(user_text, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_length=150
    )

    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return reply