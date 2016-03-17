'''
This application will act as a Cyberpunk Dictionary.  You can find the sourcecode on GitHub
at https://github.com/SevenEcks/alexa-cyberpunk-dictionary
'''

from __future__ import print_function
import random
import json
import os

# --------------- Static Variables ------------------
APPLICATION_ID = 'amzn1.echo-sdk-ams.app.1a291230-7f25-48ed-b8b7-747205d072db'
APPLICATION_NAME = 'The Cyberpunk Dictionary'
APPLICATION_INVOCATION_NAME = 'the cyberpunk dictionary'
APPLICATION_VERSION = '0.1'
APPLICATION_ENDPOINT = 'arn:aws:lambda:us-east-1:099464953977:function:basic_speech_test'
DICTIONARY_DIRECTORY = 'dictionary/'
DICTIONARY_FORMAT = '.json'
SPEECH_DIRECTORY = 'speech/'
SPEECH_FORMAT = '.json'

# --------------- Helper Functions ------------------
def load_json_from_file(file_name):
    '''load a json file into a data structure we can reference'''
    with open(file_name) as data_file:
        data = json.load(data_file)
    return data

def random_file(directory):
    '''get a random filename from the directory provided'''
    return random.choice(os.listdir(directory))

def build_definition_speech_response(word_data):
    return "{0}: {1} Usage: {2}".format(word_data['name'], word_data['definition'], random.choice(list(word_data['usage'])))

# --------------- Functions that control the skill's behavior ------------------
def get_help(intent, session):
    ''' tell the user a list of valid commands '''
    #load the json data for this intent
    response_data = load_json_from_file(SPEECH_DIRECTORY + get_help.__name__ + SPEECH_FORMAT)
    session_attributes = {}
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def pick_cyberpunk_word(intent, session):
    '''pick a random cyberpunk word and tell the user about it'''
    #no need to add the file format since random_file returns a full file name
    word_data = load_json_from_file(DICTIONARY_DIRECTORY + random_file(DICTIONARY_DIRECTORY))
    #load response data
    response_data = load_json_from_file(SPEECH_DIRECTORY + pick_cyberpunk_word.__name__ + SPEECH_FORMAT)
    session_attributes = {}
    should_end_session = False
    
    return build_response(session_attributes, build_speechlet_response(
        response_data['card_title'], build_definition_speech_response(word_data), response_data['reprompt'], 
        should_end_session))

def welcome_response():
    ''' If we wanted to initialize the session to have some attributes we could
    add those here
    '''
    response_data = load_json_from_file(SPEECH_DIRECTORY + welcome_response.__name__ + SPEECH_FORMAT)
    session_attributes = {}
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def define_cyberpunk_word(intent, session):
    ''' Sets the color in the session and prepares the speech to reply to the user. '''
    response_data = load_json_from_file(SPEECH_DIRECTORY + define_cyberpunk_word.__name__ + SPEECH_FORMAT)
    print(response_data)
    session_attributes = {}
    should_end_session = False
    cyberpunk_word = intent['slots']['CyberpunkWord']['value'].lower()

    print(DICTIONARY_DIRECTORY + cyberpunk_word)
    if os.path.isfile(DICTIONARY_DIRECTORY + cyberpunk_word + DICTIONARY_FORMAT):
        word_data = load_json_from_file(DICTIONARY_DIRECTORY + cyberpunk_word + DICTIONARY_FORMAT)
        speech_output = build_definition_speech_response(word_data)
        reprompt = response_data['reprompt']
    else:
        speech_output = response_data['failure_response']
        reprompt = response_data['failure_reprompt']
        
    print(intent['slots']['CyberpunkWord']['value'].lower())
    return build_response(session_attributes, build_speechlet_response(
        response_data['card_title'], speech_output, reprompt, should_end_session))

def invalid_intent_response(intent, session):
    '''
    we reached an invalid intention due to the user asking for something
    that we are not sure how to process.
    '''
    print(intent)
    response_data = load_json_from_file(SPEECH_DIRECTORY + invalid_intent_response.__name__ + SPEECH_FORMAT)
    session_attributes = {}
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

# --------------- Skill Dipatcher Functions ------------------
def lambda_handler(event, context):
    ''' Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    '''
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    #Prevent someone else from configuring a skill that sends requests to this function.
    if (event['session']['application']['applicationId'] != 
        APPLICATION_ID):
        #TODO make this return a response via alexa?
        raise ValueError("Invalid Application ID")

    #if event['session']['new']:
        #on_session_started({'requestId': event['request']['requestId']},
        #event['session'])
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    ''' Called when the session starts '''

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    ''' Called when the user launches the skill without specifying an intent '''
    return welcome_response()

def on_intent(intent_request, session):
    ''' Called when the user specifies an intent for this skill '''
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print(intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "DefineCyberpunkWord":
        return define_cyberpunk_word(intent, session)
    elif intent_name == "PickCyberpunkWord":
        return pick_cyberpunk_word(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(intent, session)
    else:
        return invalid_intent_response(intent, session)

def on_session_ended(session_ended_request, session):
    ''' Called when the user ends the session.
        Is not called when the skill returns should_end_session=true
    '''
    pass

# --------------- Helpers that build all of the responses ----------------------
def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': 'SessionSpeechlet - ' + title,
            'content': 'SessionSpeechlet - ' + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }