import torch
from transformers import GPTNeoForCausalLM, GPT2Tokenizer

def load_model():
    model = GPTNeoForCausalLM.from_pretrained("EleutherAI/gpt-neo-125M")
    tokenizer = GPT2Tokenizer.from_pretrained("EleutherAI/gpt-neo-125M")
    return model, tokenizer

def generate_text(model, tokenizer, prompt, max_length=50):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    # Generate text
    output = model.generate(
        input_ids,
        max_length=max_length,
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        temperature=0.7
    )
    
    return tokenizer.decode(output[0], skip_special_tokens=True)

def main():
    model, tokenizer = load_model()
    
    while True:
        prompt = input("Enter your prompt (or 'quit' to exit): ")
        if prompt.lower() == 'quit':
            break
        
        generated_text = generate_text(model, tokenizer, prompt)
        print("Generated text:")
        print(generated_text)
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
