import requests
import json

HOSTED_IP = ''
AUDIO_ROOT = ""
relative_audio_path='speech_danny_demo.mp3'
EXPORT_DIRECTORY = ''
relative_audio_path=''



def parse_request_content(content):
    # Load the JSON content into a Python object.
    return json.loads(content)

# Get the raw content of the response.
instances_response_content = requests.get(HOSTED_IP + '/A2F/Player/GetInstances').content

# Decode the bytes object to a string.
instances_response_content = instances_response_content.decode()
instances_response = parse_request_content(instances_response_content)

if instances_response['status'] == 'OK':
    instance = instances_response['result']['regular']
    print("PLayer Instances" + str(instance))

    # Get the root folder for the audio files.
    audio_root_path_content = requests.post(HOSTED_IP + '/A2F/Player/GetRootPath', json={"a2f_player": instance[0]}).content
    audio_root_path_response = parse_request_content(audio_root_path_content)
    print("Audio Root Folder found at: "+audio_root_path_response['result'])
    if audio_root_path_response['result'] != AUDIO_ROOT:
        # Set the root folder for the audio files.
        requests.post(HOSTED_IP + '/A2F/Player/SetRootPath', json={"a2f_player": instance[0], "dir_path": AUDIO_ROOT})
        print("Modified the audio player root path to: " + AUDIO_ROOT)
    else:
        print("Audio Root already set correctly.")

    # Set the active audio track.
    requests.post(HOSTED_IP+'/A2F/Player/SetTrack', json={"a2f_player": instance[0],
                                                           "file_name": relative_audio_path,
                                                           "time_range": [0, -1]
                                                          })
    
    current_track_content = requests.post(HOSTED_IP + '/A2F/Player/GetCurrentTrack', json={"a2f_player": instance[0]}).content
    current_track_response = parse_request_content(current_track_content)
    print('Current track loaded in the player: ' + current_track_response['result'])

    # TODO: Find a way to stream the blendershapes once the audio file is loaded. 
    print('Playing the track...')
    # Start playing the audio track.
    requests.post(HOSTED_IP+'/A2F/Player/Play')

    ## Emotion API's ##
    emotion_instances_response_content = requests.get(HOSTED_IP + '/A2F/GetInstances').content
    emotion_instances_response = parse_request_content(emotion_instances_response_content)
    # TODO: Check what other instances can be present.
    emotion_instance = emotion_instances_response['result']['fullface_instances']
    print('Emotion Instance in the scene:'+ str(emotion_instance))

    # Get emotion names
    emotion_names_response_content = requests.get(HOSTED_IP + '/A2F/A2E/GetEmotionNames').content
    emotion_names_response = parse_request_content(emotion_names_response_content)
    print('List of available emotions:' + str(emotion_names_response['result']))

    # Get list of emotions
    emotion_response_content = requests.post(HOSTED_IP + '/A2F/A2E/GetEmotion', json={"a2f_instance": emotion_instance[0],
                                                                                    "as_vector": False,
                                                                                    "frame": 0,
                                                                                    "as_timestamp": False}).content
    emotion_response = parse_request_content(emotion_response_content)
    print('List of emotion values:' + str(emotion_response['result']))




else:
    print(instances_response['message'])

# TODO: Figure out a way to export emotion blendershapes in GLTF format. 
# # Get a list of the existing blendshape solver nodes in the scene.
# blendshape_solver_nodes_content = requests.get(HOSTED_IP + '/A2F/Exporter/GetBlendshapeSolvers').content
# print(blendshape_solver_nodes_content)
# blendshape_solver_nodes = parse_request_content(blendshape_solver_nodes_content)['result']
# print(blendshape_solver_nodes)

# # Choose the blendshape solver node that you want to export the emotion blendershapes from.
# blendshape_solver_node_name = blendshape_solver_nodes[0]

# # Export the emotion blendershapes.
# requests.post(HOSTED_IP + '/A2F/Exporter/ExportBlendshapes', json={"a2f_node": blendshape_solver_node_name,
#                                                                    "export_directory": EXPORT_DIRECTORY,
#                                                                     "file_name": "emotion_blendershapes.gltf",
#                                                                     "format": "gltf",
#                                                                     "batch": False
# })