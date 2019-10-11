import json
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse

from sunrise.settings.common import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN
from textin.models import Survey, Question

class SurveyLoader():

    def __init__(self, survey_content):
        self.survey = json.loads(survey_content)

    def load_survey(self):
        new_survey = Survey(title=self.survey['title'],
                            end_message=self.survey['end_message'],
                            start_date=self.survey['start_date'],
                            end_date=self.survey['end_date'])

        optional_survey_attrs = [
            'start_message', 'end_message', 'followup', 'complete_responder',
            'pushed', 'hidden'
        ]
        for attr in optional_survey_attrs:
            if hasattr(self.survey, attr):
                setattr(new_survey, attr, self.survey[attr])

        new_survey.save()

        questions = [Question(body=question['body'],
                              kind=question['kind'],
                              survey=new_survey).save()
                     for question in self.survey['questions']]


def compose_response(message):
    twiml_response = MessagingResponse()
    # It's invalid to have an empty TwiML <Message />
    if message is not None:
        twiml_response.message(message)

    return twiml_response


def create_get_param_string(obj):
    get_param_string = ''
    if len(obj) > 0:
        get_param_string = '?'
        for key, val in obj.items():
            get_param_string += f'{key}={str(val)}&'
    return get_param_string


def get_twilio_client():
    return Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
