import json
from twilio.twiml.messaging_response import MessagingResponse

from textin.models import Survey, Question

class SurveyLoader():

    def __init__(self, survey_content):
        self.survey = json.loads(survey_content)

    def load_survey(self):
        new_survey = Survey(title=self.survey['title'],
                            end_message=self.survey['final_message'],
                            start_date=self.survey['start_date'],
                            end_date=self.survey['end_date'])
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
