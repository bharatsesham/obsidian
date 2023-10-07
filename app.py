import time
import logging
# from diffusers import DiffusionPipeline
from constants import USE_OPENAI_API, OPENAI_URL, OPENAI_MODEL
from botocore.exceptions import BotoCoreError, ClientError
import traceback
from dotenv import load_dotenv
import requests
import os
from flask_cors import CORS
# AutoProcessor, SpeechT5ForTextToSpeech
from transformers import AutoTokenizer, AutoModelForCausalLM
from flask import Flask, request, render_template, make_response, jsonify
import openai
import langchain
import boto3
import threading
import base64

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
        logging.info('+++++++++++++++++++ Service Request Start +++++++++++++++++++'
                     )
        start_time = time.time()

        data = request.json
        if not data or 'input' not in data:
            raise ValueError('Invalid request: missing input text')

        types_to_generate = determine_generation_types(data['input'])
        processed_input = process_request_data(data, types_to_generate)
        combined_response = combinator(data, processed_input)

        return combined_response

    except Exception as e:
        logging.error(traceback.format_exc())
        return make_response({'error': str(e)}, 400)

    finally:
        elapsed_time = time.time() - start_time
        logging.info(f'Time taken: {elapsed_time:.5f} seconds')
        logging.info(
            '+++++++++++++++++++ Service Request End +++++++++++++++++++')


def process_request_data(request_data, types_to_generate):
    """
    Process the input request data and organize it into structured data for other generate functions.

    Args:
    - request_data (dict): Raw data from the request.

    Returns:
    - dict: Processed input data.
    """
    prompt_generator = request_data['input']
    processed_input = {}

    # Extract and process audio input for the generate_audio function

    # if 'audio' in types_to_generate:
    #     processed_input["audio"] = {
    #         "prompt": "Generate audio for" + prompt_generator[audio],
    #         # ... add other required fields for the audio generation
    #     }

    # Extract and process image input for the generate_image function
    if 'image' in types_to_generate:
        processed_input["image"] = {
            "prompt": "Generate an image of" + prompt_generator,
        }

    if 'text' in types_to_generate:
        processed_input["text"] = request_data

    # ... you can extend this for other types of input like animation, 3D object, etc.

    return processed_input


def process_text_response(text_response):
    return text_response['generated_text']


# TODO: Replace this with a GPT-3 labeler and other methods to determine which functions to call
def determine_generation_types(input_text):
    """
    Use GPT-3 model (or any other method) to determine which functions to call based on the user's input.
    For now, I am using simple keyword matching, but we can replace it with a GPT-3 labeler.
    """
    types_to_generate = ['text', 'speech']

    if 'generate an image' in input_text or 'generate image' in input_text:
        types_to_generate.append('image')

    # if 'generate a speech' in input_text or 'generate speech' in input_text:
    #     types_to_generate.append('speech')

    # ... [similar checks for other types] ...

    return types_to_generate


def combinator(data, processed_input):
    try:
        """
        Combines the outputs from the required generator functions.

        Processed Input -> Generate text -> Generate Speech -> Generate Animation
                                         -> Generate Image  -> Generate 3D Object (To Display Image)
                                         -> Generate Code   -> Generate 3D Object (To Display Code)
                                         -> Generate Video  -> Generate 3D Object (To Display Video)
                                         -> Generate Audio  -> Generate 3D Object (To Play Audio)
        """
        response_data = {}
        threads = []

        if 'text' in processed_input:
            text_response = generate_text(processed_input['text'])
            response_data['text'] = text_response.get_json()

        if 'image' in processed_input:
            # Create threads to run generate_audio and generate_image functions asynchronously
            image_thread = threading.Thread(
                target=generate_image, args=(processed_input['image']))
            image_thread.start()
            threads.append(image_thread)

        if 'speech' in processed_input and text_response is not None:
            speech_thread = threading.Thread(
                target=generate_speech, args=(process_text_response(text_response),))
            speech_thread.start()
            threads.append(speech_thread)

        # Wait for all started threads to complete
        for thread in threads:
            thread.join()

        # Retrieve the results from the threads
        response_data['speech'] = speech_thread.result if "speech" in processed_input else None
        response_data['image'] = speech_thread.result if "image" in processed_input else None

        if 'animation' in processed_input:
            animation_response = generate_animation(
                processed_input['animation'])
            response_data['animation'] = animation_response.get_json()

        if 'environment' in processed_input:
            objects_response = generate_3dobjects(
                processed_input['environment'])
            response_data['3dobjects'] = objects_response.get_json()

        if 'code' in processed_input:
            code_response = generate_code(processed_input['code'])
            response_data['code'] = code_response.get_json()

        if 'video' in processed_input:
            video_response = generate_video(processed_input['video'])
            response_data['video'] = video_response.get_json()

        if 'audio' in processed_input:
            audio_response = generate_audio(processed_input['audio'])
            response_data['audio'] = audio_response.get_json()

        return response_data

    except Exception as e:
        logging.error(traceback.format_exc())
        return make_response({'error': str(e)}, 400)


@app.route('/generate_text', methods=['POST'])
def generate_text(data):
    try:
        logging.info(f'Generating Text. Input text: {data["input"]}')
        if USE_OPENAI_API:
            logging.info("Using OpenAI Codex model")
            # Set up OpenAI API credentials
            openai.api_key = os.getenv("OPENAI_API_KEY")

            # Construct messages for the conversation
            messages = []
            if data['input'].get('past_conversation'):
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


@app.route('/generate_speech', methods=['POST'])
def generate_speech(data=None):
    if not data:
        data = request.json['input']

    # initialize AWS Polly client
    polly_client = boto3.Session(
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        region_name='us-west-2'
    ).client('polly')

    try:
        # call Polly's synthesize_speech function to generate audio
        response = polly_client.synthesize_speech(
            Text=data,
            VoiceId='Raveena',
            OutputFormat='mp3'
        )
    except (BotoCoreError, ClientError) as error:
        # The service returned an error, exit gracefully
        logging.error(error)
        return make_response({'error': str(error)}, 400)

    if "AudioStream" in response:
        # create a response object
        # Encode the audio data as a base64 string
        audio_data = base64.b64encode(response["AudioStream"].read()).decode()

        # Create a JSON response with the audio data
        return jsonify({'generated_speech': 'data:audio/mp3;base64,' + audio_data})

        # response = make_response(response['AudioStream'].read())
        # # add headers to force browser to download file
        # response.headers["Content-Disposition"] = "attachment; filename=speech.mp3"
        # response.headers["Content-Type"] = "audio/mpeg"
        # return response


@app.route('/generate_image', methods=['POST'])
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


# move to a separate file and import in this file
@app.route('/generate_model_animation')
def generate_animation():
    # Placeholder for your animation generating logic
    return "animation_url_here"


@app.route('/generate_3dobjects')
def generate_3dobjects():
    # Placeholder for your 3D object generating logic
    return "3dobject_url_here"


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    # Placeholder for your audio generating logic - Plugin Meta AudioCraft (Both Song and Sound Effects)
    return "audio_url_here"


@app.route('/generate_code', methods=['POST'])
def generate_code():
    # Placeholder for your code generating logic
    return "code_url_here"


@app.route('/generate_video', methods=['POST'])
def generate_video():
    # Placeholder for your video generating logic
    return "video_url_here"


if __name__ == '__main__':
    logging.info('Starting app on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
