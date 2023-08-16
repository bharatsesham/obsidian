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
import openai
import langchain
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
        logging.info(
            '+++++++++++++++++++ Service Request Start +++++++++++++++++++')

        start_time = time.time()

        data = request.json
        if not data or 'input' not in data:
            raise ValueError('Invalid request: missing input text')

        if 'generate an image' in data['input'] or 'generate image' in data['input']:
            type = data.get('type', 'image')
        else:
            # default to 'text' if 'type' is not provided
            type = data.get('type', 'text')

        if type not in ['text', 'audio', 'image']:
            raise ValueError(
                'Invalid request: type must be "text", "audio", or "image"')

        if type == 'text':
            return generate_text(data)
        # elif type == 'audio':
        #     return generate_audio(data['input'])
        elif type == 'image':
            return generate_image(data)
        else:
            raise ValueError(f'Unsupported type: {type}')

    except Exception as e:
        logging.error(traceback.format_exc())
        return make_response({'error': str(e)}, 400)

    finally:
        end_time = time.time()
        elapsed_time = end_time - start_time
        app.logger.info(
            f'Total time taken to generate text: {elapsed_time:.5f} seconds')

        app.logger.info(
            f'+++++++++++++++++++ Service Request End +++++++++++++++++++')


def generate_text(data):
    try:
        logging.info(f'Generating Text. Input text: {data["input"]}')
        if USE_OPENAI_API:
            logging.info("Using OpenAI Codex model")
            # Set up OpenAI API credentials
            openai.api_key = os.getenv("OPENAI_API_KEY")

            # Construct messages for the conversation
            messages = []
            for conversation in data['input']['past_conversation']:
                content = conversation['content']
                role = conversation['role']
                messages.append({"role": role, "content": content})

            current_conversation_content = data['input']['current_conversation']['content']
            current_conversation_role = data['input']['current_conversation']['role']
            messages.append({"role": current_conversation_role,
                            "content": current_conversation_content})

            # Generate response from chat model
            response = openai.ChatCompletion.create(
                model=OPENAI_MODEL,  # Use the appropriate model name
                messages=messages,
                max_tokens=600,
                api_key=openai.api_key
            )

            # Extract response from completed sequence
            text = response.choices[0].message['content'].strip()
        else:
            logging.info("Using custom model")
            input_ids = tokenizer.encode(data['input'], return_tensors='pt')
            output = model.generate(input_ids, max_length=100)
            text = tokenizer.decode(output[0], skip_special_tokens=True)

        logging.debug(f'Generated text: {text}')
        response = make_response({'generated_text': text, 'type': 'text'}, 200)

        logging.debug(f'Response: {response}')
        return response

    except Exception as e:
        # log the error traceback
        logging.error(traceback.format_exc())
        # return a helpful error message to the client
        return make_response({'error': str(e)}, 400)


# @app.route('/generate_speech', methods=['POST'])
# def generate_speecht5():
#     data = request.json
#     input_text = data['input']
#     input_processor = processor_speecht5(input_text, return_tensors="pt", padding=True, truncation=True)
#     output = model_speecht5(**input_processor)
#     return {'generated_speech': output} # You might need to adjust this depending on how you want to use the output


def generate_image(data):
    try:
        logging.info(f'Generating Image. Input text: {data["input"]}')
        data = request.json
        openai.api_key = os.getenv("OPENAI_API_KEY")
        openai_response = openai.Image.create(
            prompt=data["input"],
            n=1,
            size="256x256"
        )
        image_url = openai_response['data'][0]['url']
        response = make_response(
            {'generated_image_url': image_url, 'type': 'image'}, 200)

        # Add logging for successful response
        logging.info(f"Generated image URL: {image_url}")
        logging.debug(f'Response: {response.get_data()}')

        return response

    except Exception as e:
        # Add logging for errors
        logging.error(f"Error generating image: {str(e)}")

        return {"error": str(e)}, 500


if __name__ == '__main__':
    logging.info('Starting app on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
