from datetime import date
from django.db import models
from django.core.exceptions import ValidationError

from textin.strings import SurveyStrings

class Survey(models.Model):
    title = models.CharField(max_length=255)
    start_message = models.CharField(max_length=500, blank=True, null=True)
    end_message = models.CharField(max_length=500, blank=True, null=True,
                                   default="That was the last question. Thank you for taking this survey!")
    start_date = models.DateField(default=date.today)
    end_date = models.DateField()
    followup = models.ForeignKey('self', on_delete=models.PROTECT, blank=True, null=True, default=None)
    complete_responder = models.BooleanField(default=False)
    pushable = models.BooleanField(default=False)
    pushed = models.BooleanField(default=False)
    hidden = models.BooleanField(default=False)

    @property
    def responses(self):
        return QuestionResponse.objects.filter(question__survey__id=self.id)

    @property
    def responder_count(self):
        return Responder.objects.filter(surveys__in=[Survey.objects.get(id=self.id)]).count()

    @property
    def first_question(self):
        return Question.objects.filter(survey__id=self.id).order_by('id').first()

    @property
    def first_message(self):
        return self.start_message if self.start_message else SurveyStrings.welcome(self.title)

    def __str__(self):
        return '<Survey: %s>' % self.title


class Question(models.Model):
    TEXT = 'text'
    YES_NO = 'yes-no'
    NUMERIC = 'numeric'

    QUESTION_KIND_CHOICES = (
        (TEXT, 'Text'),
        (YES_NO, 'Yes or no'),
        (NUMERIC, 'Numeric')
    )

    body = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=QUESTION_KIND_CHOICES)
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)

    @classmethod
    def validate_kind(cls, kind):
        if kind not in [cls.TEXT, cls.YES_NO, cls.NUMERIC]:
            raise ValidationError("Invalid question kind")

    def next(self):
        survey = Survey.objects.get(id=self.survey_id)
        next_questions = survey.question_set.order_by('id').filter(id__gt=self.id)
        return next_questions[0] if next_questions else None

    def __str__(self):
        return '%s' % self.body


class Responder(models.Model):
    # If this is changed, the data migration 0012_auto_20191007_0432 needs to be updated, and the
    # corresponding surveys/questions in the database need to be updated
    USER_SET_ATTRS = ['name', 'email']

    phone_number = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    surveys = models.ManyToManyField(to=Survey)
    active_survey = models.ForeignKey(Survey, on_delete=models.PROTECT, blank=True, null=True,
                                      related_name='active_survey')

    def complete(self):
        return self.phone_number and self.name and self.email

    def __str__(self):
        return "<Responder #%s  phone: %s>" % (self.id, self.phone_number)


class QuestionResponse(models.Model):
    response = models.CharField(max_length=255)
    message_sid = models.CharField(max_length=255)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    responder = models.ForeignKey(Responder, on_delete=models.CASCADE)

    def __str__(self):
        return '<QuestionResponse: %s>' % self.response

    def as_dict(self):
        return {
            'body': self.question.body,
            'kind': self.question.kind,
            'response': self.response,
            'message_sid': self.message_sid,
        }

    @classmethod
    def valid_response(cls, kind, response):
        if kind == Question.NUMERIC:
            try:
                int(response)
            except ValueError:
                return False
        elif kind == Question.YES_NO:
            first_letter = response[0].lower()
            if first_letter != 'y' and first_letter != 'n':
                return False
        return True
