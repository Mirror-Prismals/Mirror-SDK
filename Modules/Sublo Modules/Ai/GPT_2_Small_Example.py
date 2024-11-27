import torch
from transformers import GPT2LMHeadModel, GPT2Tokenizer

# Check for GPU availability
device = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load the tokenizer and model for GPT-2 Small (117M parameters)
tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)

# Encode input text
input_text = "In a world where technology and nature have merged, describe a day in the life of a tree that has become sentient due to advanced biotechnology. Include its thoughts, interactions, and challenges."
input_ids = tokenizer.encode(input_text, return_tensors='pt').to(device)

# Generate text
output = model.generate(input_ids, max_length=50, num_return_sequences=1)

# Decode and print the output
generated_text = tokenizer.decode(output[0], skip_special_tokens=True)
print(generated_text)
# Check the number of parameters
total_params = sum(p.numel() for p in model.parameters())
print(f"Total parameters: {total_params / 1e6:.1f}M")  # Should be around 117M
