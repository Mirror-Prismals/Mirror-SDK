import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

def load_model():
    model = GPT2LMHeadModel.from_pretrained("distilgpt2")
    tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
    return model, tokenizer

def generate_text(model, tokenizer, prompt, max_length=200):
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
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
    
    prompt = "In a world where technology and nature have merged, describe a day in the life of a tree that has become sentient due to advanced biotechnology. Include its thoughts, interactions, and challenges."
    
    print("Testing DistilGPT-2 with the prompt:")
    print(prompt)
    print("\nGenerating 3 responses:\n")
    
    for i in range(3):
        generated_text = generate_text(model, tokenizer, prompt)
        print(f"Response {i+1}:")
        print(generated_text)
        print("\n" + "-"*50 + "\n")

if __name__ == "__main__":
    main()
