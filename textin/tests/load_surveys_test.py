from django.core.management import call_command
from django.test import TestCase

from textin.models import Survey, Question


class SurveyLoaderTest(TestCase):
    def test_load_survey(self):
        call_command('load_survey', 'textin/tests/fixtures/survey.json')

        all_surveys = Survey.objects.all()
        all_questions = Question.objects.all()

        assert len(all_surveys) == 1
        assert len(all_questions) == 3
        assert all_surveys.first().title == 'Sunrise Text-in'
