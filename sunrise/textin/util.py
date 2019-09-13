import json
from textin.models import Survey, Question

class SurveyLoader():

    def __init__(self, survey_content):
        self.survey = json.loads(survey_content)

    def load_survey(self):
        new_survey = Survey(title=self.survey['title'])
        new_survey.save()

        questions = [Question(body=question['body'],
                              kind=question['kind'],
                              survey=new_survey).save()
                     for question in self.survey['questions']]
