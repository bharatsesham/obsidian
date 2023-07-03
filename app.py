# app.py

from flask import Flask, request, render_template
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask_cors import CORS

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained("gpt2")
# tokenizer = AutoTokenizer.from_pretrained("gpt2-xl")
# model = AutoModelForCausalLM.from_pretrained("gpt2-xl")

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    input_ids = tokenizer.encode(data['input'], return_tensors='pt')
    output = model.generate(input_ids, max_length=100)
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    return {'generated_text': text}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

