import time
import logging
# from diffusers import DiffusionPipeline
from constants import USE_OPENAI_API, OPENAI_URL, OPENAI_MODEL
import traceback
from dotenv import load_dotenv
import requests
import os
from flask_cors import CORS
# AutoProcessor, SpeechT5ForTextToSpeech
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask import Flask, request, render_template, make_response

# Setup logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


# Load the .env file
load_dotenv()

# Load the tokenizer and model
logging.info('Loading tokenizer')
# tokenizer = AutoTokenizer.from_pretrained("gpt2")
tokenizer = AutoTokenizer.from_pretrained(
    "minhtoan/gpt3-small-finetune-cnndaily-news")
logging.info('Loading model')
# model = AutoModelForCausalLM.from_pretrained("gpt2")
model = AutoModelForCausalLM.from_pretrained(
    "minhtoan/gpt3-small-finetune-cnndaily-news")


# # Load the SpeechT5ForTextToSpeech processor and model
# processor_speecht5 = AutoProcessor.from_pretrained("microsoft/speecht5_tts")
# model_speecht5 = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")

# Load the DiffusionPipeline
# pipeline = DiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5")
# pipeline.to("cuda")

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
    try:
        logging.info('+++++++++++++++++++ Generating text +++++++++++++++++++')
        start_time = time.time()
        data = request.json
        if not data or 'input' not in data:
            raise ValueError('Invalid request: missing input text')
        logging.info(f'Input text: {data["input"]}')

        if USE_OPENAI_API:
            logging.info("Using OpenAI Codex model")
            response = requests.post(OPENAI_URL,
                                     headers={'Content-Type': 'application/json',
                                              'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY").strip(chr(92))}'},
                                     json={"model": OPENAI_MODEL,
                                           "messages": [
                                               {
                                                   "role": "system",
                                                   "content": "You are a helpful assistant."
                                               },
                                               {
                                                   "role": "user",
                                                   "content": data['input']
                                               }
                                           ]})
            logging.info(response.content)
            response.raise_for_status()
            text = response.json()['choices'][0]['message']["content"]
        else:
            logging.info("Using custom model")
            input_ids = tokenizer.encode(data['input'], return_tensors='pt')
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

    except Exception as e:
        # log the error traceback
        logging.error(traceback.format_exc())
        # return a helpful error message to the client
        return make_response({'error': str(e)}, 400)

    finally:
        app.logger.info(
            f'+++++++++++++++++++ Service Request End +++++++++++++++++++')


# @app.route('/generate_speech', methods=['POST'])
# def generate_speecht5():
#     data = request.json
#     input_text = data['input']
#     input_processor = processor_speecht5(input_text, return_tensors="pt", padding=True, truncation=True)
#     output = model_speecht5(**input_processor)
#     return {'generated_speech': output} # You might need to adjust this depending on how you want to use the output


# @app.route('/generate_image', methods=['POST'])
# def generate_image():
#     try:
#         data = request.json
#         image = pipeline(data['input']).images[0]
#         image_path = "/images/generated_image.png"
#         image.save(image_path)
#         return send_file(image_path, mimetype='image/png')
#     except Exception as e:
#         return {"error": str(e)}, 500

if __name__ == '__main__':
    logging.info('Starting app on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
