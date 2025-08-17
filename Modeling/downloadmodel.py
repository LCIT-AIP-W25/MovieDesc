from transformers import AutoModel, AutoTokenizer

model_name = "Salesforce/blip-image-captioning-base"  # Example model, change if needed
save_path = "H:/MovieDesc/Modeling/blip_model"

# Load the model and tokenizer
model = AutoModel.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

# Save the model and tokenizer
model.save_pretrained(save_path)
tokenizer.save_pretrained(save_path)

print(f"Model and tokenizer saved to {save_path}")
