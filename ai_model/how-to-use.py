from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

app = Flask(__name__)

# Load the model and tokenizer
model_name = "cardiffnlp/twitter-xlm-roberta-base"
model = AutoModelForSequenceClassification.from_pretrained(model_name)
model.load_state_dict(torch.load("twitter_xlm_roberta_fine_tuned.pth"))
model.eval()  # Set the model to evaluation mode
tokenizer = AutoTokenizer.from_pretrained("./twitter_xlm_roberta_fine_tuned")

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json  # Get the JSON data sent by the user
    text = data.get('text', '')  # Extract the text from the JSON data

    # Tokenize the input text
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)

    # Make predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits

    # Get predicted class (assuming binary classification for simplicity)
    predicted_class = logits.argmax().item()

    return jsonify({'predicted_class': predicted_class})  # Return the result as JSON

if __name__ == '__main__':
    app.run(debug=True)
