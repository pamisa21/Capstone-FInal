import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

# Load the trained model and tokenizer
model_path = "./twitter_xlm_roberta_fine_tuned_sentiment" 
model = AutoModelForSequenceClassification.from_pretrained(model_path)
model.eval() 
tokenizer = AutoTokenizer.from_pretrained(model_path)

# Function to predict sentiment
def predict_sentiment(text):
    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)

    # Make predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Get predicted class
    predicted_class = logits.argmax().item()

    # Sentiment mapping: Adjust this based on your model's output classes
    sentiment_map = {0: 'Negative', 1: 'Neutral', 2: 'Positive'}
    sentiment = sentiment_map.get(predicted_class, "Unknown")

    return sentiment

# Main script
if __name__ == '__main__':
    while True:
        comment = input("Enter a comment (or 'exit' to quit): ")
        if comment.lower() == 'exit':
            break
        sentiment = predict_sentiment(comment)
        print(f"Predicted Sentiment: {sentiment}")
        
