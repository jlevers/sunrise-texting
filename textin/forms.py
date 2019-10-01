from django.forms import ModelForm, modelformset_factory

from textin.models import Question, Survey


class QuestionForm(ModelForm):
    class Meta:
        model = Question
        exclude = ['survey']

QuestionFormSet = modelformset_factory(Question, form=QuestionForm, extra=0)


class SurveyForm(ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
