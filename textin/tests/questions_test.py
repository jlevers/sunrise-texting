from django.urls import reverse
from django.test import TestCase

from textin.models import Survey, Question


class ShowQuestionTest(TestCase):

    def setUp(self):
        self.survey = Survey(title='A testing survey')
        self.survey.save()

        self.question = Question(body='A question', kind=Question.TEXT, survey=self.survey)
        self.question.save()

        self.question_ids = {
            'survey_id': self.survey.id,
            'question_id': self.question.id
        }

    def test_uses_proper_verbs_for_sms(self):
        sms_parameters = {'MessageSid': 'SMS123'}

        text_response = self.client.get(reverse('question', kwargs=self.question_ids),
                                        sms_parameters)
        decoded_content = text_response.content.decode('utf8')

        assert self.question.body in decoded_content
        assert '<Message' in decoded_content

    def test_sms_creates_a_web_session(self):
        sms_parameters = {'MessageSid': 'SMS123'}

        self.client.get(reverse('question', kwargs=self.question_ids),
                        sms_parameters)

        assert self.client.session["answering_question_id"] == self.question.id
