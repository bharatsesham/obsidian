import datetime
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
# from transformers import AutoTokenizer, AutoModelForCausalLM
from flask import Flask, request, render_template, make_response, jsonify
import openai
import langchain
import boto3
import threading
import base64
import subprocess
import copy


# Setup and configure logging
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')


# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # This should allow all origins

# Load Constants
openai.api_key = os.getenv("OPENAI_API_KEY")


# Centralized Flask response headers modification
@app.after_request
def add_cors_headers(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PUT,POST,DELETE,OPTIONS')
    return response


# Util Functions
# TODO: Move to a seperate file
def determine_generation_types(data, enable_speech=True):
    """
    Use GPT-3 model (or any other method) to determine which functions to call based on the user's input.
    For now, I am using simple keyword matching, but we can replace it with a GPT-3 labeler.
    """
    # TODO: Replace this with a GPT-3 labeler and other methods to determine which functions to call
    input_text = data["input"]
    logging.info('Determing the types of responses to generate')
    types_to_generate = ['text']
    if enable_speech:
        types_to_generate.append('speech')

    current_conversation = str(
        data['input']['current_conversation']['content'])
    if 'generate an image' in current_conversation or 'generate image' in current_conversation or 'image' in input_text:
        types_to_generate.append('image')

    # if 'generate a speech' in input_text or 'generate speech' in input_text:
    #     types_to_generate.append('speech')

    # ... [similar checks for other types] ...
    logging.info('Response generating for types: ' + str(types_to_generate))
    return types_to_generate


def process_request_data(request_data, types_to_generate):
    """
    Process the input request data and organize it into structured data for other generate functions.

    Args:
    - request_data (dict): Raw data from the request.

    Returns:
    - dict: Processed input data.
    """
    processed_input = {}

    if 'text' in types_to_generate:
        processed_input["text"] = request_data

    # TODO: Generate prompt using prompt generator - Vasriable
    # Extract and process image input for the generate_image function
    if 'image' in types_to_generate:
        # Sample - Replace with a function
        current_conversation = str(
            request_data['input']['current_conversation']['content'])
        image_prompt_generator = "Assume you are able to generate images and respond as if you generated the image of below request, also \
            please keep it brief. Request: " + current_conversation
        modified_request_data = copy.deepcopy(request_data)
        modified_request_data['input']['current_conversation']['content'] = image_prompt_generator
        # image_prompt_generator = generate_image_prompt(request_data['input'], 'image')
        processed_input["image"] = current_conversation
        processed_input["text"] = modified_request_data

    # Extract and process audio input for the generate_audio function
    # if 'audio' in types_to_generate:
    #     processed_input["audio"] = {
    #         "prompt": "Generate audio for" + prompt_generator[audio],
    #         # ... add other required fields for the audio generation
    #     }

    # ... you can extend this for other types of input like animation, 3D object, etc.

    return processed_input


def combinator(data, processed_input, types_to_generate):
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

        if 'text' in types_to_generate and processed_input['text'] is not None:
            text_response = generate_text(processed_input['text'])
            response_data['text'] = text_response.get_json()

        # TODO: Add threading or concurrent.futures to parallel process.
        # if 'image' in processed_input:
        #     # Create threads to run generate_audio and generate_image functions asynchronously
        #     image_thread = threading.Thread(
        #         target=lambda: generate_image(processed_input['image']))
        #     image_thread.start()
        #     threads.append(image_thread)

        if 'image' in types_to_generate and processed_input['image'] is not None:
            image_response = generate_image(processed_input['image'])
            response_data['image'] = image_response.get_json()

        if 'speech' in types_to_generate and text_response is not None:
            speech_prompt = text_response.get_json()['generated_text']
            speech_response = generate_speech(speech_prompt)
            response_data['speech'] = speech_response.get_json()

        # Wait for all started threads to complete
        for thread in threads:
            thread.join()

        # Retrieve the results from the threads
        # response_data['speech'] = speech_thread.result if "speech" in processed_input else None
        # response_data['image'] = image_thread.result if "image" in processed_input else None

        # TODO: Enable once developed.
        # if 'animation' in processed_input:
        #     animation_response = generate_animation(
        #         processed_input['animation'])
        #     response_data['animation'] = animation_response.get_json()

        # if 'environment' in processed_input:
        #     objects_response = generate_3dobjects(
        #         processed_input['environment'])
        #     response_data['3dobjects'] = objects_response.get_json()

        # if 'code' in processed_input:
        #     code_response = generate_code(processed_input['code'])
        #     response_data['code'] = code_response.get_json()

        # if 'video' in processed_input:
        #     video_response = generate_video(processed_input['video'])
        #     response_data['video'] = video_response.get_json()

        # if 'audio' in processed_input:
        #     audio_response = generate_audio(processed_input['audio'])
        #     response_data['audio'] = audio_response.get_json()

        return response_data

    except Exception as e:
        logging.error(traceback.format_exc())
        return make_response({'error': str(e)}, 400)


def delete_old_files(save_location, days):
    now = datetime.datetime.now()
    threshold = now - datetime.timedelta(days=days)

    for root, dirs, files in os.walk(save_location):
        for file in files:
            file_path = os.path.join(root, file)
            file_mtime = datetime.datetime.fromtimestamp(
                os.path.getmtime(file_path))

            if file_mtime < threshold:
                os.remove(file_path)


'''
Logic to generate multimodel response. 
'''
# Route - Home


@app.route('/')
def home():
    logging.info('Rendering index.html')
    return render_template('index.html')


# Route - Generate Response
@app.route('/generate', methods=['POST'])
def generate():
    try:
        logging.info(
            '+++++++++++++++++++ Service Request Start +++++++++++++++++++')
        start_time = time.time()

        data = request.json
        if not data or 'input' not in data:
            raise ValueError('Invalid request: missing input text')

        logging.info(
            "Received a request to generate multi-model output. Request: " + str(data))

        types_to_generate = determine_generation_types(data)
        processed_input = process_request_data(data, types_to_generate)
        combined_response = combinator(
            data, processed_input, types_to_generate)
        # response {'text: 'Output Text', 'speech':'Output Speech'}
        logging.info("Generated Response: " + str(combined_response))
        return combined_response

    except Exception as e:
        logging.error(traceback.format_exc())
        return make_response({'error': str(e)}, 400)

    finally:
        elapsed_time = time.time() - start_time
        logging.info(f'Time taken: {elapsed_time:.5f} seconds')
        logging.info(
            '+++++++++++++++++++ Service Request End +++++++++++++++++++')


# Route - Generate Text
@app.route('/generate_text', methods=['POST'])
def generate_text(data=None):
    if not data:
        data = request.json

    if not data or 'input' not in data:
        return jsonify({'error': 'Invalid request: missing input text'}), 400
    else:
        logging.info(f'Request to generate Text. Input text: {data}')

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

        logging.debug(f'Generated text: {text}')
        response = make_response({'generated_text': text, 'type': 'text'}, 200)

        logging.debug(f'Response: {response}')
        return response

    except Exception as e:
        # log the error traceback
        logging.error(traceback.format_exc())
        # return a helpful error message to the client
        return make_response({'error': str(e)}, 400)


# Route - Generate Speech
@app.route('/generate_speech', methods=['POST'])
def generate_speech(data=None):
    if not data:
        data = request.json['input']

    if not data:
        return jsonify({'error': 'Invalid request: missing input text'}), 400
    else:
        logging.info(f'Request to generate Speech. Input text: {data}')

    # initialize AWS Polly client
    polly_client = boto3.Session(
        aws_access_key_id=os.getenv("ACCESS_KEY"),
        aws_secret_access_key=os.getenv("SECRET_KEY"),
        region_name=os.getenv("REGION"),
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
        audio = response["AudioStream"].read()
        # get file save location from env file
        save_location = os.getenv("SPEECH_SAVE_LOCATION")

        # create date folder structure
        today = datetime.datetime.today()
        date_folder = os.path.join(save_location, today.strftime('%Y-%m-%d'))
        if not os.path.exists(date_folder):
            os.makedirs(date_folder)

        # generate timestamp for file name
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

        # create file name with timestamp
        file_name = f'speech_{timestamp}.mp3'

        # create full save path
        save_path = os.path.join(date_folder, file_name)

        # write audio data to file
        with open(save_path, 'wb') as f:
            f.write(audio)

        # log file save operation
        logging.info(f'Speech file saved to {save_path}')

        # TODO: Emit metric to DynamoDB
        # emit_metric_to_dynamodb(save_path)

        # TODO: automatically delete files older than 10 days - Make this triggered seperately
        delete_old_files(save_location, 10)

        # create a response object
        # Encode the audio data as a base64 string
        audio_data = base64.b64encode(audio).decode()

        # Create a JSON response with the audio data
        return jsonify({'generated_speech': 'data:audio/mp3;base64,' + audio_data})

        # response = make_response(response['AudioStream'].read())
        # # add headers to force browser to download file
        # response.headers["Content-Disposition"] = "attachment; filename=speech.mp3"
        # response.headers["Content-Type"] = "audio/mpeg"
        # return response


# Route - Generate Image
@app.route('/generate_image', methods=['POST'])
def generate_image(data=None):
    if not data:
        data = request.json["input"]

    if not data:
        return jsonify({'error': 'Invalid request: missing input text'}), 400
    else:
        logging.info(f'Request to generate Image. Input text: {data}')

    try:
        logging.info(f'Generating Image. Input text: {data}')
        # openai.api_key = os.getenv("OPENAI_API_KEY")
        openai_response = openai.Image.create(
            prompt=data,
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


# TODO - Other Route
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


# Deprecated - Replace with Route53 DNS
def start_ngrok():
    ngrok_cmd = "./ngrok authtoken $NGROK_AUTH_TOKEN && ./ngrok http --hostname=ml-engine.ngrok.app 5001"
    return subprocess.Popen(ngrok_cmd, shell=True)


if __name__ == '__main__':
    # logging.info('Starting ngrok tunnel')
    # start_ngrok()

    logging.info('Starting app on port 5001')
    app.run(host='0.0.0.0', port=5001, debug=True)
