from .load_model import model, tokenizer

def generate_reply(text):

    inputs = tokenizer(text, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        max_length=100
    )

    reply = tokenizer.decode(outputs[0], skip_special_tokens=True)

    return reply