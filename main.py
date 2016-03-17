"""
This application will act as a Cyberpunk Dictionary.  You can find the sourcecode on GitHub
at XYZURLHERE


"""

from __future__ import print_function
import random

#static for our alexa application id
APPLICATION_ID = 'amzn1.echo-sdk-ams.app.1a291230-7f25-48ed-b8b7-747205d072db'

APPLICATION_NAME = 'The Cyberpunk Dictionary'

APPLICATION_INVOCATION_NAME = 'the cyberpunk dictionary'

APPLICATION_VERSION = '0.1'

APPLICATION_ENDPOINT = 'arn:aws:lambda:us-east-1:099464953977:function:basic_speech_test'

dict = {"baka" : "Baka: slang for fool, or idiot.  Usage: Don't be a baka.",
        "splat job" : "Splat Job: Used to refer to someone who died " \
        "falling from a great height.  An alternate usage would be to " \
        "describe someone who is expected to die soon.  Usage: That " \
        "splat job ain't long for this world chummer, I's telling ya.",
        "diamond season" : "Diamond season: Warm weather, or " \
        "good times.  Usage: You been outside today?  Diamond season mano.",
        "chinese take-out" : "Chinese Takeout: What someone's insides look " \
        "like after being attacked violently.  Usage: I had that chummer " \
        "looking like chinese takeout when I was done with 'em."}

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Prevent someone else from configuring a skill that sends requests to this
    function.
    """
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
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print('on intent')
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']
    print(intent_name)

    # Dispatch to your skill's intent handlers
    if intent_name == "DefineCyberpunkWord":
        return define_cyberpunk_word(intent, session)
    elif intent_name == "PickCyberpunkWord":
        return pick_cyberpunk_word(intent, session)
    #elif intent_name == "TranslateEnglishWord":
        #return translate_english_word(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_help(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here

# --------------- Functions that control the skill's behavior ------------------

def get_help(intent, session):
    """ tell the user a list of valid commands """
    session_attributes = {}
    card_title = 'Help'
    speech_output = "You can ask me to define a specific word by asking, " \
                    "What does baka mean?" \
                    "Or tell me to give you a Cyberpunk word, " \
    
    reprompt_text = "Ask me for help if you want to hear the list of " \
                    "commands again."
    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def pick_cyberpunk_word(intent, session):
    """ tell the user a list of valid commands """
    session_attributes = {}
    card_title = 'Pick Cyberpunk Word'
    speech_output = random.choice(list(dict.values()))
    
    reprompt_text = "Ask me for help if you want to hear the list of " \
                    "commands again."
    
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
        
def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Cyberpunk Dictionary. " \
                    "Ask me for help to hear a list of commands."
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask me to define a specific word with, " \
                    "What does chinese takeout mean, " \
                    "Or ask me for help for more commands"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def define_cyberpunk_word(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False
    speech_output = None
    reprompt_text = None
    cyberpunk_word = 'undefined'

    if 'CyberpunkWord' in intent['slots']:
        cyberpunk_word = intent['slots']['CyberpunkWord']['value'].lower()
        #session_attributes = create_favorite_color_attributes(favorite_color)
        if cyberpunk_word in dict:
            speech_output = dict[cyberpunk_word.lower()]
            reprompt_text = 'Would you like me to define another word for you'
    
    
    if not speech_output:
        speech_output = "I'm unable to define the word you're looking for, " \
                        "Please try again." \
        
        print(intent['slots']['CyberpunkWord']['value'].lower())
        reprompt_text = "I'm unable to define the word you're looking for, " \
                        "You can ask me to define a word by saying, " \
                        "What does baka mean"
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def invalid_intent_response(intent, session):
    session_attributes = {}
    reprompt_text = None

    speech_output = "I was unable to figrue out what you wanted.  You can ask" \
                    "for help and I can give you a list of possible queries."
                    
    should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))
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