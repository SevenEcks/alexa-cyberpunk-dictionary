'''
This application will act as a Cyberpunk Dictionary.  You can find the sourcecode on GitHub
at https://github.com/SevenEcks/alexa-cyberpunk-dictionary
'''

from __future__ import print_function
import random
import json
import os
import config
'''
{u'session': {u'new': False, u'sessionId': u'session1234', u'application': {u'applicationId': u'amzn1.echo-sdk-ams.app.1a291230-7f25-48ed-b8b7-747205d072db'}, u'user': {u'userId': None}, u'attributes': {}}, u'request': {u'type': u'IntentRequest', u'intent': {u'slots': {u'CyberpunkWord': {u'Name': u'CyberpunkWord', u'value': u'aces'}}, u'name': u'DefineCyberpunkWord'}, u'requestId': u'request5678'}, u'version': u'1.0'}
'''

# --------------- Helper Functions ------------------
def debug(data):
    '''if debugging is enabled this will push debugs to the logs'''
    if config.DEBUG:
        print(data)

def load_session(event):
    config.session = event['session']
    
def save_intent_name(intent_name):
    '''save the intent_name to pass into session attributes'''
    config.session['attributes']['last_intent_name'] = intent_name
    #should update a session var

def save_intent_word(intent_word):
    '''save the last passed intent word for repeating'''
    config.session['attributes']['last_intent_word'] = intent_word
    
def get_saved_intent_name():
    '''get the saved last_intent_name for use in session attributes'''
    return config.session['attributes']['last_intent_name'] if 'last_intent_name' in config.session['attributes'] else None

def get_saved_intent_word():
    '''get the saved last_intent_word for use in session attributes'''
    return config.session['attributes']['last_intent_word']

def get_session_attributes():
    '''return a json dump of the session_attributes for passing back with the response'''
    return json.loads(json.dumps(config.session['attributes']))

def load_json_from_file(file_name):
    '''load a json file into a data structure we can reference'''
    with open(file_name) as data_file:
        data = json.load(data_file)
    return data

def load_word(file_name):
    '''load a word based on the file name, and recursively load any redirects'''
    debug(file_name)
    word_data = load_json_from_file(file_name)
    if "redirect" in word_data:
        #we have a redirect
        name = word_data['name']
        word_data = load_word(config.DICTIONARY_DIRECTORY + word_data['redirect'] + config.DICTIONARY_FORMAT)
        word_data['definition'] = 'Redirected from ' + name + '.  ' + word_data['definition']
    return word_data

def random_file(directory):
    '''get a random filename from the directory provided'''
    return random.choice(os.listdir(directory))

def build_definition_speech_response(word_data):
    return "{0}: {1} Usage: {2}".format(word_data['name'], word_data['definition'], random.choice(list(word_data['usage'])))

# --------------- Functions that control the skill's behavior ------------------
def get_help(intent, session):
    '''tell the user a list of valid commands'''
    #load the json data for this intent
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + get_help.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def get_sindome(intent, session):
    '''tell the user about sindome'''
    #load the json data for this intent
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + get_sindome.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def pick_cyberpunk_word(intent, session):
    '''pick a random cyberpunk word and tell the user about it'''
    #no need to add the file format since random_file returns a full file name
    word_data = load_word(config.DICTIONARY_DIRECTORY + random_file(config.DICTIONARY_DIRECTORY))
    #load response data
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + pick_cyberpunk_word.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name('DefineCyberpunkWord')
    save_intent_word(word_data['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], build_definition_speech_response(word_data) + " " + response_data['response'], response_data['reprompt'], 
        should_end_session))

