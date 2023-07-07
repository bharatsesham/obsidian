from flask import Flask, request, render_template, make_response
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask_cors import CORS
import logging
import time

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


# Load the tokenizer and model
logging.info('Loading tokenizer')
# tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained(
    "minhtoan/gpt3-small-finetune-cnndaily-news")
logging.info('Loading model')
# model = AutoModelForCausalLM.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained(
    "minhtoan/gpt3-small-finetune-cnndaily-news")


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This should allow all origins


@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


@app.route('/')
def home():
    logging.info('Rendering index.html')
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    logging.info('Generating text')
    start_time = time.time()
    data = request.json
    input_ids = tokenizer.encode(data['input'], return_tensors='pt')
    logging.info('Input text: ' + str(data['input']))
    output = model.generate(input_ids, max_length=100)
    text = tokenizer.decode(output[0], skip_special_tokens=True)
    logging.debug(f'Generated text: {text}')
    response = make_response({'generated_text': text}, 200)
    end_time = time.time()
    elapsed_time = end_time - start_time
    app.logger.info(
        f'Total time taken to generate text: {elapsed_time:.5f} seconds')

    logging.debug(f'Response: {response}')
    return response


if __name__ == '__main__':
    logging.info('Starting app on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
