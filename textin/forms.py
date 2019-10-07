from django import forms

from textin.models import Question, Survey


class QuestionForm(forms.ModelForm):
    def is_valid(self):
        rest_is_valid = super().is_valid()
        if self.cleaned_data != {} and \
            (not 'body' in self.cleaned_data or not self.cleaned_data['body']) or \
            (not 'kind' in self.cleaned_data or not self.cleaned_data['kind']):
            return False
        return rest_is_valid and True

    class Meta:
        model = Question
        exclude = ['survey']

QuestionFormSet = forms.modelformset_factory(Question, form=QuestionForm, extra=1)


class DateInput(forms.DateInput):
    input_type = 'date'

class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = '__all__'
        widgets = {
            'start_date': DateInput(),
            'end_date': DateInput()
        }