def welcome_response():
    '''If we wanted to initialize the session to have some attributes we could add those here'''
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + welcome_response.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    #save_intent_name(intent)
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def handle_stop(intent, session):
    '''User has requested a stop, so we exit'''
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + handle_stop.__name__ + config.SPEECH_FORMAT)
    should_end_session = True
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def define_cyberpunk_word(intent, session):
    '''Sets the color in the session and prepares the speech to reply to the user'''
    debug(config.SPEECH_DIRECTORY + define_cyberpunk_word.__name__ + config.SPEECH_FORMAT)
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + define_cyberpunk_word.__name__ + config.SPEECH_FORMAT)
    debug(response_data)
    should_end_session = False
    cyberpunk_word = intent['slots']['CyberpunkWord']['value'].lower() \
                                                              .replace(' ', '_') \
                                                              .replace('-','')

    debug(config.DICTIONARY_DIRECTORY + cyberpunk_word)
    if os.path.isfile(config.DICTIONARY_DIRECTORY + cyberpunk_word + config.DICTIONARY_FORMAT):
        debug(intent['slots']['CyberpunkWord']['value'].lower())
        word_data = load_word(config.DICTIONARY_DIRECTORY + cyberpunk_word + config.DICTIONARY_FORMAT)
        speech_output = build_definition_speech_response(word_data)
        reprompt = response_data['reprompt']
    else:
        speech_output = response_data['failure_response']
        reprompt = response_data['failure_reprompt']

    save_intent_name(intent['name'])
    save_intent_word(cyberpunk_word)
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], speech_output + " " + response_data['response'], reprompt, should_end_session))

def invalid_intent_response(intent, session):
    '''Invalid intention due to the user asking for something we are not sure how to process'''
    debug(intent)
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + invalid_intent_response.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent['name'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))

def repeat_intent(intent_request, session):
    #confirm we are not going to recall with the same repeatintent over and over
    last_intent_name = get_saved_intent_name()
    debug('LAST INTENT NAME' + last_intent_name)
    debug('UNEDITED INTENT REQUEST')
    debug(intent_request)
    if last_intent_name and last_intent_name != "AMAZON.RepeatIntent":
        #overwrite the intent where needed
        intent_request['intent']['name'] = last_intent_name
        if last_intent_name == 'DefineCyberpunkWord':
            intent_request['intent']['slots'] = {'CyberpunkWord' : {'value' : get_saved_intent_word() }}
        
        debug("EDITED INTENT REQUEST")
        debug(intent_request)
        #return False
        return on_intent(intent_request, session)
    debug("SKIPPED INTENT EDIT, RETURNING BAD REPEAT")
    response_data = load_json_from_file(config.SPEECH_DIRECTORY + repeat_intent.__name__ + config.SPEECH_FORMAT)
    should_end_session = False
    save_intent_name(intent_request['intent'])
    return build_response(get_session_attributes(), build_speechlet_response(
        response_data['card_title'], response_data['response'], response_data['reprompt'], should_end_session))
# --------------- Skill Dipatcher Functions ------------------

def on_intent(intent_request, session):
    '''Called when the user specifies an intent for this skill'''
    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    debug(intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "DefineCyberpunkWord":
        return define_cyberpunk_word(intent, session)
    elif intent_name == "PickCyberpunkWord":
        return pick_cyberpunk_word(intent, session)
    elif intent_name == "Sindome":
        return get_sindome(intent, session)
    #handle help, repeating, exiting and stopping properly
    elif intent_name == "AMAZON.RepeatIntent":
        #call with full intent request so we can make the full on_intent call again
        return repeat_intent(intent_request, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(intent, session)
    elif intent_name == "AMAZON.StopIntent" or intent_name == 'AMAZON.CancelIntent':
        return handle_stop(intent, session)
    else:
        return invalid_intent_response(intent, session)

def lambda_handler(event, context):
    '''Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    '''
    debug(event)

    #debug("event.session.application.applicationId=" +
    #event['session']['application']['applicationId'])

    #Prevent someone else from configuring a skill that sends requests to this function.
    if (event['session']['application']['applicationId'] != 
        config.APPLICATION_ID):
        #TODO make this return a response via alexa?
        raise ValueError("Invalid Application ID")
    #save the session data
    load_session(event)
    debug('SESSION')
    debug(config.session)
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']}, event['session'])
    
    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])

def on_session_started(session_started_request, session):
    '''Called when the session starts'''
    #attributes does not already exist on a new session
    config.session['attributes'] = {'last_intent_name' : 'None'}

    #debug("on_session_started requestId=" + session_started_request['requestId']
          #+ ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    '''Called when the user launches the skill without specifying an intent '''
    #save_intent_name()
    #need to json encode the session data we want to send, or have it be an array that is jsonified later.
    return welcome_response()

def on_session_ended(session_ended_request, session):
    '''Called when the user ends the session.
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
    response = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }
    debug('RESPONSE')
    debug(response)
    return response